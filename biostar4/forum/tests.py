from django.test import TestCase
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from biostar4.forum.models import User, Profile, Post


class SiteTest(TestCase):

    def setUp(self):
        self.c = Client()
        self.EQ = self.assertEqual
        self.TRUE = self.assertTrue
        self.IN = self.assertContains

    def test_links(self):
        " Test links"

        links = "home signup login logout planet user_list".split()
        for link in links:
            url = reverse(link)
            r = self.c.get(url)
            self.EQ(r.status_code, 200)

    def test_redirects(self):
        links = "me user_edit post_new messages votes my_site".split()
        for link in links:
            url = reverse(link)
            r = self.c.get(url)
            self.EQ(r.status_code, 302)

class UserTest(SiteTest):


    def test_login(self):

        signup = reverse("signup")
        user = User(email="foo@foo.com", password="$%!3456ABC")

        r = self.c.post(signup, {'email': user.email, 'password': "123"})
        # Should fail and stay on the same page.
        self.EQ(r.status_code, 200)
        self.IN(r, "error")

        r = self.c.post(signup, {'email': user.email, 'password': user.password})
        # Should succeed
        self.EQ(r.status_code, 302)

        # Logged in users can access their pages.
        links = "post_new messages votes my_site".split()
        for link in links:
            url = reverse(link)
            r = self.c.get(url)
            self.EQ(r.status_code, 200)


