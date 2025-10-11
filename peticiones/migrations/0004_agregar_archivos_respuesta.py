# Generated migration for adding response files

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peticiones', '0003_alter_peticion_fecha_radicacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='peticion',
            name='archivo_respuesta_firmada',
            field=models.FileField(blank=True, help_text='Respuesta firmada', null=True, upload_to='respuestas_firmadas/'),
        ),
        migrations.AddField(
            model_name='peticion',
            name='archivo_constancia_envio',
            field=models.FileField(blank=True, help_text='Constancia de envío', null=True, upload_to='constancias_envio/'),
        ),
        migrations.AddField(
            model_name='peticion',
            name='fecha_respuesta',
            field=models.DateTimeField(blank=True, help_text='Fecha en que se marcó como respondido', null=True),
        ),
    ]
