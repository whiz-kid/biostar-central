from django.test import TestCase
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from biostar4.forum.models import User, Profile, Post


class SiteTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_main_site(self):
        '''
        Tests that the site can be instantiated
        '''
        EQ = self.assertEqual

        # Main page works.
        r = self.c.get('/')
        EQ(r.status_code, 200)

        # This should redirect to login.
        me = reverse("me")
        r = self.c.get(me)
        EQ(r.status_code, 302)

        # Sign up a user.
        signup = reverse("signup")
        r = self.c.get(signup)
        EQ(r.status_code, 200)
