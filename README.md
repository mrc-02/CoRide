# CoRide - Carpooling Platform Backend

<div align="center">
  
  <!-- Logo Placeholder -->
  <img src="https://via.placeholder.com/200x200/4CAF50/FFFFFF?text=CoRide" alt="CoRide Logo" width="200"/>
  
  ### Production-Ready Carpooling Platform for India
  
  *Connecting commuters, reducing traffic, saving the environment*
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
  [![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
  [![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)](https://www.django-rest-framework.org/)
  [![License](https://img.shields.io/badge/License-Proprietary-yellow.svg)](LICENSE)
  [![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/coride/backend)
  
</div>

---

## 📖 About CoRide

**CoRide** is a production-ready carpooling platform designed specifically for the Indian market, targeting office commuters and daily travelers. The platform connects drivers with empty seats to passengers traveling in the same direction, reducing traffic congestion, lowering commute costs, and contributing to environmental sustainability.

### 🎯 Key Features

- **🚗 Ride Sharing**: Drivers can offer rides with available seats
- **🔍 Smart Search**: Find rides based on origin, destination, and time
- **💳 Secure Payments**: Integrated Razorpay payment gateway for India
- **📱 Real-time Tracking**: Live GPS tracking during rides via WebSockets
- **💬 In-app Chat**: Real-time messaging between drivers and passengers
- **⭐ Rating System**: Two-way rating system for drivers and passengers
- **🔔 Push Notifications**: Firebase Cloud Messaging for instant alerts
- **🛡️ Driver Verification**: Document verification for driver safety
- **📊 Admin Dashboard**: Comprehensive analytics and management tools
- **🌐 Multi-language Support**: English and Hindi (expandable)

### 🎯 Target Market

- **Primary**: Office commuters in Tier 1 & Tier 2 Indian cities
- **Secondary**: College students, daily travelers
- **Geography**: Pan-India with focus on Delhi NCR, Mumbai, Bangalore, Pune

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Django** | 4.2+ | Web framework and ORM |
| **Django REST Framework** | 3.14+ | RESTful API development |
| **PostgreSQL** | 14+ | Primary relational database |
| **Redis** | 6+ | Caching and message broker |
| **Django Channels** | 4.0+ | WebSocket support for real-time features |
| **Celery** | 5.3+ | Background task processing |
| **Razorpay** | Latest | Payment gateway (India) |
| **Firebase Admin SDK** | Latest | Push notifications |
| **Cloudinary** | Latest | Image and file storage |
| **Twilio** | Latest | SMS and OTP services |
| **Poetry** | 1.7+ | Dependency management |
| **JWT** | Latest | Token-based authentication |
| **Google Maps API** | Latest | Geocoding and distance calculation |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Mobile/Web App                          │
│                    (React Native / React)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS/WSS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway / Nginx                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django Backend (ASGI)                       │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ REST APIs    │ WebSockets   │ Admin Panel  │ Celery Tasks │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└───┬─────────────┬─────────────┬─────────────┬──────────────────┘
    │             │             │             │
    ▼             ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐
│PostgreSQL│  │  Redis  │  │ Celery  │  │ External APIs│
│         │  │ (Cache) │  │ Worker  │  │              │
│ Primary │  │ Channel │  │ Beat    │  │ • Razorpay   │
│   DB    │  │ Layers  │  │         │  │ • Firebase   │
└─────────┘  └─────────┘  └─────────┘  │ • Cloudinary │
                                        │ • Twilio     │
                                        │ • Google Maps│
                                        └──────────────┘
```

---

## 📁 Project Structure

```
CoRide(PRO)/
│
├── coride/                          # Main project configuration
│   ├── __init__.py                  # Celery app initialization
│   ├── settings.py                  # Django settings (production-ready)
│   ├── urls.py                      # Main URL routing
│   ├── asgi.py                      # ASGI config for WebSockets
│   ├── wsgi.py                      # WSGI config for deployment
│   └── celery.py                    # Celery configuration
│
├── authentication/                  # User authentication & OTP
│   ├── models.py                    # OTP model
│   ├── views.py                     # Login, register, verify OTP
│   ├── serializers.py               # Auth serializers
│   ├── urls.py                      # Auth endpoints
│   ├── tasks.py                     # OTP cleanup, SMS sending
│   └── tests.py                     # Auth tests
│
├── users/                           # User profile management
│   ├── models.py                    # Custom User model
│   ├── managers.py                  # Custom user manager
│   ├── views.py                     # Profile CRUD operations
│   ├── serializers.py               # User serializers
│   └── urls.py                      # User endpoints
│
├── drivers/                         # Driver registration & verification
│   ├── models.py                    # Driver, Vehicle, Document models
│   ├── views.py                     # Driver registration, verification
│   ├── serializers.py               # Driver serializers
│   └── urls.py                      # Driver endpoints
│
├── rides/                           # Ride creation & management
│   ├── models.py                    # Ride model
│   ├── views.py                     # Create, search, manage rides
│   ├── serializers.py               # Ride serializers
│   ├── consumers.py                 # WebSocket consumer for tracking
│   ├── routing.py                   # WebSocket URL routing
│   ├── tasks.py                     # Ride reminders, expiry updates
│   └── urls.py                      # Ride endpoints
│
├── bookings/                        # Ride booking system
│   ├── models.py                    # Booking model
│   ├── views.py                     # Create, cancel bookings
│   ├── serializers.py               # Booking serializers
│   └── urls.py                      # Booking endpoints
│
├── payments/                        # Payment processing
│   ├── models.py                    # Payment, Transaction models
│   ├── views.py                     # Razorpay integration
│   ├── serializers.py               # Payment serializers
│   ├── tasks.py                     # Payout processing
│   └── urls.py                      # Payment endpoints
│
├── notifications/                   # Push notifications
│   ├── models.py                    # Notification model
│   ├── views.py                     # Notification management
│   ├── consumers.py                 # WebSocket consumer
│   ├── tasks.py                     # FCM notification sending
│   └── urls.py                      # Notification endpoints
│
├── ratings/                         # Rating & review system
│   ├── models.py                    # Rating model
│   ├── views.py                     # Submit, view ratings
│   ├── serializers.py               # Rating serializers
│   └── urls.py                      # Rating endpoints
│
├── chat/                            # Real-time messaging
│   ├── models.py                    # ChatMessage model
│   ├── views.py                     # Chat history
│   ├── consumers.py                 # WebSocket consumer for chat
│   ├── routing.py                   # WebSocket URL routing
│   └── urls.py                      # Chat endpoints
│
├── admin_panel/                     # Admin dashboard
│   ├── models.py                    # Admin models
│   ├── views.py                     # Analytics, reports
│   ├── serializers.py               # Admin serializers
│   ├── tasks.py                     # Daily reports
│   └── urls.py                      # Admin endpoints
│
├── utils/                           # Shared utilities
│   ├── constants.py                 # Platform constants
│   ├── helpers.py                   # Helper functions
│   ├── validators.py                # Custom validators
│   ├── permissions.py               # DRF permission classes
│   ├── exceptions.py                # Custom exceptions
│   ├── pagination.py                # Pagination classes
│   └── responses.py                 # Response utilities
│
├── templates/                       # Email templates
│   └── emails/                      # Email HTML templates
│
├── static/                          # Static files
│   ├── css/                         # Stylesheets
│   ├── js/                          # JavaScript files
│   └── images/                      # Images
│
├── logs/                            # Application logs
│   └── coride.log                   # Main log file
│
├── .env                             # Environment variables (not in git)
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── pyproject.toml                   # Poetry dependencies
├── poetry.lock                      # Locked dependencies
├── manage.py                        # Django management script
├── Procfile                         # Deployment configuration
├── runtime.txt                      # Python version for deployment
└── README.md                        # This file
```

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Redis 6+** - [Download](https://redis.io/download)
- **Poetry** - [Installation Guide](https://python-poetry.org/docs/#installation)
- **Git** - [Download](https://git-scm.com/downloads)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/coride-backend.git
cd coride-backend
```

### 2. Install Poetry (if not already installed)

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Linux/macOS:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Activate Virtual Environment

```bash
poetry shell
```

### 5. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your actual credentials
# Use your preferred text editor
notepad .env  # Windows
nano .env     # Linux/macOS
```

### 6. Create PostgreSQL Database

```sql
-- Open PostgreSQL shell
psql -U postgres

-- Create database
CREATE DATABASE coride_db;

-- Create user (optional)
CREATE USER coride_user WITH PASSWORD 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE coride_db TO coride_user;

-- Exit
\q
```

### 7. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

### 9. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 10. Start Redis Server

**Windows:**
```bash
redis-server
```

**Linux/macOS:**
```bash
sudo service redis-server start
```

### 11. Start Celery Worker (in a new terminal)

```bash
celery -A coride worker -l info --pool=solo
```

### 12. Start Celery Beat (in another new terminal)

```bash
celery -A coride beat -l info
```

### 13. Start Development Server

```bash
python manage.py runserver
```

🎉 **Your CoRide backend is now running at** `http://localhost:8000`

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| **Django Core** |
| `SECRET_KEY` | Django secret key (50+ characters) | `django-insecure-xyz...` | ✅ Yes |
| `DEBUG` | Debug mode (True/False) | `True` | ✅ Yes |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` | ✅ Yes |
| **Database** |
| `DATABASE_NAME` | PostgreSQL database name | `coride_db` | ✅ Yes |
| `DATABASE_USER` | PostgreSQL username | `postgres` | ✅ Yes |
| `DATABASE_PASSWORD` | PostgreSQL password | `your_password` | ✅ Yes |
| `DATABASE_HOST` | Database host | `localhost` | ✅ Yes |
| `DATABASE_PORT` | Database port | `5432` | ✅ Yes |
| **JWT** |
| `JWT_ACCESS_TOKEN_EXPIRY` | Access token expiry (minutes) | `60` | ✅ Yes |
| `JWT_REFRESH_TOKEN_EXPIRY` | Refresh token expiry (days) | `7` | ✅ Yes |
| `JWT_SIGNING_KEY` | JWT signing key | `your_secret_key` | ✅ Yes |
| **Razorpay** |
| `RAZORPAY_KEY_ID` | Razorpay API key ID | `rzp_test_xxxxx` | ✅ Yes |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret | `your_secret` | ✅ Yes |
| `RAZORPAY_WEBHOOK_SECRET` | Webhook secret | `your_webhook_secret` | ✅ Yes |
| **Google Maps** |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | `AIzaSyXXXXX` | ✅ Yes |
| **Cloudinary** |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | `your_cloud_name` | ✅ Yes |
| `CLOUDINARY_API_KEY` | Cloudinary API key | `123456789` | ✅ Yes |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | `your_secret` | ✅ Yes |
| **Firebase** |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase JSON | `firebase-credentials.json` | ✅ Yes |
| `FIREBASE_PROJECT_ID` | Firebase project ID | `coride-app` | ✅ Yes |
| **Twilio** |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | `ACxxxxxxxx` | ✅ Yes |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | `your_token` | ✅ Yes |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | `+1234567890` | ✅ Yes |
| **Redis** |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | ✅ Yes |
| `REDIS_CACHE_URL` | Redis cache URL | `redis://localhost:6379/1` | ✅ Yes |
| **Celery** |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` | ✅ Yes |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/0` | ✅ Yes |
| **Email** |
| `EMAIL_HOST` | SMTP host | `smtp.gmail.com` | ❌ No |
| `EMAIL_PORT` | SMTP port | `587` | ❌ No |
| `EMAIL_HOST_USER` | Email address | `your_email@gmail.com` | ❌ No |
| `EMAIL_HOST_PASSWORD` | Email password/app password | `your_password` | ❌ No |
| **Platform Settings** |
| `PLATFORM_COMMISSION_PERCENT` | Platform commission | `15` | ✅ Yes |
| `OTP_EXPIRY_MINUTES` | OTP expiry time | `10` | ✅ Yes |
| `FRONTEND_URL` | Frontend URL | `http://localhost:3000` | ✅ Yes |

---

## 📚 API Documentation

### Interactive API Documentation

CoRide provides comprehensive interactive API documentation:

#### Swagger UI (Recommended)
- **URL**: `http://localhost:8000/api/docs/`
- **Features**: Interactive API testing, request/response examples
- **Best for**: Testing APIs during development

#### ReDoc
- **URL**: `http://localhost:8000/api/redoc/`
- **Features**: Clean, readable documentation
- **Best for**: API reference and integration guide

#### OpenAPI Schema
- **URL**: `http://localhost:8000/api/schema/`
- **Format**: JSON/YAML
- **Best for**: Generating client SDKs

### Authentication

All protected endpoints require JWT authentication:

```bash
# 1. Register/Login to get tokens
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "password": "YourPassword123!"
  }'

# Response:
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}

# 2. Use access token in subsequent requests
curl -X GET http://localhost:8000/api/v1/rides/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Example API Requests

#### Search Rides
```bash
curl -X GET "http://localhost:8000/api/v1/rides/search/?origin_lat=28.6139&origin_lon=77.2090&destination_lat=28.5355&destination_lon=77.3910&date=2024-01-20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Booking
```bash
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ride_id": 123,
    "seats": 2
  }'
```

---

## 🏃 Running Services

### Development Environment

Run these commands in separate terminal windows:

#### 1. Django Development Server
```bash
python manage.py runserver
```
Access at: `http://localhost:8000`

#### 2. Celery Worker
```bash
# Windows
celery -A coride worker -l info --pool=solo

# Linux/macOS
celery -A coride worker -l info
```

#### 3. Celery Beat Scheduler
```bash
celery -A coride beat -l info
```

#### 4. Redis Server
```bash
# Windows
redis-server

# Linux
sudo service redis-server start

# macOS
brew services start redis
```

#### 5. Celery Flower (Monitoring - Optional)
```bash
celery -A coride flower
```
Access at: `http://localhost:5555`

### Production Environment

For production, use process managers like **Supervisor** or **systemd**:

```bash
# Example using Gunicorn + Daphne
gunicorn coride.wsgi:application --bind 0.0.0.0:8000
daphne -b 0.0.0.0 -p 8001 coride.asgi:application
```

---

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Tests for Specific App
```bash
python manage.py test authentication
python manage.py test rides
```

### Run Tests with Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report
coverage html  # HTML report in htmlcov/
```

### Run Specific Test Class
```bash
python manage.py test authentication.tests.OTPTestCase
```

---

## 🚢 Deployment

### Railway Deployment

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login to Railway**
```bash
railway login
```

3. **Initialize Project**
```bash
railway init
```

4. **Add PostgreSQL**
```bash
railway add postgresql
```

5. **Add Redis**
```bash
railway add redis
```

6. **Set Environment Variables**
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG="False"
# ... set all other variables
```

7. **Deploy**
```bash
railway up
```

### Environment-Specific Settings

- **Development**: `DEBUG=True`, local database
- **Staging**: `DEBUG=False`, staging database, test payment keys
- **Production**: `DEBUG=False`, production database, live payment keys

---

## 🤝 Contributing

We welcome contributions to CoRide! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write/update tests**
5. **Ensure all tests pass**
   ```bash
   python manage.py test
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

### Code Style

- Follow **PEP 8** style guide
- Use **type hints** where applicable
- Write **docstrings** for all functions/classes
- Keep functions **small and focused**
- Add **comments** for complex logic

### Commit Message Format

```
Type: Brief description

Detailed description (if needed)

Types: Add, Update, Fix, Remove, Refactor, Docs, Test
```

---

## 📄 License

**Proprietary License**

Copyright © 2024 CoRide. All rights reserved.

This software and associated documentation files (the "Software") are proprietary and confidential. Unauthorized copying, distribution, modification, or use of this Software, via any medium, is strictly prohibited without explicit written permission from CoRide.

For licensing inquiries, contact: legal@coride.in

---

## 📞 Support & Contact

- **Email**: support@coride.in
- **Website**: https://coride.in
- **Documentation**: https://docs.coride.in
- **Issue Tracker**: https://github.com/coride/backend/issues

---

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- All open-source contributors
- Our amazing development team

---

<div align="center">
  
  **Made with ❤️ in India**
  
  *Reducing traffic, one ride at a time*
  
  [Website](https://coride.in) • [API Docs](http://localhost:8000/api/docs/) • [Support](mailto:support@coride.in)
  
</div>
