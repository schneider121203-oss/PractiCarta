from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("businesses", "0005_business_address_business_greeting_message_and_more")]

    operations = [
        migrations.AddField(
            model_name="business",
            name="menu_theme",
            field=models.CharField(
                choices=[
                    ("system", "Según el dispositivo del cliente"),
                    ("light", "Modo claro"),
                    ("dark", "Modo oscuro"),
                ],
                default="system",
                max_length=10,
            ),
        ),
    ]
