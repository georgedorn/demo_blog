from django.views.generic import FormView, ListView, DetailView, DeleteView
from .forms import PostForm
from .models import Post

class EditPost(FormView):
    """
    Create/edit view for Post objects.
    """
    
    form_class = PostForm
    
    def form_valid(self, form):
        """
        Associate the post with the user that created/edited it.
        """
        result = super(PostView).form_valid(form)
        self.object.owner = self.request.user
        self.object.save()
        
        return result
    
    def get_success_url(self):
        """
        On success, redirect to the new/edited blog post.
        """
        return self.object.get_absolute_url()

class ListPosts(ListView):
    """
    
    """
    
    model = Post
    

class ViewPost(DetailView):
    """
    View a specific post.
    """
    
    model = Post