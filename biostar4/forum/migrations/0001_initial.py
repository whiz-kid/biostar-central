# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import biostar4.forum.models
import taggit.managers
from django.conf import settings
import django.utils.timezone


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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=2, choices=[(1, 'Messages'), (2, 'Email'), (3, 'No Messages')])),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=3, choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')])),
                ('type', models.IntegerField(default=5, choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')])),
                ('tag_val', models.CharField(default='', max_length=200)),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(max_length=256, null=True)),
                ('rank', models.FloatField(default=0, blank=True)),
                ('vote_count', models.IntegerField(default=0, db_index=True, blank=True)),
                ('view_count', models.IntegerField(default=0, blank=True)),
                ('reply_count', models.IntegerField(default=0, blank=True)),
                ('comment_count', models.IntegerField(default=0, blank=True)),
                ('book_count', models.IntegerField(default=0)),
                ('changed', models.BooleanField(default=True)),
                ('subs_count', models.IntegerField(default=0)),
                ('thread_score', models.IntegerField(default=0, db_index=True, blank=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('lastedit_date', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('last_activity', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('sticky', models.BooleanField(default=False, db_index=True)),
                ('has_accepted', models.BooleanField(default=False)),
                ('text', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('blurb', models.TextField(default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-lastedit_date'],
            },
        ),
        migrations.CreateModel(
            name='PostUpload',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(default='File', max_length=500)),
                ('file', models.FileField(upload_to=biostar4.forum.models.file_path)),
                ('post', models.ForeignKey(to='forum.Post')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
            ],
        ),
        migrations.CreateModel(
            name='UserUpload',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(default='File', max_length=500)),
                ('file', models.FileField(upload_to=biostar4.forum.models.file_path)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='files',
            field=models.ManyToManyField(to='forum.UserUpload'),
        ),
        migrations.AddField(
            model_name='profile',
            name='messages',
            field=models.ManyToManyField(to='forum.Message'),
        ),
        migrations.AddField(
            model_name='profile',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', help_text='A comma-separated list of tags.', verbose_name='Tags', through='taggit.TaggedItem'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='files',
            field=models.ManyToManyField(to='forum.PostUpload', related_name='posts'),
        ),
        migrations.AddField(
            model_name='post',
            name='followers',
            field=models.ManyToManyField(to='forum.Follower', related_name='posts'),
        ),
        migrations.AddField(
            model_name='post',
            name='lastedit_user',
            field=models.ForeignKey(related_name='editor', null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(null=True, related_name='children', to='forum.Post', blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='root',
            field=models.ForeignKey(null=True, related_name='descendants', to='forum.Post', blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='site',
            field=models.ForeignKey(to='sites.Site', null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', help_text='A comma-separated list of tags.', verbose_name='Tags', through='taggit.TaggedItem'),
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
