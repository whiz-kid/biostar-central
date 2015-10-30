# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import taggit.managers
from django.conf import settings


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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')], default=3)),
                ('type', models.IntegerField(choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')], default=5)),
                ('tag_val', models.CharField(max_length=200, default='')),
                ('title', models.CharField(max_length=250)),
                ('uuid', models.CharField(max_length=256, null=True)),
                ('rank', models.FloatField(blank=True, default=0)),
                ('vote_count', models.IntegerField(blank=True, db_index=True, default=0)),
                ('view_count', models.IntegerField(blank=True, default=0)),
                ('reply_count', models.IntegerField(blank=True, default=0)),
                ('comment_count', models.IntegerField(blank=True, default=0)),
                ('book_count', models.IntegerField(default=0)),
                ('changed', models.BooleanField(default=True)),
                ('subs_count', models.IntegerField(default=0)),
                ('thread_score', models.IntegerField(blank=True, db_index=True, default=0)),
                ('creation_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('lastedit_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('last_activity', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('sticky', models.BooleanField(db_index=True, default=False)),
                ('has_accepted', models.BooleanField(default=False)),
                ('text', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('blurb', models.TextField(default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('lastedit_user', models.ForeignKey(related_name='editor', to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(blank=True, related_name='children', to='forum.Post', null=True)),
                ('root', models.ForeignKey(blank=True, related_name='descendants', to='forum.Post', null=True)),
                ('site', models.ForeignKey(to='sites.Site', null=True)),
                ('tags', taggit.managers.TaggableManager(verbose_name='Tags', to='taggit.Tag', help_text='A comma-separated list of tags.', through='taggit.TaggedItem')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                ('files', models.CharField(max_length=1000, default='')),
                ('text', models.CharField(max_length=3000, default='')),
                ('html', models.CharField(max_length=6000, default='')),
                ('tags', taggit.managers.TaggableManager(verbose_name='Tags', to='taggit.Tag', help_text='A comma-separated list of tags.', through='taggit.TaggedItem')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
