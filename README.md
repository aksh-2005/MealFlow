# 🍽️ MealFlow

A full-stack **meal subscription management platform** built with Django. Users can register, choose meal plans (Veg/Non-Veg), subscribe via Stripe payments, manage their profiles, and view weekly menus. Includes an admin dashboard powered by Django Unfold.

**Live Demo:** [https://mealflow-web.vercel.app/](https://mealflow-web.vercel.app/)

---

## ✨ Features

- **User Registration & Authentication** — Sign up, log in, log out with session management
- **Meal Plan Subscriptions** — Daily Trial, 7-Day Value, and 30-Day Premium plans
- **Stripe Payment Integration** — Secure checkout sessions with payment verification
- **Weekly Menu Display** — Dynamic Veg/Non-Veg menus managed from the admin panel
- **User Dashboard** — View subscription status, today's meals, weekly schedule
- **Profile Management** — Edit address, change password, switch meal preferences
- **Issue Reporting & Reviews** — Submit meal reviews (1-5 stars) and report issues
- **Contact & Enquiry System** — Public contact form saved to admin
- **Admin Dashboard** — Django Unfold–powered admin with analytics, charts, and sidebar navigation

---

## 🛠️ Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Django 6.0                        |
| Database    | PostgreSQL (Supabase)             |
| Payments    | Stripe Checkout                   |
| Admin UI    | Django Unfold                     |
| Static Files| WhiteNoise                        |
| Deployment  | Vercel (Serverless Python)        |

---

## 📦 Setup (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/aksh-2005/MealFlow.git
cd MealFlow
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@host:port/dbname
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 8. Start the development server

```bash
python manage.py runserver
```

Visit **http://localhost:8000** in your browser.

---

## 🌐 Environment Variables

| Variable                 | Description                           | Required |
|--------------------------|---------------------------------------|----------|
| `SECRET_KEY`             | Django secret key                     | ✅       |
| `DEBUG`                  | Enable debug mode (`True`/`False`)    | ✅       |
| `DATABASE_URL`           | PostgreSQL connection string          | ✅       |
| `STRIPE_SECRET_KEY`      | Stripe secret API key                 | ✅       |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable API key            | ✅       |
| `ALLOWED_HOSTS`          | Comma-separated list of allowed hosts | ✅       |
| `CSRF_TRUSTED_ORIGINS`   | Comma-separated trusted origins       | ✅       |

---

## 🚀 Deploy to Vercel

1. **Install Vercel CLI** (or connect your GitHub repository to Vercel):
   * If using GitHub, import the repository on the [Vercel Dashboard](https://vercel.com/dashboard).
2. Configure **Environment Variables** in the Vercel project settings:
   * `SECRET_KEY` (Generate a secure Django key)
   * `DEBUG` (`False`)
   * `DATABASE_URL` (Your Supabase connection string)
   * `STRIPE_SECRET_KEY` (Your Stripe test/live secret key)
   * `STRIPE_PUBLISHABLE_KEY` (Your Stripe test/live publishable key)
   * `ALLOWED_HOSTS` (e.g. `mealflow-web.vercel.app` or `*`)
   * `CSRF_TRUSTED_ORIGINS` (e.g. `https://mealflow-web.vercel.app`)
3. Vercel will build and run the Django app using the configuration in `vercel.json` and `build_files.sh`.

---

## 📁 Project Structure

```
├── MealFlow/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── myapp/               # Main application
│   ├── models.py        # User profiles, meals, reviews, enquiries
│   ├── views.py         # All view logic
│   ├── admin.py         # Unfold admin configuration
│   ├── utils.py         # Dashboard callback utilities
│   └── tests.py         # Unit tests
├── templates/           # HTML templates
├── vercel.json          # Vercel deployment configuration
├── build_files.sh       # Vercel dependency/static build script
├── requirements.txt     # Python dependencies
└── manage.py
```

---

## 🧪 Running Tests

```bash
python manage.py test myapp
```

---

## 📄 License

This project is for educational / micro-project purposes.
