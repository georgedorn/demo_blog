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
        
    
    
admin.site.register(Post)