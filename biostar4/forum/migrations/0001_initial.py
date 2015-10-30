# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('status', models.IntegerField(default=3, choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')])),
                ('type', models.IntegerField(default=5, choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')])),
                ('tag_val', models.CharField(default='', max_length=200)),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(null=True, max_length=256)),
                ('rank', models.FloatField(default=0, blank=True)),
                ('vote_count', models.IntegerField(blank=True, db_index=True, default=0)),
                ('view_count', models.IntegerField(default=0, blank=True)),
                ('reply_count', models.IntegerField(default=0, blank=True)),
                ('comment_count', models.IntegerField(default=0, blank=True)),
                ('book_count', models.IntegerField(default=0)),
                ('changed', models.BooleanField(default=True)),
                ('subs_count', models.IntegerField(default=0)),
                ('thread_score', models.IntegerField(blank=True, db_index=True, default=0)),
                ('creation_date', models.DateTimeField(db_index=True)),
                ('lastedit_date', models.DateTimeField(db_index=True)),
                ('last_activity', models.DateTimeField(db_index=True)),
                ('sticky', models.BooleanField(db_index=True, default=False)),
                ('has_accepted', models.BooleanField(default=False)),
                ('text', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('lastedit_user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='editor')),
                ('parent', models.ForeignKey(null=True, to='forum.Post', related_name='children', blank=True)),
                ('root', models.ForeignKey(null=True, to='forum.Post', related_name='descendants', blank=True)),
                ('site', models.ForeignKey(to='sites.Site', null=True)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', to='taggit.Tag', through='taggit.TaggedItem', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('files', models.CharField(default='', max_length=1000)),
                ('text', models.CharField(default='', max_length=3000)),
                ('html', models.CharField(default='', max_length=6000)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', to='taggit.Tag', through='taggit.TaggedItem', verbose_name='Tags')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
