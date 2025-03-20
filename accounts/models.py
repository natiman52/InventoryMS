from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField

 
# Define choices for profile status and roles
STATUS_CHOICES = [
    ('INA', 'Inactive'),
    ('A', 'Active'),
    ('OL', 'On leave')
]

ROLE_CHOICES = [
    ('MR','Marketing'),
    ("DR","Designer"),
    ('OP', 'Operative'),
    ('AT', 'Accounting'),
    ('DL', 'Delivery'),
    ("AD","Admin")
]
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not username:
            raise ValueError(_("The Email must be set"))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username, password, **extra_fields)

class OverTime(models.Model):
    date =models.DateField(default=timezone.datetime.today)
    ammount =models.ManyToManyField("store.Item") 
    paid = models.BooleanField(default=False) 
    def __str__(self):
        return f"{self.date}"
class OverTimeConnect(models.Model):
    date =models.DateField(default=timezone.datetime.today)
    myuser = models.ForeignKey('accounts.MyUser',on_delete=models.CASCADE)
    overtime =models.ForeignKey('accounts.OverTime',on_delete=models.CASCADE)

class MyUser(AbstractUser):
    username = models.CharField(max_length=50 ,unique=True) 
    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=12,
        default="MR",
        verbose_name='Role'
    )
    overtime = models.ManyToManyField(OverTime,through=OverTimeConnect)
    last_login = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    
class Supplier(models.Model):
    """
    Represents a vendor with contact and address information.
    """
    user = models.ForeignKey(MyUser,on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=50, verbose_name='Name')
    slug = AutoSlugField(unique=True,populate_from='name',verbose_name='Slug')
    phone_number = models.BigIntegerField(blank=True, null=True, verbose_name='Phone Number')
    address = models.CharField(max_length=50, blank=True, null=True, verbose_name='Address')
    
    def __str__(self):
        """
        Returns a string representation of the vendor.
        """
        return self.name

    class Meta:
        """Meta options for the Vendor model."""
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'


class Customer(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=256)
    address = models.TextField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)

    class Meta:
        db_table = 'Customers'

    def __str__(self) -> str:
        return self.name

    def get_full_name(self):
        return self.name

    def to_select2(self):
        item = {
            "label": self.get_full_name(),
            "value": self.id
        }
        return item
