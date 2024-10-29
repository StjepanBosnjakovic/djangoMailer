# Generated by Django 5.1.2 on 2024-10-29 13:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('scheduled_time', models.DateTimeField()),
                ('recipients', models.ManyToManyField(to='campaign.recipient')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaign.emailtemplate')),
            ],
        ),
    ]
