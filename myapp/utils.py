import json
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from .models import UserProfile, ReportIssue, MealReview

def dashboard_callback(request, context):
    
    active_subscribers = UserProfile.objects.filter(subscription_active=True).count()

    total_payments = UserProfile.objects.aggregate(total=Sum('last_amount_paid'))['total'] or 0

    preferences = UserProfile.objects.values('meal_preference').annotate(count=Count('id'))
    pref_labels = []
    pref_data = []
    for p in preferences:
        pref_labels.append(p['meal_preference'] or "Unspecified")
        pref_data.append(p['count'])
    issues = ReportIssue.objects.values('issue').annotate(count=Count('id'))
    issue_labels = []
    issue_data = []
    for i in issues:

        label = dict(ReportIssue.ISSUE_CHOICES).get(i['issue'], i['issue'])
        issue_labels.append(label)
        issue_data.append(i['count'])

    avg_rating = MealReview.objects.aggregate(avg=Sum('rating'))['avg']
    review_count = MealReview.objects.count()
    average_score = round(avg_rating / review_count, 1) if (avg_rating and review_count) else 0.0

    context.update({
        "active_subscribers": active_subscribers,
        "total_payments": total_payments,
        "average_score": average_score,
        "review_count": review_count,
        "pref_labels": json.dumps(pref_labels),
        "pref_data": json.dumps(pref_data),
        "issue_labels": json.dumps(issue_labels),
        "issue_data": json.dumps(issue_data),
    })
    return context
