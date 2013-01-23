from django.conf.urls import patterns, url

from views import ViewPost, ListPosts, EditPost

urlpatterns = patterns('',
    url(r'^$', ListPosts.as_view(), name='post-list'),
    url(r'^(?P<slug>[-_\w]+)/$', ViewPost.as_view(), name='post-detail'),
    url(r'^(?P<slug>[-_\w]+)/edit/$', EditPost.as_view(), name='post-edit'),
    url(r'^(?P<slug>[-_\w]+)/create/$', EditPost.as_view(), name='post-edit'),
    url(r'^(?P<slug>[-_\w]+)/delete/$', EditPost.as_view(), name='post-edit'),
)
