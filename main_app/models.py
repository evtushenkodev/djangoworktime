from io import BytesIO

import qrcode
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255)
    qrcode = models.ImageField(upload_to='qr_codes/', blank=True)

    def save(self, *args, **kwargs):
        created = not self.pk  # проверяем, создаём или обновляем объект
        super().save(*args, **kwargs)
        if created:  # генерируем QR-код только при создании объекта
            self.generate_qr_code()

    def generate_qr_code(self):
        # Генерируем данные для QR-кода
        data = f'{self.id}-{self.name}'

        # Создаем QR-код
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        # Сохраняем QR-код в поле qrcode
        buffer = BytesIO()
        img.save(buffer)
        file_name = f'qr_code_{self.id}.png'
        file = InMemoryUploadedFile(buffer, None, file_name, 'image/png', buffer.getbuffer().nbytes, None)
        self.qrcode.save(file_name, file, save=True)

    def __str__(self):
        return self.name


class User(models.Model):
    firstname = models.TextField(max_length=30)
    lastname = models.TextField(max_length=30)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    login = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Event(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_entry = models.BooleanField(default=True)

    @classmethod
    def create_from_qr(cls, qr_data, user):
        # Разбираем данные из QR-кода
        org_id, is_entry_str = qr_data.split('-')
        is_entry = is_entry_str == 'entry'

        # Получаем объект организации
        organization = Organization.objects.get(id=int(org_id))

        # Создаем событие
        event = cls(user=user, organization=organization, is_entry=is_entry)
        event.save()
        return event

    def __str__(self):
        return f'{self.user.firstname} {self.user.lastname} {self.organization.name} {self.timestamp.__str__()}'