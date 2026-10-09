from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("businesses", "0006_business_menu_theme"), ("menu_imports", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="DailyImportUsage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day", models.DateField(default=django.utils.timezone.localdate)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("business", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="daily_import_usage", to="businesses.business")),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("business", "day"), name="unique_daily_import_usage")]},
        ),
    ]
