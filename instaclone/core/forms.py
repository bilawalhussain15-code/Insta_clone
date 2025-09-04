from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Post, Comment


class CustomUserCreationForm(UserCreationForm):

    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=150, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'password1', 'password2', 'bio', 'gender', 'profile_picture')




    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.bio = self.cleaned_data['bio']
        user.gender = self.cleaned_data['gender']
        
        if self.cleaned_data['profile_picture']:
            user.profile_picture = self.cleaned_data['profile_picture']
        
        if commit:
            user.save()
        return user


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'email', 'bio', 'gender', 'profile_picture']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Add a comment...', 
                'class': 'w-full rounded p-1 text-black'
            })
        }