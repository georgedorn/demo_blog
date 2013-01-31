from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from django.core.urlresolvers import reverse_lazy

from django.contrib import admin

class Post(models.Model):
    """
    A blog post.
    """
    
    title = models.TextField()
    content = models.TextField()
    owner = models.ForeignKey(User)

    #AutoSlugFields are automatically calculated upon save
    #and in the case of a collision append -2, -3, etc.
    slug = AutoSlugField(populate_from = lambda x: x.title,
                         unique=True)
    
    created = models.DateTimeField(auto_now_add = True)
    modified = models.DateTimeField(auto_now = True)
    
    def get_absolute_url(self):
        """
        The authoritative url for viewing a post.
        """
        return reverse_lazy('post-detail', kwargs={'slug':self.slug})
    
    def get_edit_url(self):
        """
        The authoritative url for editing a post.
        """
        return reverse_lazy('post-edit', kwargs={'slug':self.slug})

    def get_delete_url(self):
        """
        The authoritative url for deleting a post.
        """
        return reverse_lazy('post-delete', kwargs={'slug':self.slug})
    
    def get_comments(self):
        """
        Helper method for loading all comments on this post.
        
        Not actually used if comment threading is used, except in some unit tests.
        """
        return Comment.objects.filter(post=self)
    
#This is just to help with development; admin can post this way but staff cannot.        
admin.site.register(Post)
    


#delimiter used to store a comment's thread path.
#see Comment.thread_path
THREAD_PATH_SEPARATOR = ';'

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
    
    # The path to this comment.
    # e.g. 1;5;6;8 means that this comment is a reply to comment 8, which in turn
    # is a comment on 6, then 5, then 1.  
    # A comment that is not a reply (i.e. a top-level comment on a post) will have a path of None (NULL).
    
    # This is actually unused at the moment outside of unit tests, but could be used
    # for pagination or AJAX loading of comment trees.
    thread_path = models.TextField(default=None, null=True) 
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created']
    
    @staticmethod
    def get_top_comments_for_post(post):
        """
        Get comments that are direct replies to the main post,
        and not replies to other comments.
        """
        return Comment.objects.filter(post=post, parent=None)

    @property
    def replies(self):
        """
        Returns all comments that directly reply to this comment.
        """
        return Comment.objects.filter(parent=self)
        
    @property
    def path_list(self):
        """
        Converts the delimited string version of comment's path
        to a list of strings of pks.
        """
        if not self.thread_path:
            return []
        return self.thread_path.split(THREAD_PATH_SEPARATOR)

    @property
    def descendants_count(self):
        """
        Only applicable to top-level comments, this property
        counts all descendants from this comment.
        """
        if self.thread_path != '':
            raise ValueError('descendants_count only valid for top-level comments')
        
        filter_string = "%s%s" % (self.pk, THREAD_PATH_SEPARATOR)
        qs = (Comment.objects.filter(thread_path=str(self.pk)) |
                Comment.objects.filter(thread_path__startswith=filter_string))
        return qs.count()
    
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
            path = self.parent.path_list
            path.append(str(self.parent.pk))
            self.thread_path = THREAD_PATH_SEPARATOR.join(path)
        else:
            self.thread_path = None
        return super(Comment, self).save(*args, **kwargs)
    
    @property
    def depth(self):
        """
        Determines the depth of this comment, with 0 being top-level.
        """
        return len(self.path_list)
    
    def get_reply_url(self):
        """
        Calculates the URL to get/post a reply to this comment.
        """
        return reverse_lazy('reply-create', kwargs={'post_slug':self.post.slug,
                                                    'parent_id':self.pk})
    
#currently the only way to edit or delete a comment
admin.site.register(Comment)

