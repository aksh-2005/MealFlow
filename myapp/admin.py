from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils import timezone
from .models import *


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = (
        'first_name',
        'user',
        'phone',
        'address',
        'pincode',
        'meal_preference',
        'plan_name',
        'subscription_active',
        'subscription_expiry',
        'last_amount_paid'
    )
    search_fields = ('first_name', 'user__username', 'phone')
    list_filter = ('subscription_active', 'plan_name', 'meal_preference')


@admin.register(ChangeInMeal)
class ChangeInMealAdmin(ModelAdmin):
    list_display = ['user', 'meal_preference']
    search_fields = ('user__username', 'meal_preference')
    list_filter = ('meal_preference',)


@admin.register(ChangeInAddress)
class ChangeInAddressAdmin(ModelAdmin):
    list_display = ['user', 'address', 'pincode']
    search_fields = ('user__username', 'address', 'pincode')
    list_filter = ('pincode',)


@admin.register(MealReview)
class MealReviewAdmin(ModelAdmin):
    list_display = ['user', 'rating', 'comment', 'created_at']
    search_fields = ('user__username', 'comment')
    list_filter = ('rating', 'created_at')


@admin.register(ReportIssue)
class ReportIssueAdmin(ModelAdmin):
    list_display = ['user', 'issue', 'description', 'created_at']
    search_fields = ('user__username', 'description')
    list_filter = ('issue', 'created_at')


@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    list_display = ['day', 'meal_type', 'breakfast', 'lunch', 'dinner']
    list_filter = ('day', 'meal_type')


@admin.register(PaymentInfo)
class PaymentInfoAdmin(ModelAdmin):
    list_display = ['user', 'last_amount_paid', 'plan_name', 'subscription_expiry']
    search_fields = ('user__username', 'plan_name')
    list_filter = ('plan_name',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(last_amount_paid__gt=0)


@admin.register(SubscriberInfo)
class SubscriberInfoAdmin(ModelAdmin):
    list_display = ['user', 'first_name', 'phone', 'plan_name', 'meal_preference', 'subscription_expiry', 'subscription_active']
    search_fields = ('user__username', 'first_name', 'phone', 'plan_name')
    list_filter = ('plan_name', 'subscription_active')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            subscription_active=True,
            subscription_expiry__gte=timezone.localdate()
        )


@admin.register(ProcessedPayment)
class ProcessedPaymentAdmin(ModelAdmin):
    list_display = ['user', 'stripe_session_id', 'plan_id', 'amount', 'created_at']
    search_fields = ('user__username', 'stripe_session_id')
    list_filter = ('plan_id', 'created_at')


@admin.register(Enquiry)
class EnquiryAdmin(ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'created_at']
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    list_filter = ('created_at',)