# Generated manually to keep the abuse-control schema explicit.
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_user_theme_preference")]

    operations = [
        migrations.CreateModel(
            name="RequestLimit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope", models.CharField(max_length=40)),
                ("fingerprint", models.CharField(max_length=64)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("window_started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("scope", "fingerprint"), name="unique_request_limit")]},
        ),
    ]
