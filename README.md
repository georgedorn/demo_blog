demo_blog
=========

This is a demo blog implemented in Django as a coding challenge.  It's probably not very useful for you if you don't know why it exists.

Installation
============

1. Clone the repo, preferably into a virtualenv.
2. Create a postgres user and database (and grant create rights if you want to run tests.) matching the insecure credentials in settings.py.  Or edit settings.py.
3. pip install -r requirements.txt
3a. if pylibmc fails to install, you need libmemcachd-dev.  Or remove caching from settings.py or change it to something your system already supports. 
4. python manage.py syncdb
4a. Create a superuser, as you'll need one to post blog entries (or to make staff users that can post blog entries).
5. python manage.py runserver, or point mod_wsgi or nginx at wsgi.py.

Notes
=====

* Some AJAX support is implemented in the backend but not in the frontend.  Namely inline editing of posts and adding of comments.
* A fork of django-registration 0.7 was copied into this codebase.  This is because the 0.8 distribution on pypi has failing tests out-of-the-box, but 0.7 is not immediately compatible with django 1.4.  Given more time, I'd create a separate repo for this fork, but including it directly was more expedient.
* Nested comments are implemented by recursively including a template.  This would probably be done better via a template tag or client-side rendering of nested comments.
* Caching was implement in the last commit with a minimum of effort via django-johnny-cache.  It does queryset and template caching, but I didn't notice any significant speed improvemnts, likely due to everything being fast enough already at the level of load I can produce alone.
* I created a project on pivotaltracker.com to track my own progress: https://www.pivotaltracker.com/projects/737573
* There's a demo site running.  Given that it's wide open and a good spam target, contact me for info.
