from django.conf.urls import patterns, url

from .views import ViewPost, ListPosts, CreatePost, DeletePost, EditPost
from .views import post_comment

urlpatterns = patterns('',
    url(r'^$', ListPosts.as_view(), name='post-list'),
    url(r'^(?P<slug>[-_\w]+)/$', ViewPost.as_view(), name='post-detail'),
    url(r'^posts/create/$', CreatePost.as_view(), name='post-create'),
    url(r'^(?P<slug>[-_\w]+)/edit/$', EditPost.as_view(), name='post-edit'),
    url(r'^(?P<slug>[-_\w]+)/delete/$', DeletePost.as_view(), name='post-delete'),
    url(r'^(?P<post_slug>[-_\w]+)/comment/$', post_comment, name='comment-create'),

)
