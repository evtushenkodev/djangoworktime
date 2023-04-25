from io import BytesIO

import qrcode
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
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


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    firstname = models.TextField(max_length=30)
    lastname = models.TextField(max_length=30)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='users', blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    objects = CustomUserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email


class Event(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    qr_data = models.ImageField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_entry = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    @classmethod
    def create_from_qr(cls, qr_data, user):
        # Разбираем данные из QR-кода
        org_id, is_entry_str = qr_data.split('-')
        is_entry = is_entry_str == 'entry'

        # Получаем объект организации
        organization = Organization.objects.get(id=org_id)

        # Получаем последнее событие пользователя для данной организации
        last_event = user.event_set.filter(organization=organization).order_by('-timestamp').first()

        # Если последнее событие уже отмечено как приход, то текущее событие будет уходом, и наоборот
        is_entry = not last_event.is_entry if last_event and last_event.is_entry == is_entry else is_entry

        # Создаем событие
        event = cls(user=user, is_entry=is_entry, organization=organization.name)
        event.save()
        return event

    def __str__(self):
        entry_exit = "приход" if self.is_entry else "уход"
        return f"{self.user} {entry_exit} в {self.organization}"
