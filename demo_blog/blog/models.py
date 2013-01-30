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
    

comment_path_separator = ';'
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
    
    thread_path = models.TextField(default='', blank=True) #stores the entire path of this comment
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """
        Overriding default save to:
        - denormalize username into this model (standardizing whether comment
          came from a logged-in user or anon
        - calculate this comment's thread path and save it.
        """
        if self.user and not self.user_name:
            self.user_name = self.user.username
            
        #also calculate the thread_path
        #conveniently, it's just the parent's thread_path with
        #the parent's ID appended.
        if self.parent:
            if self.parent.thread_path:
                path = self.parent.thread_path.split(comment_path_separator)
            else:
                path = []

            path.append(str(self.parent.pk))
            
            self.thread_path = comment_path_separator.join(path)
        else:
            self.thread_path = ''
        return super(Comment, self).save(*args, **kwargs)
    
    @property
    def depth(self):
        if self.thread_path == '':
            return 0
        return len(self.thread_path.split(comment_path_separator))
    
    def get_reply_url(self):
        """
        Calculates the URL to get/post a reply to this comment.
        """
        return reverse_lazy('reply-create', kwargs={'post_slug':self.post.slug,
                                                    'parent_id':self.pk})
    
admin.site.register(Comment)

