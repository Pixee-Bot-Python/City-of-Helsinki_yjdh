# Generated by Django 3.2.18 on 2023-11-20 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ad_username',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
