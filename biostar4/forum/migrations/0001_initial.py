# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import taggit.managers
import biostar4.forum.models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('status', models.IntegerField(default=3, choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')])),
                ('type', models.IntegerField(default=5, choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')])),
                ('tag_val', models.CharField(default='', max_length=200)),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(null=True, max_length=256)),
                ('rank', models.FloatField(default=0, blank=True)),
                ('vote_count', models.IntegerField(default=0, blank=True, db_index=True)),
                ('view_count', models.IntegerField(default=0, blank=True)),
                ('reply_count', models.IntegerField(default=0, blank=True)),
                ('comment_count', models.IntegerField(default=0, blank=True)),
                ('book_count', models.IntegerField(default=0)),
                ('changed', models.BooleanField(default=True)),
                ('subs_count', models.IntegerField(default=0)),
                ('thread_score', models.IntegerField(default=0, blank=True, db_index=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('lastedit_date', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('last_activity', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('sticky', models.BooleanField(default=False, db_index=True)),
                ('has_accepted', models.BooleanField(default=False)),
                ('text', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('blurb', models.TextField(default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('lastedit_user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='editor')),
                ('parent', models.ForeignKey(to='forum.Post', blank=True, null=True, related_name='children')),
                ('root', models.ForeignKey(to='forum.Post', blank=True, null=True, related_name='descendants')),
                ('site', models.ForeignKey(to='sites.Site', null=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='PostUpload',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('file', models.FileField(upload_to=biostar4.forum.models.file_path)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('role', models.IntegerField(default=1, choices=[(1, 'New user'), (2, 'Trusted user'), (3, 'Moderator'), (4, 'Admin')])),
                ('access', models.IntegerField(default=100, choices=[(100, 'Active'), (200, 'Suspended'), (300, 'Banned')])),
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
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='UserUpload',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
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
