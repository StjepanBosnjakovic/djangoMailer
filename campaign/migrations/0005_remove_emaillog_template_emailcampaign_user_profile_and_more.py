# Generated by Django 5.1.2 on 2024-11-02 16:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0004_userprofile_max_emails_per_hour_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emaillog',
            name='template',
        ),
        migrations.AddField(
            model_name='emailcampaign',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_campaigns', to='campaign.userprofile'),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='campaign.emailcampaign'),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_logs', to='campaign.userprofile'),
        ),
        migrations.AddField(
            model_name='emailsendcandidate',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='campaign.emailcampaign'),
        ),
        migrations.AddField(
            model_name='emailsendcandidate',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_send_candidates', to='campaign.userprofile'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_templates', to='campaign.userprofile'),
        ),
        migrations.AddField(
            model_name='recipient',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to='campaign.userprofile'),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='sent_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='status',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='recipient',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterUniqueTogether(
            name='recipient',
            unique_together={('user_profile', 'email')},
        ),
    ]