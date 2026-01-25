from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    profile_photo = models.ImageField(
        _('profile photo'),
        upload_to='profile_photos/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField()

    def __str__(self):
        return self.title

    # TASK 1: Define custom permissions for the Book model
    # These permissions will be used to control access to book-related operations
    class Meta:
        permissions = [
            ("can_view", "Can view books"),        # Permission to view books
            ("can_create", "Can create books"),    # Permission to create new books
            ("can_edit", "Can edit books"),        # Permission to edit existing books
            ("can_delete", "Can delete books"),    # Permission to delete books
        ]