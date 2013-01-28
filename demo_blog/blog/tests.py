from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Post, Comment

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
        """
        Common fixtures for most CRUD tests.
        """
        self.user = User.objects.create_user('monkey', password='monkey_pass')
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='monkey', password='monkey_pass')
        self.create_post_url = reverse('post-create')


    def test_create_post(self):
        """
        Post a new blog entry.
        Make sure the browser is redirected to the entry.
        Make sure the post's owner is set to the logged-in user.
        """
        post_params = {'title':'Post The First',
                'content':'This is post #1.'}
        res = self.client.post(self.create_post_url, data=post_params)

        post = Post.objects.get(title=post_params['title'])
        self.assertEqual(post.owner, self.user)
        
        self.assertRedirects(res, reverse('post-detail', kwargs={'slug':post.slug}))

    def test_create_post_not_staff(self):
        """
        Trying to create a post without having the is_staff bit set should
        result in a 403.
        """
        #create a different user and login
        normal_user = User.objects.create_user('fred', password='fred_pass')
        #redundant, but for clarity:
        normal_user.is_staff = False
        normal_user.save()
        
        self.client.login(username='fred', password='fred_pass')
        
        post_params = {'title':'Normal User Post',
                       'content':'This post should not be'}
        
        res = self.client.post(self.create_post_url, data=post_params)
        
        #check to make sure a blog post wasn't created.
        self.assertRaises(ObjectDoesNotExist,
                          Post.objects.get, title=post_params['title'])
        
    def test_update_post_get(self):
        """
        Test the url for getting the form to edit a post.
        Make sure the content is populated in the form.
        """
        post = Post.objects.create(title='RE: monkeys',
                                   content='This is an editable post about monkeys.',
                                   owner=self.user)
        
        edit_post_url = reverse('post-edit', kwargs={'slug':post.slug})
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
        
        edit_post_url = reverse('post-edit', kwargs={'slug':post.slug})
        
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
        
        edit_post_url = reverse('post-edit', kwargs={'slug':post.slug})
        
        res = self.client.get(edit_post_url)
        self.assertEqual(res.status_code, 403)


    def test_delete_post_button(self):
        """
        Retrieve the edit post page, ensure there's a button to delete the post on it.
        """
        post = Post.objects.create(title='A Doomed Post',
                                   content='',
                                   owner=self.user)
        
        edit_post_url = reverse('post-edit', kwargs={'slug':post.slug})
        
        res = self.client.get(edit_post_url)

        delete_post_url = reverse('post-delete', kwargs={'slug':post.slug})
        
        self.assertContains(res, delete_post_url)
        
    def test_delete_confirmation(self):
        """
        GET the delete page for a post.
        """
        post = Post.objects.create(title='A More Doomed Post',
                                   content='',
                                   owner=self.user)
        
        delete_post_url = reverse('post-delete', kwargs={'slug':post.slug})
        
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
        
        delete_post_url = reverse('post-delete', kwargs={'slug':post.slug})

        res = self.client.post(delete_post_url)
        self.assertRedirects(res, reverse('post-list'))
        
        #no more posts
        post_count = Post.objects.count()
        self.assertEqual(post_count, 0)
        
    def test_delete_post_not_yours(self):
        other_user = User.objects.create_user('real_author')
        post = Post.objects.create(title='A Post Belonging To Real Author',
                                   content="Can't Edit Me",
                                   owner=other_user)
        
        delete_post_url = reverse('post-delete', kwargs={'slug':post.slug})

        res = self.client.post(delete_post_url)
        
        self.assertEqual(res.status_code, 403)
        
        
class TestComments(TestCase):
    """
    Tests of making and viewing comments.
    """

    def login(self):
        """
        Helper method.  Pairs with self.commenter from setUp().
        """
        self.client.login(username='logged_in_commenter',
                          password='logged_in_commenter_pass')
    
    def setUp(self):
        """
        Fixtures shared between tests.
        """
        self.author = User.objects.create(username='post_author')
        self.commenter = User.objects.create_user(username='logged_in_commenter',
                                                  password='logged_in_commenter_pass') #for logged-in commenters
        self.post = Post.objects.create(title='Base Post',
                                        content='Just a dummy post',
                                        owner=self.author)
        self.comment_form_url = reverse('comment-create', kwargs={'post_slug':self.post.slug})
        
    def test_comment_on_post_detail(self):
        """
        Tests whether an anonymous comment appears on a post's detail page.
        """
        comment = Comment.objects.create(post=self.post,
                                         user_name='Anonymous Commenter',
                                         content='Nice post! Please view my website.')
        res = self.client.get(self.post.get_absolute_url())
        
        self.assertContains(res, comment.content)
        self.assertContains(res, comment.user_name)
        
    def test_logged_in_comment_on_post_detail(self):
        """
        Tests whether a comment made by a user appears on a post's detail page.
        """
        comment = Comment.objects.create(post=self.post,
                                         user=self.commenter,
                                         content='Hey Author, long time no see!')
        
        res = self.client.get(self.post.get_absolute_url())

        self.assertContains(res, comment.content)
        self.assertContains(res, self.commenter.username)
        

    def test_get_comment_form_anon(self):
        """
        Tests rendering of the comment form for an anon user.
        user_name field should appear.
        """
        res = self.client.get(self.comment_form_url)
        
        self.assertNotContains(res, 'id_parent') #parent should never be in the form, it's a query string param only.
        self.assertContains(res, 'name="user_name"') #we're anon, so we should be asking for a user name
        self.assertContains(res, self.comment_form_url) #the ACTION should be specified
    
    def test_get_comment_form_logged_in(self):
        """
        Tests rendering of the comment form for a logged-in user.
        user_name field should NOT appear; the comment's user_name is
        calculated from the logged-in user's.
        """
        self.login()
        res = self.client.get(self.comment_form_url)
        self.assertNotContains(res, 'user_name') #user_name field should not appear
        
    def test_get_comment_form_anon_reply(self):
        """
        Tests rendering the comment form when replying to
        another comment (as an anon user).
        
        Mostly ensures the comment_parent_id GET param appears.
        """
        comment = Comment.objects.create(post=self.post,
                                                 user_name='Anonymous Commenter',
                                                 content='Nice post! Please view my website.')
        url = comment.get_reply_url()
        res = self.client.get(url)

        self.assertContains(res, url) #posts to correct url with parent id
        self.assertContains(res, comment.pk)
        self.assertContains(res, 'user_name')


    def test_post_comment_anon(self):
        """
        Tests posting a comment as an anonymous user.
        """
        comment_params = {'user_name':'Anonymous Coward',
                          'content': 'Could not disagree more!'}
        
        res = self.client.post(self.comment_form_url, data=comment_params)
        
        comment = self.post.get_comments()[0]
        self.assertEqual(comment.user_name, comment_params['user_name'])
        self.assertEqual(comment.content, comment_params['content'])
    
    def test_post_comment_logged_in(self):
        """
        Tests posting a comment as a logged-in user.
        """
        self.login()
        
        comment_params = {'content': 'Good on ya.'}
        
        res = self.client.post(self.comment_form_url, data=comment_params)
        
        comment = self.post.get_comments()[0]
        self.assertEqual(comment.user_name, self.commenter.username)
        self.assertEqual(comment.content, comment_params['content'])
        
    def test_post_comment_reply(self):
        """
        Tests posting a reply to another comment.
        """
        comment = Comment.objects.create(user_name='Anonymous',
                                         content='This is a parent comment.  Please reply.',
                                         post=self.post)
        url = comment.get_reply_url()
        
        reply_params = {'user_name':'Anonymous 2',
                        'content':'This is a child comment.'}
        
        res = self.client.post(url, data=reply_params)
        
        reply = Comment.objects.get(user_name='Anonymous 2')
        self.assertEqual(reply.parent, comment)