# Generated by Django 5.1.1 on 2024-11-09 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseEnroll', '0003_remove_courseinfo_class_day_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseinfo',
            name='class_days',
            field=models.CharField(blank=True, choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=100, null=True),
        ),
    ]
