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
        ('sites', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')], default=3)),
                ('type', models.IntegerField(choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')], default=5)),
                ('tag_val', models.CharField(max_length=200, default='')),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(null=True, max_length=256)),
                ('rank', models.FloatField(blank=True, default=0)),
                ('vote_count', models.IntegerField(blank=True, default=0, db_index=True)),
                ('view_count', models.IntegerField(blank=True, default=0)),
                ('reply_count', models.IntegerField(blank=True, default=0)),
                ('comment_count', models.IntegerField(blank=True, default=0)),
                ('book_count', models.IntegerField(default=0)),
                ('changed', models.BooleanField(default=True)),
                ('subs_count', models.IntegerField(default=0)),
                ('thread_score', models.IntegerField(blank=True, default=0, db_index=True)),
                ('creation_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('lastedit_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('last_activity', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('sticky', models.BooleanField(default=False, db_index=True)),
                ('has_accepted', models.BooleanField(default=False)),
                ('text', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('blurb', models.TextField(default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('lastedit_user', models.ForeignKey(related_name='editor', to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(to='forum.Post', blank=True, related_name='children', null=True)),
                ('root', models.ForeignKey(to='forum.Post', blank=True, related_name='descendants', null=True)),
                ('site', models.ForeignKey(to='sites.Site', null=True)),
                ('tags', taggit.managers.TaggableManager(verbose_name='Tags', through='taggit.TaggedItem', to='taggit.Tag', help_text='A comma-separated list of tags.')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
                ('tags', taggit.managers.TaggableManager(verbose_name='Tags', through='taggit.TaggedItem', to='taggit.Tag', help_text='A comma-separated list of tags.')),
            ],
        ),
        migrations.CreateModel(
            name='UserUpload',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
