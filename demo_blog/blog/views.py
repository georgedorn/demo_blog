from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.views.generic.edit import ModelFormMixin
from .forms import PostForm
from .models import Post


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