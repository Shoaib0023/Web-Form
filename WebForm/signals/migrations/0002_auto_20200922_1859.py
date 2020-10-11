# Generated by Django 3.0.5 on 2020-09-22 18:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signal',
            name='category_level_name1',
        ),
        migrations.RemoveField(
            model_name='signal',
            name='category_level_name2',
        ),
        migrations.RemoveField(
            model_name='signal',
            name='category_level_name3',
        ),
        migrations.RemoveField(
            model_name='signal',
            name='category_level_name4',
        ),
        migrations.RemoveField(
            model_name='signal',
            name='signal_id',
        ),
        migrations.AddField(
            model_name='signal',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='signal',
            name='file',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='attachments/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='signal',
            name='kenmark',
            field=models.SlugField(default='', editable=False, max_length=6),
        ),
        migrations.AddField(
            model_name='signal',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='signal',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='signal',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
