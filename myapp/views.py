import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

WEEKLY_MENU = {
    'Veg': {
        'Monday': {
            'breakfast': 'Soft Idli served with flavorful vegetable salna.',
            'lunch': 'White Rice, rich paneer gravy, and potato fry (urulaikilangu poriyal).',
            'dinner': 'Crispy plain Dosa served with tasty vegetable kurma.'
        },
        'Tuesday': {
            'breakfast': 'Steamed Puttu served with spicy veg roast.',
            'lunch': 'White Rice, mor kulambu, and crispy raw banana fry (vazhakkai fry).',
            'dinner': 'Hot Masala Dosa served with flavorful vegetable salna.'
        },
        'Wednesday': {
            'breakfast': 'Toasted cheese bread toast served with green mint Chutney.',
            'lunch': 'White Rice, home-style soya chunks curry, and plantain chips (ethakka upperi).',
            'dinner': 'Soft Appam served with vegetable stew and sweet coconut milk.'
        },
        'Thursday': {
            'breakfast': 'Crispy Medu Vada served with delicious mushroom kurma / paya.',
            'lunch': 'White Rice, pepper Rasam, curd, and paneer bhurji (scrambled paneer).',
            'dinner': 'Onion Uthappam served with flavorful vegetable salna.'
        },
        'Friday': {
            'breakfast': 'Ghee Pongal served with pepper mushroom fry / veg kurma.',
            'lunch': 'White Rice, crispy gobi 65, pepper Rasam, and crunchy papad (appalam).',
            'dinner': 'Crispy masala roast Dosa served with spicy tomato Chutney.'
        },
        'Saturday': {
            'breakfast': 'Soft Idiyappam served with Kerala style vegetable curry.',
            'lunch': 'White Rice, paruppu urundai kuzhambu (lentil ball curry), curd, and crispy raw banana fry.',
            'dinner': 'Soft Wheat Chapati served with paneer butter masala.'
        },
        'Sunday': {
            'breakfast': 'Fluffy Poori served with spicy soya kheema.',
            'lunch': 'Premium Mushroom Biryani served with paneer cubes, onion raita, and sweet payasam.',
            'dinner': 'Flaky Malabar Parotta served with vegetable kurma / salna.'
        }
    },
    'Non-Veg': {
        'Monday': {
            'breakfast': 'Soft Idli served with flavorful chicken salna.',
            'lunch': 'White Rice, spicy egg gravy, and potato fry (urulaikilangu poriyal).',
            'dinner': 'Crispy plain Dosa served with spicy chicken gravy.'
        },
        'Tuesday': {
            'breakfast': 'Steamed Puttu served with spicy egg roast.',
            'lunch': 'White Rice, mor kulambu, and crispy fish fry.',
            'dinner': 'Hot Masala Dosa served with spicy chicken salna.'
        },
        'Wednesday': {
            'breakfast': 'Toasted bread omelette served with green mint Chutney.',
            'lunch': 'White Rice, home-style chicken kulambu, and plantain chips (ethakka upperi).',
            'dinner': 'Soft Appam served with chicken stew and sweet coconut milk.'
        },
        'Thursday': {
            'breakfast': 'Crispy Medu Vada served with mutton paya / chicken gravy.',
            'lunch': 'White Rice, pepper Rasam, curd, and egg podimas (scrambled egg).',
            'dinner': 'Onion Uthappam served with chicken salna.'
        },
        'Friday': {
            'breakfast': 'Ghee Pongal served with chicken liver fry / chicken gravy.',
            'lunch': 'White Rice, chicken dry fry, pepper Rasam, and crunchy papad (appalam).',
            'dinner': 'Crispy egg roast Dosa served with spicy tomato Chutney.'
        },
        'Saturday': {
            'breakfast': 'Soft Idiyappam served with Kerala style egg curry (mutta curry).',
            'lunch': 'White Rice, traditional fish curry, curd, and crispy fish fry.',
            'dinner': 'Soft Wheat Chapati served with chicken butter masala.'
        },
        'Sunday': {
            'breakfast': 'Fluffy Poori served with spicy chicken kheema.',
            'lunch': 'Premium Chicken Biryani served with boiled egg and cool onion raita.',
            'dinner': 'Flaky Malabar Parotta served with chicken salna.'
        }
    }
}


def get_weekly_menu(meal_preference='Veg'):
    if meal_preference not in ['Veg', 'Non-Veg']:
        meal_preference = 'Veg'

    items = MenuItem.objects.filter(meal_type=meal_preference)
    if not items.exists():
        for day, meals in WEEKLY_MENU[meal_preference].items():
            MenuItem.objects.get_or_create(
                day=day,
                meal_type=meal_preference,
                defaults={
                    'breakfast': meals['breakfast'],
                    'lunch': meals['lunch'],
                    'dinner': meals['dinner']
                }
            )
        items = MenuItem.objects.filter(meal_type=meal_preference)

    menu_dict = {}
    for item in items:
        menu_dict[item.day] = {
            'breakfast': item.breakfast,
            'lunch': item.lunch,
            'dinner': item.dinner
        }

    for day, meals in WEEKLY_MENU[meal_preference].items():
        if day not in menu_dict:
            menu_dict[day] = meals

    return menu_dict


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode', '').strip()
        meal_preference = request.POST.get('meal_preference')
        password = request.POST.get('password')

        # Validate pincode format
        if not pincode.isdigit() or len(pincode) != 6:
            return render(
                request,
                'register.html',
                {
                    'error': 'Enter a valid 6-digit pincode.',
                    'full_name': full_name,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'meal_preference': meal_preference,
                }
            )

        # Validate phone format
        clean_phone = phone.strip() if phone else ""
        if not clean_phone.isdigit() or not (10 <= len(clean_phone) <= 15):
            return render(
                request,
                'register.html',
                {
                    'error': 'Enter a valid 10 to 15 digit phone number.',
                    'full_name': full_name,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'meal_preference': meal_preference,
                }
            )

        # Check username
        if User.objects.filter(username=username).exists():
            return render(
                request,
                'register.html',
                {
                    'error': 'Username already exists',
                    'full_name': full_name,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'meal_preference': meal_preference,
                }
            )

        # Check email
        if User.objects.filter(email=email).exists():
            return render(
                request,
                'register.html',
                {
                    'error': 'Email already exists',
                    'full_name': full_name,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'meal_preference': meal_preference,
                }
            )

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        # Create user profile (safe update or create if signal ran)
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'first_name': full_name,
                'email': email,
                'phone': phone,
                'address': address,
                'pincode': pincode,
                'meal_preference': meal_preference
            }
        )

        # Login user
        login(request, user)

        return redirect('dashboard')

    return render(request, 'register.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('register')

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'email': request.user.email or '',
            'phone': '',
            'address': 'No address provided',
            'pincode': '000000',
            'meal_preference': 'Veg',
        }
    )

    # Calculate days left dynamically
    days_left = 0
    today = timezone.localdate()
    if profile.subscription_active and profile.subscription_expiry:
        if profile.subscription_expiry >= today:
            days_left = (profile.subscription_expiry - today).days
        else:
            profile.subscription_active = False
            profile.save()

    # Get current weekday dynamically
    current_day = timezone.localdate().strftime('%A')

    weekly_menu = get_weekly_menu(profile.meal_preference)

    if current_day not in weekly_menu:
        current_day = 'Monday'

    today_meal = weekly_menu[current_day]

    context = {
        'profile': profile,
        'days_left': days_left,
        'current_day': current_day,
        'today_meal': today_meal,
        'weekly_menu': weekly_menu,
    }
    return render(request, 'dashboard.html', context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect(home)


@login_required
def edit_pass(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # keeps user logged in
            messages.success(request, 'Password changed successfully!')
            return redirect('edit_pass')

    return render(request, 'edit_pass.html')


@login_required
def edit_address(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'email': request.user.email or '',
            'phone': '',
            'address': 'No address provided',
            'pincode': '000000',
            'meal_preference': 'Veg',
        }
    )

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        if not address or not pincode:
            messages.error(request, 'Both fields are required.')
        elif not pincode.isdigit() or len(pincode) != 6:
            messages.error(request, 'Enter a valid 6-digit pincode.')
        else:
            profile.address = address
            profile.pincode = pincode
            profile.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('edit_address')

    return render(request, 'edit_address.html', {'profile': profile})


@login_required
def edit_meal_preference(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'email': request.user.email or '',
            'phone': '',
            'address': 'No address provided',
            'pincode': '000000',
            'meal_preference': 'Veg',
        }
    )

    if request.method == 'POST':
        meal_preference = request.POST.get('diet')  # 'diet' matches name="diet" in your form
        profile.meal_preference = meal_preference
        profile.save()
        messages.success(request, 'Meal preference updated successfully!')
        return redirect('dashboard')

    return redirect('dashboard')


@login_required
def review_meal(request):
    if request.method == 'POST':
        rating_raw = request.POST.get('rating')
        comment = request.POST.get('comment')
        try:
            rating = int(rating_raw)
            if 1 <= rating <= 5:
                MealReview.objects.create(
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, 'Thank you for your feedback!')
            else:
                messages.error(request, 'Rating must be between 1 and 5.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating value.')
        return redirect('dashboard')
    return redirect('dashboard')


@login_required
def report_issue(request):
    if request.method == 'POST':
        issue = request.POST.get('issue')
        description = request.POST.get('description', '').strip()

        valid_issues = [choice[0] for choice in ReportIssue.ISSUE_CHOICES]
        if not issue or issue not in valid_issues:
            messages.error(request, 'Please select a valid issue type.')
            return redirect('report_issue')

        if not description:
            messages.error(request, 'Description is required.')
            return redirect('report_issue')

        ReportIssue.objects.create(
            user=request.user,
            issue=issue,
            description=description
        )
        messages.success(request, 'Issue reported successfully! We will get back to you soon.')
        return redirect('report_issue')
    return render(request, 'report.html')


def plans(request):
    return render(request, 'plans.html')


PLAN_DETAILS = {
    'trial': {
        'name': 'Daily Trial Meal Plan',
        'price': 120,
        'days': 1,
    },
    'weekly': {
        'name': '7-Day Value Plan',
        'price': 800,
        'days': 7,
    },
    'monthly': {
        'name': '30-Day Premium Saver',
        'price': 3000,
        'days': 30,
    }
}


@login_required
def create_checkout_session(request, plan_id):
    if plan_id not in PLAN_DETAILS:
        messages.error(request, "Invalid plan selected.")
        return redirect('plans')

    plan = PLAN_DETAILS[plan_id]
    amount_in_paise = plan['price'] * 100

    # If Stripe keys are not configured, fallback to simulated sandbox checkout
    if not settings.STRIPE_SECRET_KEY:
        import time
        mock_session_id = f"mock_checkout_{plan_id}_{request.user.id}_{int(time.time())}"
        messages.info(request, "Stripe API keys not found. Simulated sandbox payment initiated.")
        return redirect(reverse('payment_success') + f'?session_id={mock_session_id}')

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': plan['name'],
                    },
                    'unit_amount': amount_in_paise,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
            metadata={
                'user_id': request.user.id,
                'plan_id': plan_id,
            }
        )
        return redirect(session.url, status=303)
    except Exception as e:
        messages.error(request, f"Error initializing payment with Stripe: {str(e)}")
        return redirect('plans')


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "No Stripe session ID provided.")
        return redirect('plans')

    # Get user profile safely
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'email': request.user.email or '',
            'phone': '',
            'address': 'No address provided',
            'pincode': '000000',
            'meal_preference': 'Veg',
        }
    )

    # Check database to prevent replay attacks across different devices/sessions
    db_payment = ProcessedPayment.objects.filter(stripe_session_id=session_id).first()
    if db_payment:
        plan = PLAN_DETAILS.get(db_payment.plan_id)
        context = {
            'plan_name': plan['name'] if plan else db_payment.plan_id,
            'price': db_payment.amount,
            'days': plan['days'] if plan else 0,
            'expiry': profile.subscription_expiry,
            'session_id': session_id,
        }
        return render(request, 'payment_success.html', context)

    # Check if already processed in request session to avoid duplicate Stripe API calls and saves
    session_key = f"processed_stripe_{session_id}"
    if request.session.get(session_key):
        cached_data = request.session.get(session_key)
        context = {
            'plan_name': cached_data['plan_name'],
            'price': cached_data['price'],
            'days': cached_data['days'],
            'expiry': datetime.datetime.strptime(cached_data['expiry'], '%Y-%m-%d').date(),
            'session_id': session_id,
        }
        return render(request, 'payment_success.html', context)

    # If it is a mock session ID (simulated sandbox checkout)
    if session_id.startswith('mock_checkout_'):
        try:
            parts = session_id.split('_')
            # Format: mock_checkout_<plan_id>_<user_id>_<timestamp>
            if len(parts) >= 5:
                plan_id = parts[2]
                user_id_str = parts[3]
            else:
                messages.error(request, "Invalid mock session ID.")
                return redirect('plans')

            try:
                user_id = int(user_id_str)
            except ValueError:
                messages.error(request, "Invalid user ID in mock session.")
                return redirect('plans')

            if user_id != request.user.id:
                messages.error(request, "Session verification failed.")
                return redirect('plans')

            plan = PLAN_DETAILS.get(plan_id)
            if not plan:
                messages.error(request, "Invalid plan in payment session.")
                return redirect('plans')

            # Update User Profile with subscription stacking
            profile.plan_name = plan['name']
            profile.subscription_active = True
            
            today = timezone.localdate()
            if profile.subscription_expiry and profile.subscription_expiry >= today:
                start_date = profile.subscription_expiry
            else:
                start_date = today
                
            profile.subscription_expiry = start_date + datetime.timedelta(days=plan['days'])
            profile.last_amount_paid = plan['price']
            profile.save()

            # Record payment in DB
            ProcessedPayment.objects.create(
                stripe_session_id=session_id,
                user=request.user,
                plan_id=plan_id,
                amount=plan['price']
            )

            # Cache processed session info
            request.session[session_key] = {
                'plan_name': plan['name'],
                'price': plan['price'],
                'days': plan['days'],
                'expiry': profile.subscription_expiry.strftime('%Y-%m-%d')
            }

            context = {
                'plan_name': plan['name'],
                'price': plan['price'],
                'days': plan['days'],
                'expiry': profile.subscription_expiry,
                'session_id': session_id,
            }
            return render(request, 'payment_success.html', context)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error processing simulated payment: {str(e)}")
            return redirect('plans')

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)

        # Safely extract attributes from the session object using 'in' operator
        # or dict conversion to completely bypass custom class get() errors (like KeyError: 'get')
        payment_status = None
        metadata = {}

        if hasattr(session, 'payment_status'):
            payment_status = getattr(session, 'payment_status', None)
        elif isinstance(session, dict) or hasattr(session, '__getitem__'):
            try:
                payment_status = session['payment_status'] if 'payment_status' in session else None
            except Exception:
                pass

        if hasattr(session, 'metadata'):
            metadata = getattr(session, 'metadata', None) or {}
        elif isinstance(session, dict) or hasattr(session, '__getitem__'):
            try:
                metadata = session['metadata'] if 'metadata' in session else {}
            except Exception:
                pass

        # Verify payment status is paid
        if payment_status != 'paid':
            messages.error(request, "Payment was not completed successfully.")
            return redirect('plans')

        # Safely extract metadata fields using 'in' operator to avoid KeyError: 'get' on StripeObjects
        user_id = None
        plan_id = None
        if isinstance(metadata, dict) or hasattr(metadata, '__getitem__'):
            try:
                user_id = metadata['user_id'] if 'user_id' in metadata else None
                plan_id = metadata['plan_id'] if 'plan_id' in metadata else None
            except Exception:
                pass
        else:
            user_id = getattr(metadata, 'user_id', None)
            plan_id = getattr(metadata, 'plan_id', None)

        if not user_id or not plan_id or int(user_id) != request.user.id:
            messages.error(request, "Session verification failed.")
            return redirect('plans')

        plan = PLAN_DETAILS.get(plan_id)
        if not plan:
            messages.error(request, "Invalid plan in payment session.")
            return redirect('plans')

        # Update User Profile with subscription stacking
        profile.plan_name = plan['name']
        profile.subscription_active = True
        
        today = timezone.localdate()
        if profile.subscription_expiry and profile.subscription_expiry >= today:
            start_date = profile.subscription_expiry
        else:
            start_date = today
            
        profile.subscription_expiry = start_date + datetime.timedelta(days=plan['days'])
        profile.last_amount_paid = plan['price']
        profile.save()

        # Record payment in DB
        ProcessedPayment.objects.create(
            stripe_session_id=session_id,
            user=request.user,
            plan_id=plan_id,
            amount=plan['price']
        )

        # Cache processed session info
        request.session[session_key] = {
            'plan_name': plan['name'],
            'price': plan['price'],
            'days': plan['days'],
            'expiry': profile.subscription_expiry.strftime('%Y-%m-%d')
        }

        context = {
            'plan_name': plan['name'],
            'price': plan['price'],
            'days': plan['days'],
            'expiry': profile.subscription_expiry,
            'session_id': session_id,
        }
        return render(request, 'payment_success.html', context)

    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"Error processing payment success: {str(e)}")
        return redirect('plans')

@login_required
def payment_cancel(request):
    return render(request, 'payment_cancel.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not message:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'contact.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'subject': subject,
                'message': message,
            })
        else:
            Enquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, 'Thank you! Your message has been received. We will get back to you shortly.')
            return redirect('contact_us')

    return render(request, 'contact.html')


def faq(request):
    return render(request, 'faq.html')


def privacy_policy(request):
    return render(request, 'privacy.html')


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)


def custom_403(request, exception=None):
    return render(request, '403.html', status=403)


def custom_400(request, exception=None):
    return render(request, '400.html', status=400)
