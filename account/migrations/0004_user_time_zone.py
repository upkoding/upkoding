# Generated by Django 3.1.6 on 2021-10-18 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20210908_0214'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='time_zone',
            field=models.CharField(choices=[('Asia/Jakarta', '(WIB) Waktu Indonesia Barat'), ('Asia/Makassar', '(WITA) Waktu Indonesia Tengah'), ('Asia/Jayapura', '(WIT) Waktu Indonesia Timur')], default='Asia/Jakarta', max_length=100),
        ),
    ]