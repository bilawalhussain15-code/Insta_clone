from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Post, CustomUser, Comment, Like, Follow, CommentLike
from .forms import CustomUserCreationForm, EditProfileForm, PostForm, CommentForm

from django.http import JsonResponse
from django.views.decorators.http import require_POST

def login_view(request):   #Handle user login authentication.
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'core/login.html')



def register_view(request):   #Handle new user registration.
    form = CustomUserCreationForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')
    
    return render(request, 'core/register.html', {'form': form})




@login_required          #Log out the  login page
def logout_view(request):
    logout(request)
    return redirect('login')




@login_required                        #  home feed with posts  followed user and users
def home_view(request):
    
    following_ids = Follow.objects.filter(
        follower=request.user, 
        is_approved=True                           # Get users that current user is following
    ).values_list("following_id", flat=True)
    
    
    followed_posts = Post.objects.filter(
        user_id__in=list(following_ids) + [request.user.id]    # Get posts from followed users and own posts
    ).order_by('-created_at')
    
    
    if followed_posts.count() < 5:
        random_posts = Post.objects.exclude(                          # Get random posts from users not followed
            user_id__in=list(following_ids) + [request.user.id]
        ).order_by('?')[:10]
        
        all_posts = list(followed_posts) + list(random_posts)
        

        all_posts.sort(key=lambda x: x.created_at, reverse=True)
        posts = all_posts
    else:
        posts = followed_posts
    
    post_ids = [post.id for post in posts]
    user_likes = Like.objects.filter(
        user=request.user, 
        post_id__in=post_ids
    ).values_list('post_id', flat=True)
    
    
    comment_ids = []
    for post in posts:
        comment_ids.extend(post.comment_set.values_list('id', flat=True))
    
    user_comment_likes = CommentLike.objects.filter(
        user=request.user, 
        comment_id__in=comment_ids
    ).values_list('comment_id', flat=True)

    for post in posts:
        post.is_liked = post.id in user_likes                         # Add is_liked property to each post and comment
        
        for comment in post.comment_set.all():
            comment.is_liked = comment.id in user_comment_likes
    
    comment_form = CommentForm()
    
    return render(request, 'core/home.html', {
        'posts': posts, 
        'comment_form': comment_form
    })


@login_required
def profile_view(request, username=None):
    profile_user = get_object_or_404(CustomUser, username=username) if username else request.user

    # Check if user can view this profile
    if not profile_user.can_view_profile(request.user):
        is_pending = Follow.objects.filter(
            follower=request.user, 
            following=profile_user, 
            is_approved=False
        ).exists()
        
        return render(request, 'core/private_profile.html', {
            'profile_user': profile_user,
            'is_pending': is_pending
        })

    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and request.user == profile_user and form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        
        # Validate that either image or video is provided
        if not post.image and not post.video:
            form.add_error(None, "Either image or video is required.")
        else:
            post.save()
            messages.success(request, "Post uploaded successfully.")
            return redirect('user_profile', username=profile_user.username)

    # Get posts that have either image or video
    posts = Post.objects.filter(user=profile_user).exclude(
        Q(image__isnull=True) & Q(video__isnull=True)
    ).order_by('-created_at')
    # CORRECT FOLLOW STATUS CHECK
    is_following = False
    is_pending = False
    
    if request.user != profile_user:
        # Check if approved follow exists
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user,
            is_approved=True
        ).exists()
        
        # Check if pending follow request exists
        is_pending = Follow.objects.filter(
            follower=request.user, 
            following=profile_user,
            is_approved=False
        ).exists()

    return render(request, 'core/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'form': form if request.user == profile_user else None,
        'is_following': is_following,
        'is_pending': is_pending
    })


@login_required
def edit_profile_view(request):
    """Handle user profile editing"""
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('user_profile', username=request.user.username)
    
    return render(request, 'core/edit_profile.html', {'form': form})


@login_required
def toggle_private_account(request):
    """Toggle between private and public account settings"""
    if request.method == 'POST':
        request.user.is_private = not request.user.is_private
        request.user.save()
        status = "private" if request.user.is_private else "public"
        messages.success(request, f"Account is now {status}")
    
    return redirect('profile')


@login_required
def follow_requests(request):
    """Display pending follow requests for private accounts"""
    pending_requests = Follow.objects.filter(
        following=request.user, 
        is_approved=False
    )
    
    return render(request, 'core/follow_requests.html', {
        'pending_requests': pending_requests
    })


@login_required
def approve_follow_request(request, follow_id):
    """Approve a follow request"""
    follow_request = get_object_or_404(
        Follow, 
        id=follow_id, 
        following=request.user
    )
    follow_request.is_approved = True
    follow_request.save()
    
    messages.success(request, f"Approved follow request from {follow_request.follower.username}")
    return redirect('follow_requests')


@login_required
def reject_follow_request(request, follow_id):
    """Reject a follow request"""
    follow_request = get_object_or_404(
        Follow, 
        id=follow_id, 
        following=request.user
    )
    follow_request.delete()
    
    messages.success(request, f"Rejected follow request from {follow_request.follower.username}")
    return redirect('follow_requests')


@login_required
def follow_toggle_view(request, username):                 #Handle follow/unfollow actions with support for private accounts
    target_user = get_object_or_404(CustomUser, username=username)
    
    if request.user != target_user:
        follow_instance = Follow.objects.filter(
            follower=request.user, 
            following=target_user
        ).first()
        
        if follow_instance:                                                        # Already following or requested - unfollow/reject
            follow_instance.delete()
            messages.success(request, f"Unfollowed {target_user.username}")
        else:
            if target_user.is_private:
                Follow.objects.create(
                    follower=request.user, 
                    following=target_user, 
                    is_approved=False
                )
                messages.info(request, f"Follow request sent to {target_user.username}")
            else:
                Follow.objects.create(
                    follower=request.user, 
                    following=target_user, 
                    is_approved=True
                )
                messages.success(request, f"Started following {target_user.username}")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required                                       #Display list of followers for a user
def followers_list_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    
    followers_list = []
    follow_relationships = Follow.objects.filter(
        following=user, 
        is_approved=True
    )
    
    for follow in follow_relationships:
        follower = follow.follower
        follower.is_followed_by_me = Follow.objects.filter(
            follower=request.user, 
            following=follower,                     #current user follows this follower
            is_approved=True
        ).exists()

        follower.is_pending = Follow.objects.filter(
            follower=request.user, 
            following=follower,
            is_approved=False
        ).exists()
        
        followers_list.append(follower)
    
    return render(request, 'core/followers_list.html', {
        'profile_user': user, 
        'followers': followers_list
    })


@login_required                                     #Display list of users that a user is following
def following_list_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    
    following_list = []
    follow_relationships = Follow.objects.filter(
        follower=user, 
        is_approved=True
    )
    
    for follow in follow_relationships:
        following_user = follow.following                   #current user follows this user
        following_user.is_followed_by_me = Follow.objects.filter(
            follower=request.user, 
            following=following_user,
            is_approved=True
        ).exists()
        
        following_user.is_pending = Follow.objects.filter(
            follower=request.user,                          #pending follow request
            following=following_user,
            is_approved=False                        
        ).exists()
        
        following_list.append(following_user)
    
    return render(request, 'core/following_list.html', {
        'profile_user': user, 
        'following': following_list
    })





















@require_POST
@login_required
def like_toggle_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    # Return JSON response for AJAX
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count
    })

@require_POST
@login_required
def comment_like_toggle(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(
        user=request.user, 
        comment=comment
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    # Return JSON response for AJAX
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes_count
    })

# core/views.py - Update add_comment_view function

@require_POST
@login_required
def add_comment_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    text = request.POST.get('text')
    if text:
        comment = Comment.objects.create(user=request.user, post=post, text=text)
        
        # Return JSON response for AJAX with comment details
        return JsonResponse({
            'success': True,
            'comments_count': post.comments_count,
            'comment_id': comment.id,
            'username': request.user.username
        })
    
    return JsonResponse({'success': False})
















@login_required
def search_users(request):                #Search for users
    query = request.GET.get("q", "").strip()
    
    if query:
        users = CustomUser.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(name__icontains=query) 
            
        ).exclude(id=request.user.id).distinct()

        followed_user_ids = request.user.following_set.filter(
            is_approved=True
        ).values_list('following_id', flat=True)
        
        pending_user_ids = request.user.following_set.filter(
            is_approved=False
        ).values_list('following_id', flat=True)
        
        for user in users:
            user.is_followed = user.id in followed_user_ids
            user.is_pending = user.id in pending_user_ids
    else:
        users = CustomUser.objects.none()
    
    return render(request, "core/search_results.html", {
        "users": users, 
        "query": query
    })


@login_required                                        # Shows all posts from the same user
def post_detail_view(request, post_id):
   
    post = get_object_or_404(Post, id=post_id)
    user_posts = Post.objects.filter(user=post.user).order_by('-created_at')
    
    post_ids = [p.id for p in user_posts]
    user_likes = Like.objects.filter(                                # Check which posts are liked by current user
        user=request.user, 
        post_id__in=post_ids
    ).values_list('post_id', flat=True)
    
    comment_ids = []
    for user_post in user_posts:                               # Check which comments are liked by current user
        comment_ids.extend(user_post.comment_set.values_list('id', flat=True))
    
    user_comment_likes = CommentLike.objects.filter(
        user=request.user, 
        comment_id__in=comment_ids
    ).values_list('comment_id', flat=True)
    

    for user_post in user_posts:
        user_post.is_liked = user_post.id in user_likes
        
        for comment in user_post.comment_set.all():                                 # Add is_liked property to each post and comment
            comment.is_liked = comment.id in user_comment_likes
    
    return render(request, 'core/post_detail.html', {
        'post': post,
        'user_posts': user_posts
    })