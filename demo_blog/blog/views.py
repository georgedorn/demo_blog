from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.views.generic.edit import ModelFormMixin
from .forms import PostForm
from .models import Post
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied

class PostMixin(object):
    form_class = PostForm
    model = Post #only needed for Delete
    
    def form_valid(self, form):
        """
        During form validation, assign the post's owner
        to the user in the request.
        """
        form.instance.owner = self.request.user
        return ModelFormMixin.form_valid(self, form)

    def get_success_url(self):
        """
        On success, redirect to the new/edited blog post.
        """
        return self.object.get_absolute_url()

    def get_object(self, qs=None):
        object = SingleObjectMixin.get_object(self, qs)
        
        if object is not None and object.owner != self.request.user:
            raise PermissionDenied
        
        return object
    

class CreatePost(PostMixin, CreateView):
    pass

class EditPost(PostMixin, UpdateView):
    pass

class DeletePost(PostMixin, DeleteView):
    pass


class ListPosts(ListView):
    """
    
    """
    
    model = Post
    

class ViewPost(DetailView):
    """
    View a specific post.
    """
    
    model = Post