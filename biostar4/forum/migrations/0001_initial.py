# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Closed'), (5, 'Deleted')], default=3)),
                ('type', models.IntegerField(choices=[(1, 'Question'), (2, 'Answer'), (3, 'Comment'), (4, 'Tutorial'), (5, 'Forum'), (6, 'Job'), (7, 'Tool'), (8, 'News')], default=5)),
                ('post_num', models.IntegerField(default=0)),
                ('new_messages', models.IntegerField(default=0)),
                ('new_votes', models.IntegerField(default=0)),
                ('new_posts', models.IntegerField(default=0)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, default='User')),
                ('new_messages', models.IntegerField(default=0)),
                ('new_votes', models.IntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
