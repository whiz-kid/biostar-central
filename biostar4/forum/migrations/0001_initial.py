# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import biostar4.forum.models
import django.utils.timezone
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('type', models.IntegerField(default=2, choices=[(1, 'Messages'), (2, 'Email'), (3, 'No Messages')])),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('status', models.IntegerField(default=3, choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')])),
                ('type', models.IntegerField(default=5, choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')])),
                ('tag_val', models.CharField(max_length=200, default='')),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(max_length=256, null=True)),
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
            ],
            options={
                'ordering': ['-lastedit_date'],
            },
        ),
        migrations.CreateModel(
            name='PostUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=500, default='File')),
                ('file', models.FileField(upload_to=biostar4.forum.models.file_path)),
                ('post', models.ForeignKey(to='forum.Post')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('role', models.IntegerField(default=1, choices=[(1, 'New user'), (2, 'Trusted user'), (3, 'Moderator'), (4, 'Admin')])),
                ('access', models.IntegerField(default=100, choices=[(100, 'Active'), (200, 'Suspended'), (300, 'Banned')])),
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
                ('tags', taggit.managers.TaggableManager(through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags', help_text='A comma-separated list of tags.')),
            ],
        ),
        migrations.CreateModel(
            name='UserUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=500, default='File')),
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
            name='files',
            field=models.ManyToManyField(related_name='posts', to='forum.PostUpload'),
        ),
        migrations.AddField(
            model_name='post',
            name='followers',
            field=models.ManyToManyField(related_name='posts', to='forum.Follower'),
        ),
        migrations.AddField(
            model_name='post',
            name='lastedit_user',
            field=models.ForeignKey(related_name='editor', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='forum.Post', null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='root',
            field=models.ForeignKey(related_name='descendants', blank=True, to='forum.Post', null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='site',
            field=models.ForeignKey(null=True, to='sites.Site'),
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=taggit.managers.TaggableManager(through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags', help_text='A comma-separated list of tags.'),
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
