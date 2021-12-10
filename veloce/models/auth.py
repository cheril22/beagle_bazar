from django.db import models
from django.contrib.auth.models import User
from veloce import validators
from veloce.models.listings import Product, Category, SubCategory
from veloce import enums


class VeloceUser(models.Model):
    """
    This model has extra property of users user model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_role = models.SmallIntegerField(
        choices=enums.to_choices(enums.UserRole),
        default=3
    )
    first_name = models.CharField(
        max_length=20,
        validators=[validators.NameValidator],
    )
    last_name = models.CharField(
        max_length=20,
        validators=[validators.NameValidator]
    )
    email_address = models.EmailField(
        max_length=60,
        validators=[validators.EmailValidator],
        unique=True
    )
    gender = models.SmallIntegerField(
        choices=enums.to_choices(enums.Gender)
    )
    birthdate = models.DateField()
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return "%s" % self.pk

    def full_name(self):
        """
        this method return full name of the user
        :return:
        """
        return "%s %s" % (self.first_name, self.last_name)


class RecentlyVisited(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visit_counter = models.PositiveIntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    last_visited = models.DateTimeField()