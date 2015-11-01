from django.test import TestCase
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from biostar4.forum.models import User, Profile, Post
from faker import Factory

fake = Factory.create()


class TestBase(TestCase):

    def setUp(self):
        self.c = Client()
        self.EQ = self.assertEqual
        self.TRUE = self.assertTrue
        self.IN = self.assertContains


class SiteTest(TestBase):
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

    def test_shortpass(self):
        signup = reverse("signup")
        r = self.c.post(signup, {'email': "foo@foo.com", 'password': "123"})
        # Should fail and stay on the same page.
        self.EQ(r.status_code, 200)
        self.IN(r, "error")


class UserTest(TestBase):
    def setUp(self):
        super(UserTest, self).setUp()
        self.user = User(
            email=fake.email(),
            password=fake.password(),
        )
        signup = reverse("signup")
        self.c.post(signup, {'email': self.user.email, 'password': self.user.password})

    def test_login(self):
        "Logged in users can access their pages."
        links = "post_new messages votes my_site".split()
        for link in links:
            url = reverse(link)
            r = self.c.get(url)
            self.EQ(r.status_code, 200)

    def test_edit_user(self):
        "Test user editing"
        user_edit = reverse("user_edit")
        name, email, username = fake.name(), fake.email(), fake.word()
        scholar, twitter = fake.word(), fake.word()

        r = self.c.post(user_edit, {
            'name': name,
            'username': username,
            'email': email,
            'scholar': scholar,
            'twitter': twitter,
        })
        self.EQ(r.status_code, 302)
        self.TRUE(User.objects.filter(email=email, username=username, profile__name=name))
        self.TRUE(Profile.objects.filter(scholar=scholar, twitter=twitter))


class PostTest(TestBase):
    def setUp(self):
        super(PostTest, self).setUp()

        # Adds both a user and a post.
        self.user = User(
            email=fake.email(),
            password=fake.password(),
        )
        signup = reverse("signup")
        self.c.post(signup, {'email': self.user.email, 'password': self.user.password})

        self.post_new = reverse("post_new")
        self.post = Post(
            title=fake.sentence(),
            tag_val=" ".join(fake.words()),
            text=fake.paragraph(),
        )

    def test_incomplete_post(self):
        "Incomplete post."
        r = self.c.post(self.post_new, {
            'title': self.post.title,
            'tag_val': self.post.tag_val
        })
        self.EQ(r.status_code, 200)
        self.IN(r, "error")

    def test_full_post(self):
        "Full post"
        r = self.c.post(self.post_new, {
            'title': self.post.title,
            'tag_val': self.post.tag_val,
            'text': self.post.text,
        })
        self.EQ(r.status_code, 200)
        self.IN(r, self.post.title)
