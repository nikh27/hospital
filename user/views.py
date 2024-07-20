from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import *

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
    if request.user.user_type != 'D':
        raise PermissionDenied
    return render(request, 'doctor_dashboard.html', {'user': request.user})

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
