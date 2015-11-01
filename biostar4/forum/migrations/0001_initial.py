# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import taggit.managers
import biostar4.forum.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('type', models.IntegerField(choices=[(1, 'Messages'), (2, 'Email'), (3, 'No Messages')], default=2)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('new', models.BooleanField(default=True)),
                ('content', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')], default=3)),
                ('type', models.IntegerField(choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')], default=5)),
                ('tag_val', models.CharField(max_length=200, default='')),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(max_length=256, null=True)),
                ('rank', models.FloatField(blank=True, default=0)),
                ('vote_count', models.IntegerField(blank=True, default=0, db_index=True)),
                ('view_count', models.IntegerField(blank=True, default=0)),
                ('reply_count', models.IntegerField(blank=True, default=0)),
                ('comment_count', models.IntegerField(blank=True, default=0)),
                ('book_count', models.IntegerField(default=0)),
                ('changed', models.BooleanField(default=True)),
                ('subs_count', models.IntegerField(default=0)),
                ('thread_score', models.IntegerField(blank=True, default=0, db_index=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('lastedit_date', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('last_activity', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('sticky', models.BooleanField(default=False, db_index=True)),
                ('has_accepted', models.BooleanField(default=False)),
                ('text', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('blurb', models.TextField(default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(to='forum.Follower', related_name='posts')),
                ('lastedit_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='editor')),
                ('parent', models.ForeignKey(blank=True, null=True, to='forum.Post', related_name='children')),
                ('root', models.ForeignKey(blank=True, null=True, to='forum.Post', related_name='descendants')),
                ('site', models.ForeignKey(null=True, to='sites.Site')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', verbose_name='Tags', help_text='A comma-separated list of tags.', through='taggit.TaggedItem')),
            ],
        ),
        migrations.CreateModel(
            name='PostUpload',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=250, default='File')),
                ('file', models.FileField(upload_to=biostar4.forum.models.file_path)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('role', models.IntegerField(choices=[(1, 'New user'), (2, 'Trusted user'), (3, 'Moderator'), (4, 'Admin')], default=1)),
                ('access', models.IntegerField(choices=[(100, 'Active'), (200, 'Suspended'), (300, 'Banned')], default=100)),
                ('name', models.CharField(max_length=100, default='User')),
                ('score', models.IntegerField(default=0)),
                ('new_messages', models.IntegerField(default=0)),
                ('new_votes', models.IntegerField(default=0)),
                ('post_num', models.IntegerField(default=0)),
                ('location', models.CharField(max_length=250, default='')),
                ('twitter', models.CharField(max_length=250, default='')),
                ('scholar', models.CharField(max_length=250, default='')),
                ('website', models.CharField(max_length=250, default='')),
                ('my_tags', models.CharField(max_length=500, default='')),
                ('watched_tags', models.CharField(max_length=500, default='')),
                ('text', models.CharField(max_length=3000, default='')),
                ('html', models.CharField(max_length=6000, default='')),
                ('messages', models.ManyToManyField(to='forum.Message')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', verbose_name='Tags', help_text='A comma-separated list of tags.', through='taggit.TaggedItem')),
            ],
        ),
        migrations.CreateModel(
            name='UserUpload',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=250, default='File')),
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
        migrations.AddField(
            model_name='post',
            name='uploads',
            field=models.ManyToManyField(to='forum.UserUpload'),
        ),
        migrations.AddField(
            model_name='follower',
            name='post',
            field=models.ForeignKey(to='forum.Post'),
        ),
        migrations.AddField(
            model_name='follower',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
