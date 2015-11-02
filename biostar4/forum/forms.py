from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from biostar4.forum.ext import captcha
from biostar4.forum.models import User, Post, Profile
from biostar4.forum import html, utils
from django.template.loader import render_to_string
from biostar4.forum.utils import parse_tags
from biostar4.forum.ext.fields import MultiFileField


class PagedownWidget(forms.Textarea):
    TEMPLATE = "widgets/pagedown_widget.html"

    def render(self, name, value, attrs=None):
        value = value or ''
        rows = attrs.get('rows', 15)
        klass = attrs.get('class', '')
        params = dict(value=value, rows=rows, klass=klass)
        return render_to_string(self.TEMPLATE, params)


def get_captcha_field():
    if settings.RECAPTCHA_ENABLED:
        return captcha.html_field(settings.RECAPTCHA_SITE_KEY)
    else:
        return ''


def validate_captcha(request):
    if settings.RECAPTCHA_ENABLED:
        return captcha.validate_captcha(request, settings.RECAPTCHA_SECRET_KEY)
    else:
        return (True, "RECAPTCHA disabled")


def unique_email(email):
    if User.objects.filter(email=email):
        raise ValidationError('The {} email already exists '.format(email))


def check_email(email):
    if not User.objects.filter(email=email):
        raise ValidationError('The {} email does not exists '.format(email))


def check_tags(text):
    tags = parse_tags(text)
    bigs = [tag for tag in tags if len(tag) > 10]
    dups = len(set(tags)) != len(tags)

    if len(tags) > 10:
        raise ValidationError('You have too many tags: {}'.format(len(tags)))
    if dups:
        raise ValidationError('Duplicated tags in input')
    if bigs:
        raise ValidationError('These tags are too long: {} '.format(",".join(bigs)))


class SignupForm(forms.Form):
    email = forms.CharField(label='Email', min_length=5, max_length=100,
                            validators=[unique_email])
    password = forms.CharField(label='Password', min_length=6, max_length=100)


class ResetForm(forms.Form):
    email = forms.CharField(label='Email', validators=[check_email])


class LogoutForm(forms.Form):
    pass


class LoginForm(forms.Form):
    email = forms.CharField(label='Email', validators=[check_email])
    password = forms.CharField(label='Password')

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = User.objects.filter(email=email).first()
            valid = user and user.check_password(password)
            if not valid:
                raise forms.ValidationError(
                    "Unable to validate this email/password combination"
                )


class UserEditForm(forms.Form):
    name = forms.CharField(label='Name',
                           min_length=1, required=True, max_length=100,
                           help_text="The name displayed for you.")

    email = forms.CharField(label='Email', required=True,
                            help_text="Your email on the site")

    username = forms.CharField(label='Username', required=True, max_length=10,
                               help_text="A short identifier: can be used as <code>@username</code>")

    twitter = forms.CharField(label='Twitter',
                              required=False,
                              help_text="Your Twitter handle <code>goldilocks</code>")

    scholar = forms.CharField(label='Scholar',
                              required=False,
                              help_text="Your google scholar id <code>hordfUUAAAAJ</code>")

    website = forms.URLField(label='Website', required=False, initial='',
                             help_text="The address of your website.")

    location = forms.CharField(label='Location', required=False,
                               help_text="Institute/Town/Country/Continent")

    my_tags = forms.CharField(label='My Tags', max_length=500,
                              widget=forms.TextInput(
                                  attrs={'class': 'uk-width-1-1'}),
                              required=False,
                              help_text="Post matching these tags will be listed on 'My Site' (regex ok).")

    watched_tags = forms.CharField(label='Watched Tags', max_length=500,
                                   widget=forms.TextInput(
                                       attrs={'class': 'uk-width-1-1'}),
                                   required=False,
                                   help_text="Posts matching these tags will  generate notifications (regex ok).")

    text = forms.CharField(label="About me",
                           widget=PagedownWidget(),
                           required=False,
                           max_length=3000)

    uploads = MultiFileField(label="Attach files",
                             min_num=0, max_num=Profile.MAX_FILE_NUM, required=False,
                             max_file_size=1024 * 1024 * Profile.MAX_FILE_SIZE,
                             help_text="Files shown on your profile. You may upload {} files, {} Mb per file.".format(
                                 Profile.MAX_FILE_NUM, Profile.MAX_FILE_SIZE))

    remove_ids = forms.MultipleChoiceField(label="Remove uploaded files", required=False,
                                           widget=forms.CheckboxSelectMultiple
                                           )

    def clean_uploads(self):
        files = self.cleaned_data['uploads']
        count = len(self.user.profile.files.all()) + len(files)
        if count > Profile.MAX_FILE_NUM:
            raise ValidationError(
                'Only {} file uploads are allowed per user. You have {}'.format(
                    Profile.MAX_FILE_NUM, count))
        return files

    def clean_email(self):
        text = self.cleaned_data['email']
        if text != self.user.email and User.objects.filter(email=text):
            raise ValidationError('The email {} already exists '.format(text))
        return text

    def clean_my_tags(self):
        text = self.cleaned_data['my_tags']
        tags = parse_tags(text)
        return ",".join(tags)

    def clean_watched_tags(self):
        text = self.cleaned_data['watched_tags']
        tags = parse_tags(text)
        return ",".join(tags)

    def clean_username(self):
        text = self.cleaned_data['username']
        text = text.lower()
        text = text.strip(" @")
        text = "".join(text.split())

        # New username must be unique.
        # There is potential for a race condition here.
        if text != self.user.username and User.objects.filter(username=text):
            raise ValidationError('The username {} already exists '.format(text))

        # Only auto-generated usernames may look like that.
        # Otherwise we can't automatically create default username.
        if text != self.user.username and text.startswith("user"):
            raise ValidationError(
                "New usernames may not start with the word 'user'.")

        return text

    def __init__(self, user, *args, **kwargs):
        # Need to access user during field validation.
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.user = user
        # Populate the file remove fields.
        choices = [(up.id, str(up.name)) for up in user.profile.files.all()]
        if choices:
            self.fields['remove_ids'].choices = choices
        else:
            del self.fields['remove_ids']


class TopLevel(forms.Form):
    POST_TYPES = [
        (Post.QUESTION, "Question"),
        (Post.FORUM, "Forum"),
        (Post.JOB, "Job"),
        (Post.NEWS, "News"),
        (Post.TUTORIAL, "Tutorial"),
        (Post.TOOL, "Tool"),
    ]

    POST_STATUS = [
        (Post.DRAFT, "Draft"),
        (Post.PUBLISHED, "Publish"),
        (Post.DELETED, "Delete"),
    ]

    title = forms.CharField(label='Post title',
                            widget=forms.TextInput(attrs={"class": "uk-width-1-1"}),
                            min_length=10, required=True, max_length=250)

    tag_val = forms.CharField(label='Tags', max_length=500, min_length=1,
                              validators=[check_tags],
                              widget=forms.TextInput(attrs={'class': 'uk-width-1-1'}),
                              help_text="Example: <code>samtools, bwa</code>")

    text = forms.CharField(label="Write your post",
                           initial='',
                           widget=PagedownWidget(),
                           min_length=25,
                           max_length=Post.MAX_CHARS,
                           )

    type = forms.ChoiceField(label="Post type", choices=POST_TYPES,
                             initial=Post.QUESTION)

    status = forms.ChoiceField(label="State",
                               choices=POST_STATUS, initial=Post.PUBLISHED)

    uploads = MultiFileField(label="Attach files",
                             min_num=0, max_num=Post.MAX_FILE_NUM, required=False,
                             max_file_size=1024 * 1024 * Post.MAX_FILE_SIZE,
                             help_text="You may attach up to {} files, {} Mb per file.".format(
                                 Post.MAX_FILE_NUM, Post.MAX_FILE_SIZE))

    remove_ids = forms.MultipleChoiceField(label="Remove uploaded files", required=False,
                                           widget=forms.CheckboxSelectMultiple)

    def __init__(self, user, post, *args, **kwargs):
        # Need to access user during field validation.
        super(TopLevel, self).__init__(*args, **kwargs)
        self.user = user
        self.post = post
        self.toplevel = True

        # Populate the file remove fields.
        if post:
            choices = [(up.id, str(up.name)) for up in post.files.all()]
        else:
            choices = []

        if choices:
            self.fields['remove_ids'].choices = choices
        else:
            del self.fields['remove_ids']

    def clean_uploads(self):
        files = self.cleaned_data['uploads']
        if self.post:
            count = len(self.post.files.all()) + len(files)
            if count > Post.MAX_FILE_NUM:
                raise ValidationError(
                    'Only {} file uploads are allowed per post. You have {}'.format(
                        Post.MAX_FILE_NUM, count))
        return files

    def clean_status(self):
        value = self.cleaned_data['status']
        value = int(value)
        if self.post and (value == Post.DRAFT) and (self.user != self.post.author):
            raise ValidationError('Only post authors may set draft status')
        return value

    def clean_type(self):
        text = self.cleaned_data['type']
        return int(text)

    def clean_tag_val(self):
        text = self.cleaned_data['tag_val']
        tags = parse_tags(text)
        return ",".join(tags)


class Content(forms.Form):
    text = forms.CharField(label="Add your answer",
                           initial='', widget=PagedownWidget(),
                           min_length=25,max_length=Post.MAX_CHARS,
                           )
    parent = forms.IntegerField(widget=forms.HiddenInput)


    uploads = MultiFileField(label="Attach files",
                             min_num=0, max_num=Post.MAX_FILE_NUM, required=False,
                             max_file_size=1024 * 1024 * Post.MAX_FILE_SIZE,
                             help_text="You may attach up to {} files, {} Mb per file.".format(
                                 Post.MAX_FILE_NUM, Post.MAX_FILE_SIZE))

    remove_ids = forms.MultipleChoiceField(label="Remove uploaded files", required=False,
                                           widget=forms.CheckboxSelectMultiple)

    def __init__(self, user, post, *args, **kwargs):
        # Need to access user during field validation.
        super(Content, self).__init__(*args, **kwargs)
        self.toplevel = False
        self.user = user
        self.post = post
