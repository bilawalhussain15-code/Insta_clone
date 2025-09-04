"""
URL configuration for instaclone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""





"""
URL configuration for instaclone project.
Defines all the URL patterns for the application.
"""
from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Core application URLs
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),

    # Follow system URLs
    path('follow/<str:username>/', views.follow_toggle_view, name='follow_toggle'),
    path('followers/<str:username>/', views.followers_list_view, name='followers_list'),
    path('following/<str:username>/', views.following_list_view, name='following_list'),
    path('toggle-private/', views.toggle_private_account, name='toggle_private'),
    path('follow-requests/', views.follow_requests, name='follow_requests'),
    path('approve-request/<int:follow_id>/', views.approve_follow_request, name='approve_follow_request'),
    path('reject-request/<int:follow_id>/', views.reject_follow_request, name='reject_follow_request'),

    # Post interaction URLs
    path('post/<int:post_id>/like/', views.like_toggle_view, name='like_toggle'),
    path('post/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),
    path('comment/<int:comment_id>/like/', views.comment_like_toggle, name='comment_like'),

    # Search and detail URLs
    path("search/", views.search_users, name="search_users"),
    path('post/<int:post_id>/detail/', views.post_detail_view, name='post_detail'),
    
    
    # Follow management URLs
    path('toggle-private/', views.toggle_private_account, name='toggle_private'),
    path('follow-requests/', views.follow_requests, name='follow_requests'),
    path('approve-request/<int:follow_id>/', views.approve_follow_request, name='approve_follow_request'),
    path('reject-request/<int:follow_id>/', views.reject_follow_request, name='reject_follow_request'), 
    

]


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)