
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError("Users must have an email address")
		if not username:
			raise ValueError("Users must have an username")

		user  = self.model(
				email=self.normalize_email(email),
				username=username,
			)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user  = self.create_user(
				email=self.normalize_email(email),
				password=password,
				username=username,
			)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	username 				= models.CharField(max_length=30, unique=True)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	# first_name 				= models.CharField(max_length=30)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username',]

	objects = MyAccountManager()

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True
	
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)
	

class Server(models.Model):
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	ip = models.GenericIPAddressField(verbose_name="Ip Address")
	port = models.IntegerField(default=0)


	def __str__(self):
		return str(self.account) if self.account else ''

def upload_location(instance, filename):
    file_path = 'account/{profile_id}/{filename}'.format(
        profile_id=str(instance.account), filename=filename
    )
    return file_path

class Profile(models.Model):
	account = models.OneToOneField(Account, on_delete=models.CASCADE)
	follower = models.ForeignKey(Account, related_name="owner", on_delete=models.CASCADE)
	image = models.ImageField(upload_to=upload_location, null=True, blank=True)
	date_of_birth = models.DateField()
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	Bio = models.CharField(max_length=250)


	def __str__(self):
		return str(self.first_name + " " + self.last_name)

