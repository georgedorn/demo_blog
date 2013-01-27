from django import forms
from django.contrib.comments import CommentForm
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('owner')
        widgets = {
                   'title': forms.TextInput()
                   
                   }
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('user', 'post', 'parent')
        widgets = {
                    'user_name': forms.TextInput()
            }

    def __init__(self, *args, **kwargs):
        """
        This form works both for logged-in users
        and anonymous users.  It the case of the former,
        the user_name field is hidden and populated
        via the user passed in during init.
        """
        self.post = kwargs.pop('post', None)
        self.user = kwargs.pop('user', None)

        super(CommentForm, self).__init__(*args, **kwargs)
        
        if self.user.is_authenticated():
            # If we're logged in, don't ask for a username.
            del self.fields['user_name']
            
    def save(self, commit=True, *args, **kwargs):
        obj = super(CommentForm, self).save(commit=False, *args, **kwargs)
        obj.post = self.post
        if self.user.is_authenticated():
            obj.user = self.user
        
        if commit:
            obj.save()
        
        return obj
        
        
        
        
