
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):  #Custom User model extending Django's AbstractUser.
    name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True)
    GENDER_CHOICES = (('M', 'Male'),('F', 'Female'),('O', 'Other'),)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    is_private = models.BooleanField(default=False)  

    def __str__(self):
        return self.username

    @property
    def followers_count(self):   #Count  approved followers
        return self.followers_set.filter(is_approved=True).count()

    @property
    def pending_followers_count(self):   #Count  pending follow requests
        return self.followers_set.filter(is_approved=False).count()

    @property
    def following_count(self):     #Count  user is following
        return self.following_set.filter(is_approved=True).count()

    @property
    def posts_count(self):     #Count of posts by this user
        return self.post_set.count()

    def can_view_profile(self, viewer):   #private accounts
        if not self.is_private:
            return True
        if viewer == self:
            return True
        return Follow.objects.filter(follower=viewer, following=self, is_approved=True).exists()





class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Post"
    
    
    def is_video(self):
        return bool(self.video and self.video.name)  # Check if video exists and has a file
    
    def has_media(self):
        return bool(self.image) or bool(self.video)

 

    
    @property
    def likes_count(self):   #Count of likes
        return self.like_set.count()

    @property
    def comments_count(self):    #Count of comments
        return self.comment_set.count()

    def liked_by_user(self, user):        #Check if a user has liked this post
        return self.like_set.filter(user=user).exists()






class Like(models.Model):    #    Like model  user likes on posts.Ensures one like per user per post.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"






class Comment(models.Model):   #Comment model representing user comments on posts
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}"

    @property 
    def likes_count(self):     #Count of likes on this comment
        return self.commentlike_set.count()

    def liked_by_user(self, user):     #Check if a user has liked this comment
        return self.commentlike_set.filter(user=user).exists()






class CommentLike(models.Model):     #    CommentLike model user likes on comments.Ensures one like per user per comment.

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"






class Follow(models.Model):          #Follow model to manage user follow relationships
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following_set",
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers_set",
        on_delete=models.CASCADE
    )
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Temporary allow null

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        status = "approved" if self.is_approved else "pending"
        return f"{self.follower.username} follows {self.following.username} ({status})"
    