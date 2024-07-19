from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient_dashboard/', patient_dashboard, name='patient_dashboard'),
    path('logout/', logout_view, name='logout'),
    path('delete_account/', delete_account_view, name='delete_account'),
    path('blog/', doctor_blog_dashboard, name='doctor_blog_dashboard'),
    path('patient_blog/', patient_blog_dashboard, name='patient_blog_dashboard'),
    path('blog/new/', create_blog_post, name='create_blog_post'),
    path('blog/<int:post_id>/', blog_post_detail, name='blog_post_detail'),
    path('blog/<int:post_id>/edit/', edit_blog_post, name='edit_blog_post'),
    path('blog/<int:post_id>/delete/', delete_blog_post, name='delete_blog_post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)