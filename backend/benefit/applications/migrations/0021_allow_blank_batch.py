# Generated by Django 3.2.4 on 2021-09-25 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0020_employee_consent_attachment_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="batch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="applications",
                to="applications.applicationbatch",
                verbose_name="ahjo batch",
            ),
        ),
    ]
