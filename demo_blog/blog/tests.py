from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post

class TestPostSlugs(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('monkey')
    
    def test_create_post_slug(self):
        post = Post.objects.create(title='My Blog Post', content='Monkeys',
                                   owner=self.user)
        self.assertEqual(post.slug, 'my-blog-post')
        
    def test_create_dupe_slug(self):
        post = Post.objects.create(title='My Blog Post', content='Monkeys',
                                           owner=self.user)
        self.assertEqual(post.slug, 'my-blog-post')

        #with a slightly different title that slugifies to the same as an existing one
        post = Post.objects.create(title='My Blog Post!', content='Monkeys',
                                                   owner=self.user)
        self.assertEqual(post.slug, 'my-blog-post-2')
        
    def test_get_absolute_url(self):
        """
        Test to ensure that the right url for a post involves the slug in some fashion,
        and not the primary key.
        """
        post = Post.objects.create(title='A Test Post', content='Too many monkeys',
                                   owner=self.user)
        
        post_url = post.get_absolute_url()
        self.assertTrue('a-test-post' in post_url)
        self.assertFalse(str(post.pk) in post_url)
        
    def test_get_post(self):
        """
        Actually load a post's page by slug url
        and make sure it works.
        """
        post = Post.objects.create(title='A Sorta Real Post', content='Just enough monkeys this time',
                                   owner=self.user)
        post_url = post.get_absolute_url()
        
        resp = self.client.get(post_url)
        
        self.assertContains(resp, post.content)
        
        
                                


