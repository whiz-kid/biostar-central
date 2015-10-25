from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from forum.ext import captcha
from forum.models import User, Post, parse_tags
from biostar4.forum import html
from django.template.loader import render_to_string


# forms.TextInput(
# attrs={'class': "wmd-input", 'id': 'wmd-input',
# 'placeholder': 'Type your post here'}),


class PagedownWidget(forms.Textarea):
    TEMPLATE = "widgets/pagedown_widget.html"

    def render(self, name, value, attrs=None):
        value = value or ''
        params = dict(value=value)
        return render_to_string(self.TEMPLATE, params)


def update(obj, form):
    "Sets object attributes from form fields"
    if form.is_valid():
        for key, value in form.cleaned_data.items():
            setattr(obj, key, value)
    return obj


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


def unique_username(username):
    if User.objects.filter(username=username):
        raise ValidationError('The {} username already exists '.format(username))


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


def user_file_check(upload):
    if upload and upload.size > (User.MAX_FILE_SIZE * 1024 * 1024):
        this_size = upload.size / 1024 / 1024
        raise forms.ValidationError(
            'File size of {:.0f} MB is larger than maximum allowed {:d} MB ' \
                .format(this_size, User.MAX_FILE_SIZE))


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
                           help_text="The name displayed on for you.")

    email = forms.CharField(label='Email', required=True,
                            help_text="Your email on the site")

    username = forms.CharField(label='Username', required=True, max_length=8,
                               validators=[unique_username],
                               help_text=" Your <code>@username</code> on this site. 8 letter max. Must be unique.")

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

    upload = forms.FileField(label="Attach new file", required=False,
                             validators=[user_file_check],
                             help_text="This file will be shown on your profile. Max size: {} Mb".format(
                                 User.MAX_FILE_SIZE),
                             )

    files = forms.CharField(label="Previously attached files",
                            widget=forms.Textarea(
                                attrs={'rows': '3', 'class': 'uk-width-1-1'}),
                            help_text="Removing a name deletes the file. Max number of files: {}".format(
                                User.MAX_FILE_SIZE),
                            required=False)

    text = forms.CharField(label="About me",
                           widget=PagedownWidget(),
                           required=False,
                           max_length=3000,
                           help_text="Introduce yourself to others (markdown ok)")

    def clean_watched_tags(self):
        text = self.cleaned_data['watched_tags']
        data = parse_tags(text)
        return data

    def clean_my_tags(self):
        text = self.cleaned_data['my_tags']
        data = parse_tags(text)
        return data

    def clean_files(self):
        text = self.cleaned_data['files']
        data = text.split()
        return data

    def clean_username(self):
        text = self.cleaned_data['username']
        text = text.lower()
        text = text.strip(" @")
        text = "".join(text.split())
        return text


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
                            min_length=10, required=True, max_length=250,
                            help_text="Your post title.")

    tags = forms.CharField(label='Tags', max_length=500, min_length=1,
                           validators=[check_tags],
                           widget=forms.TextInput(attrs={'class': 'uk-width-1-1'}),
                           help_text="Post tags, for example: rna-seq Separate multiple tags with commas")

    ptype = forms.ChoiceField(label="Post type", choices=POST_TYPES,
                              initial=Post.PUBLISHED, help_text="Select a post type.",
                              )

    status = forms.ChoiceField(choices=POST_STATUS, initial=Post.PUBLISHED,
                               help_text="Select a post status. Only published posts will be shown to others",
                               )

    text = forms.CharField(label="Post body",
                           initial='',
                           widget=PagedownWidget(),
                           min_length=25,
                           max_length=Post.MAX_CHARS,
                           )

    upload = forms.FileField(label="You may attach a file.", required=False,
                             help_text="This file will be added to the post. Must be smaller than 10Mb",
                             )

    files = forms.CharField(label="Previously attached files",
                            widget=forms.Textarea(
                                attrs={'rows': '2', 'class': 'uk-width-1-1'}),
                            help_text="Deleting the name deletes attached file.",
                            required=False)

    def clean_status(self):
        text = self.cleaned_data['status']
        return int(text)

    def clean_ptype(self):
        text = self.cleaned_data['ptype']
        return int(text)

    def clean_tags(self):
        text = self.cleaned_data['tags']
        data = parse_tags(text)
        return data

    def clean_files(self):
        text = self.cleaned_data['files']
        data = text.split()
        return data
