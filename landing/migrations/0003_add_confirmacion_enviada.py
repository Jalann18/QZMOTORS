from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0002_reserva'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='confirmacion_enviada',
            field=models.BooleanField(default=False),
        ),
    ]
