# Generated by Django 5.0.1 on 2024-02-10 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='sen_locc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(max_length=10)),
                ('lon', models.FloatField(max_length=100)),
            ],
        ),
    ]