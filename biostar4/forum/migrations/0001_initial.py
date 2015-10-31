# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
import django.utils.timezone
import biostar4.forum.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')], default=3)),
                ('type', models.IntegerField(choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')], default=5)),
                ('tag_val', models.CharField(default='', max_length=200)),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(null=True, max_length=256)),
                ('rank', models.FloatField(default=0, blank=True)),
                ('vote_count', models.IntegerField(db_index=True, default=0, blank=True)),
                ('view_count', models.IntegerField(default=0, blank=True)),
                ('reply_count', models.IntegerField(default=0, blank=True)),
                ('comment_count', models.IntegerField(default=0, blank=True)),
                ('book_count', models.IntegerField(default=0)),
                ('changed', models.BooleanField(default=True)),
                ('subs_count', models.IntegerField(default=0)),
                ('thread_score', models.IntegerField(db_index=True, default=0, blank=True)),
                ('creation_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('lastedit_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('last_activity', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('sticky', models.BooleanField(db_index=True, default=False)),
                ('has_accepted', models.BooleanField(default=False)),
                ('text', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('blurb', models.TextField(default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('lastedit_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='editor')),
                ('parent', models.ForeignKey(to='forum.Post', blank=True, null=True, related_name='children')),
                ('root', models.ForeignKey(to='forum.Post', blank=True, null=True, related_name='descendants')),
                ('site', models.ForeignKey(to='sites.Site', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', help_text='A comma-separated list of tags.', through='taggit.TaggedItem', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='PostUpload',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('file', models.FileField(upload_to=biostar4.forum.models.file_path)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('role', models.IntegerField(choices=[(1, 'New user'), (2, 'Trusted user'), (3, 'Moderator'), (4, 'Admin')], default=1)),
                ('access', models.IntegerField(choices=[(100, 'Active'), (200, 'Suspended'), (300, 'Banned')], default=100)),
                ('name', models.CharField(default='User', max_length=100)),
                ('score', models.IntegerField(default=0)),
                ('new_messages', models.IntegerField(default=0)),
                ('new_votes', models.IntegerField(default=0)),
                ('post_num', models.IntegerField(default=0)),
                ('location', models.CharField(default='', max_length=250)),
                ('twitter', models.CharField(default='', max_length=250)),
                ('scholar', models.CharField(default='', max_length=250)),
                ('website', models.CharField(default='', max_length=250)),
                ('my_tags', models.CharField(default='', max_length=500)),
                ('watched_tags', models.CharField(default='', max_length=500)),
                ('text', models.CharField(default='', max_length=3000)),
                ('html', models.CharField(default='', max_length=6000)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', help_text='A comma-separated list of tags.', through='taggit.TaggedItem', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='UserUpload',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(default='File', max_length=250)),
                ('file', models.FileField(upload_to=biostar4.forum.models.file_path)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='uploads',
            field=models.ManyToManyField(to='forum.UserUpload'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
