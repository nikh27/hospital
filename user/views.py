from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from .forms import *
from django.conf import settings
from .google_calendar import create_event

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def create_event(summary, location, description, start_datetime, end_datetime, timezone, attendees):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    try:
        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": timezone},
            "end": {"dateTime": end_datetime, "timeZone": timezone},
            "attendees": [{"email": email} for email in attendees]
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event.get('htmlLink')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = status
    appointment.save()

    if status == 'A':
        subject = 'Appointment Accepted'
        message = (
            f"Dear {appointment.patient.get_full_name()},\n\n"
            f"We are pleased to inform you that your appointment with Dr. {appointment.doctor.get_full_name()} "
            f"has been accepted.\n\n"
            f"Appointment Details:\n"
            f"Date: {appointment.date}\n"
            f"Time: {appointment.start_time} - {appointment.end_time} (45 min)\n\n"
            f"If you have any questions or need to reschedule, please contact us.\n\n"
            f"Thank you,\n"
            f"The Healthcare Team"
        )
        recipient_list = [appointment.patient.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

        event_link = create_event(
            summary=f"Appointment with Dr. {appointment.doctor.get_full_name()}",
            location="Healthcare Center",
            description=f"Appointment with Dr. {appointment.doctor.get_full_name()}",
            start_datetime=f"{appointment.date}T{appointment.start_time}+05:30",
            end_datetime=f"{appointment.date}T{appointment.end_time}+05:30",
            timezone='Asia/Kolkata',
            attendees=[appointment.patient.email]
        )
        
        if event_link:
            messages.success(request, 'Appointment accepted, email sent to the patient, and event created on Google Calendar.')
        else:
            messages.success(request, 'Appointment accepted and email sent to the patient, but failed to create event on Google Calendar.')
    elif status == 'R':
        messages.success(request, 'Appointment rejected.')

    return redirect('doctor_appointments')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'D':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def doctor_dashboard(request):
    user = request.user
    if user.user_type == 'D':
        appointments = Appointment.objects.filter(doctor=user, viewed=False)
        appointments_count = appointments.count()
    else:
        appointments_count = 0

    context = {
        'user': user,
        'user_type': user.user_type,
        'appointments_count': appointments_count,
    }
    return render(request, 'doctor_dashboard.html', context)

@login_required
def doctor_appointments(request):
    user = request.user
    appointments = Appointment.objects.filter(doctor=user).order_by('-created_at').distinct()
    appointments.update(viewed=True)
    context = {
        'appointments': appointments,
    }
    return render(request, 'doctor_appointments.html', context)

@login_required
def patient_dashboard(request):
    if request.user.user_type != 'P':
        raise PermissionDenied
    return render(request, 'patient_dashboard.html', {'user': request.user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('login')
    return redirect('doctor_dashboard')

@login_required
def doctor_blog_dashboard(request):
    if request.user.user_type != 'D':
        raise PermissionDenied
    user = request.user
    published_posts = BlogPost.objects.filter(author=user, is_draft=False).order_by('-updated_at').distinct()
    draft_posts = BlogPost.objects.filter(author=user, is_draft=True).order_by('-updated_at').distinct()
    all_posts = BlogPost.objects.filter(author=user).order_by('-updated_at').distinct()
    
    context = {
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'all_posts': all_posts,
    }
    return render(request, 'doctor_blog_dashboard.html', context)

def patient_blog_dashboard(request):
    query = request.GET.get('query', '')
    category = request.GET.get('category', 'All')

    filters = Q(author__user_type='D', is_draft=False) 
    if query:
        filters &= Q(title__icontains=query) | Q(summary__icontains=query)
    if category != 'All':
        filters &= Q(category=category)

    blog_posts = BlogPost.objects.filter(filters).order_by('-updated_at').distinct()

    categories = BlogPost.CATEGORY_CHOICES

    context = {
        'blog_posts': blog_posts,
        'categories': [('All', 'All Categories')] + list(categories),
        'selected_category': category
    }

    return render(request, 'patient_blog_dashboard.html', context)

@login_required
def create_blog_post(request):
    if request.user.user_type != 'D':
        raise PermissionDenied
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.is_draft = 'is_draft' in request.POST and request.POST['is_draft'] == 'True'
            blog_post.save()
            return redirect('doctor_blog_dashboard')
    else:
        form = BlogPostForm()
    return render(request, 'create_blog_post.html', {'form': form})

@login_required
def blog_post_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'blog_post_detail.html', {'post': post})
    
@login_required
def edit_blog_post(request, post_id):
    if request.user.user_type != 'D':
        raise PermissionDenied

    post = get_object_or_404(BlogPost, id=post_id, author=request.user)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if 'publish' in request.POST:
            form.instance.is_draft = False
            if form.is_valid():
                form.save()
                messages.success(request, "Blog post published successfully!")
                return redirect('doctor_blog_dashboard')
        elif 'save_draft' in request.POST:
            form.instance.is_draft = True
            if form.is_valid():
                form.save()
                messages.success(request, "Blog post saved as draft!")
                return redirect('doctor_blog_dashboard')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'edit_blog_post.html', {'form': form, 'post': post})

@login_required
def delete_blog_post(request, post_id):
    if request.user.user_type != 'D':
        raise PermissionDenied
    post = get_object_or_404(BlogPost, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Blog post deleted successfully!")
        return redirect('doctor_blog_dashboard')
    
    return render(request, 'doctor_dashboard.html', {'user': request.user})

@login_required
def doctor_blog_posts(request):
    user = request.user
    posts = BlogPost.objects.filter(author=user, is_draft=False).order_by('-updated_at').distinct()
    draft_posts = BlogPost.objects.filter(author=user, is_draft=True).order_by('-updated_at').distinct()
    all_posts = BlogPost.objects.filter(author=user).order_by('-updated_at').distinct()
    
    context = {
        'published_posts': posts,
        'draft_posts': draft_posts,
        'all_posts': all_posts,
    }
    return render(request, 'doctor_blog_posts.html', context)
