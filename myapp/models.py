from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    meal_preference = models.CharField(max_length=50)
    plan_name = models.CharField(max_length=50, default="No Active Plan")
    subscription_active = models.BooleanField(default=False)
    subscription_expiry = models.DateField(blank=True, null=True)
    last_amount_paid = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class ChangeInMeal(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Meal Preference'
        verbose_name_plural = 'Meal Preference'


class ChangeInAddress(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Address Details'
        verbose_name_plural = 'Address Details'


class MealReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}★"


class ReportIssue(models.Model):
    ISSUE_CHOICES = [
        ('wrong_meal', 'Wrong Meal Delivered'),
        ('late_delivery', 'Late Delivery'),
        ('quality', 'Food Quality Issue'),
        ('missing_item', 'Missing Item'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.CharField(max_length=50, choices=ISSUE_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.issue}"


class MenuItem(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    MEAL_TYPE_CHOICES = [
        ('Veg', 'Veg'),
        ('Non-Veg', 'Non-Veg'),
    ]
    day = models.CharField(max_length=15, choices=DAY_CHOICES)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES, default='Veg')
    breakfast = models.TextField()
    lunch = models.TextField()
    dinner = models.TextField()

    class Meta:
        unique_together = ('day', 'meal_type')

    def __str__(self):
        return f"{self.day} ({self.meal_type})"


class PaymentInfo(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments Got'


class SubscriberInfo(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'


class ProcessedPayment(models.Model):
    stripe_session_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_id = models.CharField(max_length=50)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.stripe_session_id} - {self.amount}"


class Enquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=150, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Enquiry'
        verbose_name_plural = 'Enquiries'

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name or instance.username,
                'email': instance.email or '',
                'phone': '',
                'address': 'No address provided',
                'pincode': '000000',
                'meal_preference': 'Veg',
            }
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()