from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView, View
from django.views.generic.edit import ModelFormMixin
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .forms import PostForm, CommentForm
from .models import Post, Comment

class PostMixin(ModelFormMixin):
    form_class = PostForm
    model = Post #only needed for Delete
    template_name = 'blog/post_form.html'
    
    def get_template_names(self, *args, **kwargs):
        if self.request.is_ajax():
            return super(PostMixin, self).get_template_names(*args, **kwargs)
        else:
            return ['blog/post_form_page.html']
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        """
        Only logged-in users with is_staff permission
        should be able to interact with these views.

        In the future, staff_member_required should probably
        be replaced with something more helpful; that decorator 
        doesn't actually redirect or 403, it just displays
        a form to login (even if you're already logged in.)
        """
        return super(PostMixin, self).dispatch(*args, **kwargs)


    
    def form_valid(self, form):
        """
        During form validation, assign the post's owner
        to the user in the request.
        """
        form.instance.owner = self.request.user
        return super(PostMixin, self).form_valid(form)

    def get_success_url(self):
        """
        On success, redirect to the new/edited blog post.
        """
        return self.object.get_absolute_url()

    def get_object(self, qs=None):
        object = super(PostMixin, self).get_object(qs)
        
        if object is not None and object.owner != self.request.user:
            raise PermissionDenied
        
        return object
    

class CreatePost(PostMixin, CreateView):
    pass

class EditPost(PostMixin, UpdateView):
    pass

class DeletePost(DeleteView):
    model = Post
    
    def get_success_url(self):
        """
        PostMixin's get_success_url doesn't make sense if the post's been deleted.
        """
        return reverse_lazy('post-list')

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

    def get_context_data(self, *args, **kwargs):
        """
        Add the comment form to the context so that it can be rendered.
        """
        context = super(ViewPost, self).get_context_data(*args, **kwargs)
        context['comments'] = Comment.objects.filter(post=self.object).order_by('created')
        context['comment_form'] = CommentForm(post=self.object,
                                              user=self.request.user)
        return context


@csrf_protect
def post_comment(request, post_slug, parent_id=None):
    """
    Simple view to add a comment to a post.
    
    CBVs not used due to time constraints.
    
    Some parts modeled after django.contrib.comments.
    """

    post = get_object_or_404(Post, slug=post_slug)

    if parent_id is not None:
        parent_comment = Comment.objects.get(pk=parent_id)
    else:
        parent_comment = None

    form = CommentForm(post=post, user=request.user, data=request.POST or None)
    context = RequestContext(request, {})
    
    if request.method == 'POST':
        #process the form
        
        if form.is_valid():
            #don't save yet, we need to add some more data
            #from the request that isn't in the form
            comment = form.save(commit=False)
                        
            #add the comment's parent if there was one
            if parent_comment:
                comment.parent = parent_comment

            #now save
            comment.save()

            #build the URL to redirect to
            anchor = comment.pk
            url = post.get_absolute_url() + '?comment_id=%s#comment_id/%s' % (comment.pk, comment.pk) #revisit if post url changes or GET string added
            return HttpResponseRedirect(url)

    if request.is_ajax():
        template_name = 'blog/comment_form.html'
    else:
        template_name = 'blog/comment_form_page.html'
    #we're here either due to a GET or the form had errors.
    #in either case, display the form
    return render_to_response(template_name,
                                {'form':form,
                                 'post':post,
                                 'parent_comment': parent_comment},
                                  context)


    
    
    
    


