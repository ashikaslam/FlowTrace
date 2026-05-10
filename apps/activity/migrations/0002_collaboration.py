import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
        ('activity', '0001_initial'),
        ('tasks', '0001_initial'),
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollaborationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_collab_requests', to='accounts.workspacemembership')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_collab_requests', to='accounts.workspacemembership')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collab_requests', to='tasks.task')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collab_requests', to='workspaces.workspace')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='collaborationrequest',
            constraint=models.UniqueConstraint(fields=('requester', 'target', 'task'), name='unique_collab_request'),
        ),
        migrations.AddIndex(
            model_name='collaborationrequest',
            index=models.Index(fields=['target', 'status'], name='activity_cr_target_status_idx'),
        ),
        migrations.AddIndex(
            model_name='collaborationrequest',
            index=models.Index(fields=['task', 'status'], name='activity_cr_task_status_idx'),
        ),
        migrations.CreateModel(
            name='TaskCollaborator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborators', to='tasks.task')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborations', to='accounts.workspacemembership')),
            ],
            options={'ordering': ['joined_at']},
        ),
        migrations.AddConstraint(
            model_name='taskcollaborator',
            constraint=models.UniqueConstraint(fields=('task', 'member'), name='unique_task_collaborator'),
        ),
        migrations.AddIndex(
            model_name='taskcollaborator',
            index=models.Index(fields=['task', 'is_active'], name='activity_tc_task_active_idx'),
        ),
        migrations.CreateModel(
            name='CollaborationActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('request_sent', 'Request Sent'), ('request_accepted', 'Request Accepted'), ('request_rejected', 'Request Rejected'), ('request_cancelled', 'Request Cancelled'), ('collab_started', 'Collaboration Started'), ('collab_ended', 'Collaboration Ended')], max_length=30)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collab_logs', to='tasks.task')),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collab_logs', to='accounts.workspacemembership')),
            ],
            options={'ordering': ['-timestamp']},
        ),
        migrations.AddIndex(
            model_name='collaborationactivitylog',
            index=models.Index(fields=['task', 'timestamp'], name='activity_cal_task_ts_idx'),
        ),
    ]
