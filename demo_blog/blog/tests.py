from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy

from .models import Post

class TestPostSlugs(TestCase):
    """
    Basic tests to ensure post slugs are
    created and used correctly.
    """
    
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
        self.assertContains(resp, post.owner.username)
        

class TestCRUDPosts(TestCase):
    """
    Tests that actually exercise pages to create/update/delete blog posts.
    """
    
    def setUp(self):
        self.user = User.objects.create_user('monkey', password='monkey_pass')
        self.client.login(username='monkey', password='monkey_pass')
        self.create_post_url = reverse_lazy('post-create')
        self.delete_post_url = reverse_lazy('post-delete')
        

    def test_create_post(self):
        """
        Post a new blog entry.
        Make sure the browser is redirected to the entry.
        Make sure the post's owner is set to the logged-in user.
        """
        post_params = {'title':'Post The First',
                'content':'This is post #1.'}
        res = self.client.post(self.create_post_url, data=post_params)
        self.assertEqual(res.status_code, 302)
        self.assertTrue('post-the-first' in res.get('Location'))

        post = Post.objects.get(title=post_params['title'])
        self.assertEqual(post.owner, self.user)
        
    def test_update_post_get(self):
        """
        Test the url for getting the form to edit a post.
        Make sure the content is populated in the form.
        """
        post = Post.objects.create(title='RE: monkeys',
                                   content='This is an editable post about monkeys.',
                                   owner=self.user)
        
        edit_post_url = reverse_lazy('post-edit', kwargs={'slug':post.slug})
        res = self.client.get(edit_post_url)
        
        self.assertContains(res, post.title)
        self.assertContains(res, post.content)

    def test_update_post_post(self):
        """
        Actually make edits to a post by submitting the form.
        Make sure they are reflected in the db.
        Also make sure the owner is still set.
        """
        post = Post.objects.create(title='RE: monkeys (part 2)',
                                   content='The continuing monkey saga.',
                                   owner=self.user)
        
        edit_post_url = reverse_lazy('post-edit', kwargs={'slug':post.slug})
        
        new_post_params = {'title':'RE: monkeys (part deux)',
                           'content':'More about monkeys.'}
        res = self.client.post(edit_post_url, new_post_params)
        
        #get the post again by primary key
        new_post = Post.objects.get(pk=post.pk)
        self.assertEqual(new_post.title, new_post_params['title'])
        self.assertEqual(new_post.content, new_post_params['content'])
        
        self.assertEqual(new_post.owner, self.user)
        
    def test_update_unowned_post(self):
        """
        Try to edit a post belonging to a different user.
        """
        other_user = User.objects.create_user('real_author')
        post = Post.objects.create(title='A Post Belonging To Real Author',
                                   content="Can't Edit Me",
                                   owner=other_user)
        
        edit_post_url = reverse_lazy('post-edit', kwargs={'slug':post.slug})
        
        res = self.client.get(edit_post_url)
        self.assertEqual(res.status_code, 403)


    def test_delete_post_button(self):
        """
        Retrieve the edit post page, ensure there's a button to delete the post on it.
        """
        post = Post.objects.create(title='A Doomed Post',
                                   content='',
                                   owner=self.user)
        
        edit_post_url = reverse_lazy('post-edit', kwargs={'slug':post.slug})
        
        res = self.client.get(edit_post_url)

        delete_post_url = reverse_lazy('post-delete', kwargs={'slug':post.slug})
        
        self.assertContains(res, delete_post_url)
        
    def test_delete_confirmation(self):
        """
        GET the delete page for a post.
        """
        post = Post.objects.create(title='A More Doomed Post',
                                   content='',
                                   owner=self.user)
        
        delete_post_url = reverse_lazy('post-delete', kwargs={'slug':post.slug})
        
        res = self.client.get(delete_post_url)
        
        #really only two things confirm here without actually parsing HTML:
        #the post_confirm_delete.html template was used
        #and the object still exists
        
        self.assertTrue('blog/post_confirm_delete.html' in res.template_name)
        
        new_post = Post.objects.get(pk=post.pk) #will raise Post.NotFound if deleted
        
    def test_delete_post(self):
        """
        Actually POST a delete to ensure the post is removed.
        """
        post = Post.objects.create(title='An Even More Doomed Post',
                                   content='',
                                   owner=self.user)
        
        delete_post_url = reverse_lazy('post-delete', kwargs={'slug':post.slug})

        res = self.client.post(delete_post_url)
        
        self.assertEqual(res.status_code, 302)
        
        #no more posts
        post_count = Post.objects.count()
        self.assertEqual(post_count, 0)
        
    def test_delete_post_not_yours(self):
        other_user = User.objects.create_user('real_author')
        post = Post.objects.create(title='A Post Belonging To Real Author',
                                   content="Can't Edit Me",
                                   owner=other_user)
        
        delete_post_url = reverse_lazy('post-delete', kwargs={'slug':post.slug})

        res = self.client.post(delete_post_url)
        
        self.assertEqual(res.status_code, 403)