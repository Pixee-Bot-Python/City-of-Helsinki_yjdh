# Generated by Django 3.2.18 on 2023-06-15 11:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("applications", "0033_add_origin_and_attachment_types"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationbatch",
            name="p2p_checker_name",
            field=models.CharField(
                blank=True, max_length=64, verbose_name="P2P acceptor's title"
            ),
        ),
        migrations.AddField(
            model_name="applicationbatch",
            name="p2p_inspector_email",
            field=models.EmailField(
                blank=True, max_length=254, verbose_name="P2P inspector's email address"
            ),
        ),
        migrations.AddField(
            model_name="applicationbatch",
            name="p2p_inspector_name",
            field=models.CharField(
                blank=True, max_length=128, verbose_name="P2P inspector's name"
            ),
        ),
    ]
