# Generated by Django 4.2 on 2023-04-19 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('qrcode', models.ImageField(blank=True, upload_to='qr_codes/')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.TextField(max_length=30)),
                ('lastname', models.TextField(max_length=30)),
                ('login', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=100)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='main_app.organization')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_entry', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.user')),
            ],
        ),
    ]
