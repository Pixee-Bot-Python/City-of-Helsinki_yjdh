# Generated by Django 3.2.18 on 2023-03-29 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0028_localized_iban_field'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalapplication',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical application', 'verbose_name_plural': 'historical applications'},
        ),
        migrations.AlterModelOptions(
            name='historicalapplicationbasis',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical application basis', 'verbose_name_plural': 'historical application bases'},
        ),
        migrations.AlterModelOptions(
            name='historicalapplicationlogentry',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical application log entry', 'verbose_name_plural': 'historical application log entries'},
        ),
        migrations.AlterModelOptions(
            name='historicaldeminimisaid',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical de minimis aid', 'verbose_name_plural': 'historical de minimis aids'},
        ),
        migrations.AlterField(
            model_name='historicalapplication',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalapplicationbasis',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalapplicationlogentry',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicaldeminimisaid',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
