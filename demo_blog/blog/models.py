from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from django.core.urlresolvers import reverse_lazy

from django.contrib import admin

class Post(models.Model):
    
    title = models.TextField()
    content = models.TextField()
    owner = models.ForeignKey(User)

    slug = AutoSlugField(populate_from = lambda x: x.title,
                         unique=True)
    
    created = models.DateTimeField(auto_now_add = True)
    modified = models.DateTimeField(auto_now = True)
    
    def get_absolute_url(self):
        return reverse_lazy('post-detail', kwargs={'slug':self.slug})
    
    def get_edit_url(self):
        return reverse_lazy('post-edit', kwargs={'slug':self.slug})

    def get_delete_url(self):
        return reverse_lazy('post-delete', kwargs={'slug':self.slug})
    
    @staticmethod
    def get_by_slug(slug):
        return Post.objects.get(slug=slug)
    
    def get_comments(self):
        return Comment.objects.filter(post=self).order_by('-created') #newest first?
        
admin.site.register(Post)
    
    
class Comment(models.Model):
    """
    Represents a comment on a post.
    
    django.contrib.comment not used as it's too
    generic and difficult to extend to change behaviors.
    """
    
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User, null=True, blank=True) #if a user is logged in, relate this comment to them.
    user_name = models.TextField()
    content = models.TextField()
    
    parent = models.ForeignKey('Comment', null=True, default=None) #for threaded comments, later
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """
        Overriding default save to automatically denormalize 
        the user_name into the comment field.
        
        Technically a premature optimization, but makes the
        comment display form a lot more straightforward, too.
        """
        if self.user and not self.user_name:
            self.user_name = self.user.username
            
        return super(Comment, self).save(*args, **kwargs)
    
    def get_reply_url(self):
        """
        Calculates the URL to get/post a reply to this comment.
        """
        return reverse_lazy('reply-create', kwargs={'post_slug':self.post.slug,
                                                    'parent_id':self.pk})
    
