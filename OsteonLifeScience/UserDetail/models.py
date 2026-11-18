from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('editor', 'Content Editor'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')
    contact_number = models.CharField(max_length=20, null=True, blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Superusers created from the command line are always admins.
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username
