# Generated by Django 2.2.16 on 2022-04-06 03:33

from django.db import migrations
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_post_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='video',
            field=embed_video.fields.EmbedVideoField(blank=True),
        ),
    ]
