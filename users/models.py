from django.db import models

# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
    pass

class CustomUser(AbstractUser):
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    is_user = models.BooleanField(default=False)