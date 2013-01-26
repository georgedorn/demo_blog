from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView, View
from django.views.generic.edit import ModelFormMixin
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


from .forms import PostForm, CommentForm
from .models import Post, Comment

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
    View a list of posts.
    """
    model = Post
    

class ViewPost(DetailView):
    """
    View a specific post.
    """
    model = Post
    


@csrf_protect
def post_comment(request, post_slug):
    """
    Simple view to add a comment to a post.
    
    CBVs not used due to time constraints.
    
    Some parts modeled after django.contrib.comments.
    """

    post = get_object_or_404(Post, slug=post_slug)
    parent_id = request.GET.get('comment_parent', None)

    if parent_id is not None:
        parent_comment = Comment.objects.get(pk=parent_id)
    else:
        parent_comment = None

    form = CommentForm(post=post, data=request.POST or None)
    context = RequestContext(request, {})
    
    if request.method == 'POST':
        #process the form
        
        if form.is_valid():
            #don't save yet, we need to add some more data
            #from the request that isn't in the form
            comment = form.save(commit=False)
            
            #add the user if logged in
            if request.user.is_authenticated():
                comment.user = request.user
            
            #add the comment's parent if there was one
            if parent_comment:
                comment.parent = parent_comment

            #now save
            comment.save()

            #build the URL to redirect to
            anchor = comment.pk
            url = post.get_absolute_url() + '?comment_id=%s#comment_id' #revisit if post url changes or GET string added
            return HttpResponseRedirect(url)
    
    #we're here either due to a GET or the form had errors.
    #in either case, display the form
    return render_to_response('blog/comment_form.html',
                                {'form':form,
                                 'post':post,
                                 'parent_comment': parent_comment},
                                  context)


    
    
    
    


