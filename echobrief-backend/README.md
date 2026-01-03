# EchoBrief Backend API

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io/)

EchoBrief is a comprehensive backend API built with FastAPI that transforms news articles into engaging podcast audio content. The system automatically aggregates news from RSS feeds, generates AI-powered summaries, creates podcast scripts, and converts them to audio using advanced Text-to-Speech technology.

## Overview

EchoBrief revolutionizes news consumption by converting traditional text-based articles into immersive audio experiences. Our AI-powered platform automatically:

- Aggregates news from multiple RSS sources
- Generates intelligent summaries and topic classifications
- Creates engaging podcast scripts
- Produces high-quality audio content using Edge TTS
- Manages user subscriptions and personalized content delivery

## Key Features

### 🤖 AI-Powered Content Processing
- **Intelligent Summarization**: Uses DeepSeek for context-aware article summaries
- **Topic Classification**: Automatic categorization using advanced AI models
- **Podcast Script Generation**: Creates engaging, conversational podcast content
- **Fallback Processing**: Robust error handling with fallback mechanisms

### 🎧 Audio Generation & Management
- **Text-to-Speech**: High-quality audio generation using Microsoft Edge TTS
- **Multiple Voices**: Support for various voice options and languages
- **Audio Storage**: Efficient storage and streaming of generated audio files
- **Background Processing**: Asynchronous audio generation with Celery

### 📰 News Aggregation System
- **RSS Feed Integration**: Automated collection from multiple news sources
- **Duplicate Detection**: Intelligent filtering of duplicate articles
- **Real-time Updates**: Continuous background news aggregation
- **Source Management**: Admin panel for source configuration

### 👥 User Management & Authentication
- **JWT Authentication**: Secure token-based authentication system
- **Google OAuth Integration**: Seamless social login functionality
- **Role-Based Access**: User and admin role management
- **Profile Management**: Custom avatars and user preferences
- **Password Reset**: Secure email-based password recovery

### 💳 Subscription & Monetization
- **Flexible Plans**: Free and paid subscription tiers ($5.00/month)
- **Ko-fi Integration**: Payment processing and subscription management
- **Usage Limits**: Plan-based feature restrictions

    #### Plan Comparison
    | Feature | Free Plan | Paid Plan ($5/month) |
    |---------|-----------|---------------------|
    | **Podcasts per day** | 1 podcast | Unlimited |
    | **Topics per podcast** | Max 3 topics | Unlimited |
    | **Topic selection** | Limited | Full access |
    | **Audio quality** | Standard | Premium |
    | **Support** | Community | Priority |

### ⚡ Performance & Security
- **Rate Limiting**: Redis-based API rate limiting with sliding window algorithm
- **Admin Exemption**: Unrestricted access for administrative operations
- **Request Throttling**: Configurable limits per endpoint type
- **Security Headers**: Comprehensive security middleware

### 🔧 Admin Management Panel
- **User Administration**: Complete user lifecycle management
- **Content Moderation**: Article, source, and topic management
- **System Monitoring**: Health checks and system statistics
- **Bulk Operations**: Efficient bulk data management

## Tech Stack

### Core Technologies
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for Python
- **Database**: [PostgreSQL 15](https://www.postgresql.org/) with [AsyncPG](https://github.com/MagicStack/asyncpg) driver
- **Cache/Queue**: [Redis 7+](https://redis.io/) for caching, task queuing, and rate limitting
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases in Python, designed for FastAPI

### AI & Media Processing
- **AI Services**: [DeepSeek](https://platform.deepseek.com/) for text processing and summarization
- **Text-to-Speech**: [Edge TTS](https://github.com/rany2/edge-tts) for high-quality audio generation
- **Image Processing**: [Pillow](https://python-pillow.org/) for avatar image handling

### Background Processing
- **Task Queue**: [Celery](https://docs.celeryq.dev/) with Redis broker
- **Email Service**: SMTP integration with [Jinja2](https://jinja.palletsprojects.com/) templates

### Authentication & Security
- **JWT Tokens**: [PyJWT](https://pyjwt.readthedocs.io/) for secure authentication
- **OAuth**: [Authlib](https://authlib.org/) for Google OAuth 2.0 integration
- **Password Security**: [PassLib](https://passlib.readthedocs.io/) with Argon2 hashing

### Development & Deployment
- **Containerization**: [Docker](https://www.docker.com/) & Docker Compose
- **Code Quality**: [Black](https://black.readthedocs.io/), [isort](https://pycqa.github.io/isort/), [Flake8](https://flake8.pycqa.org/)
- **API Documentation**: Auto-generated OpenAPI/Swagger UI
- **Environment**: Python 3.13+ with modern async/await patterns

## API Endpoints Overview

The EchoBrief API is organized into several functional areas. All endpoints return JSON responses with a consistent structure including `message`, `data`, and optional pagination metadata. Authentication is required for most endpoints using JWT tokens.

### Authentication Endpoints (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Register a new user account | No |
| `POST` | `/auth/login` | Authenticate user and return access/refresh tokens | No |
| `POST` | `/auth/refresh` | Refresh access token using refresh token | No |
| `GET` | `/auth/google` | Get Google OAuth authorization URL | No |
| `GET` | `/auth/google/callback` | Handle Google OAuth callback and authenticate user | No |
| `POST` | `/auth/forgot-password` | Request password reset email | No |
| `POST` | `/auth/reset-password` | Reset password using reset token | No |

### User Management Endpoints (`/users`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/users/me` | Get current user profile information | Yes |
| `PUT` | `/users/me` | Update current user profile (username only) | Yes |
| `POST` | `/users/onboarding` | Complete user onboarding (plan selection, topics, avatar) | Yes |
| `POST` | `/users/topics` | Add topic to user's favorite topics | Yes |
| `DELETE` | `/users/topics/{topic_id}` | Remove topic from user's favorite topics | Yes |
| `GET` | `/users/topics` | Get user's favorite topics | Yes |
| `POST` | `/users/me/avatar` | Upload user avatar image | Yes |
| `DELETE` | `/users/me/avatar` | Delete user avatar (reset to default) | Yes |
| `GET` | `/users/{user_id}/avatar` | Get user avatar URL by user ID | Yes |

### Content Endpoints

#### Topics (`/topics`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/topics/` | Get paginated list of all topics with optional search | Yes |
| `GET` | `/topics/{topic_id}` | Get topic details by ID | Yes |
| `GET` | `/topics/slug/{slug}` | Get topic details by slug | Yes |

#### Articles (`/articles`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/articles/` | Get paginated list of articles with optional search and topic filtering | Yes |
| `GET` | `/articles/{article_id}` | Get article details by ID | Yes |

#### Sources (`/sources`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/sources/` | Get paginated list of all news sources | Yes |
| `GET` | `/sources/{source_id}` | Get source details by ID | Yes |

### Podcast Endpoints (`/podcasts`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/podcasts/` | Create a new podcast request (uses user's favorite topics if none specified) | Yes |
| `GET` | `/podcasts/` | Get paginated list of user's podcasts with optional search | Yes |
| `GET` | `/podcasts/{podcast_id}` | Get podcast details by ID | Yes |
| `POST` | `/podcasts/{podcast_id}/generate-script` | Generate AI script for a podcast | Yes |
| `POST` | `/podcasts/{podcast_id}/generate-audio` | Generate audio file for a podcast using TTS | Yes |
| `POST` | `/podcasts/quick-generate` | Quick podcast generation with caching support | Yes |

### Dashboard & Search Endpoints (`/dashboard`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/dashboard/` | Get user dashboard with statistics, recent podcasts, articles, and favorite topics | Yes |
| `GET` | `/dashboard/search` | Global search across articles, topics, and sources | Yes |

### Subscription Endpoints (`/subscriptions`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/subscriptions/webhooks/kofi` | Handle Ko-fi payment webhooks | No |
| `GET` | `/subscriptions/me` | Get current user's active subscription | Yes |
| `GET` | `/subscriptions/plan-type` | Get user's effective plan type (free/paid) | Yes |

### Admin Endpoints (`/admin`) - Admin Only

#### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/users` | Get paginated list of all users with optional search |
| `PUT` | `/admin/users/{user_id}` | Update user profile (username, plan_type, role) |

#### Content Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/admin/articles` | Create a new article |
| `PUT` | `/admin/articles/{article_id}` | Update article information |
| `DELETE` | `/admin/articles/{article_id}` | Delete an article |
| `POST` | `/admin/sources` | Create a new news source |
| `POST` | `/admin/sources/bulk` | Create multiple sources in bulk |
| `PUT` | `/admin/sources/{source_id}` | Update source information |
| `DELETE` | `/admin/sources/{source_id}` | Delete a source |
| `POST` | `/admin/topics` | Create a new topic |
| `POST` | `/admin/topics/bulk` | Create multiple topics in bulk |
| `PUT` | `/admin/topics/{topic_id}` | Update topic information |
| `DELETE` | `/admin/topics/{topic_id}` | Delete a topic |

#### Podcast Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `DELETE` | `/admin/podcasts/{podcast_id}` | Delete a podcast and all related data |

#### System Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/admin/system/aggregate-news` | Trigger news aggregation process |
| `POST` | `/admin/subscriptions/check-expired` | Check and update expired subscriptions |

### Response Format

All API responses follow a consistent JSON structure:

```json
{
  "message": "Operation completed successfully",
  "data": {
    // Response data varies by endpoint
  }
}
```

Paginated endpoints include additional metadata:

```json
{
  "message": "Items retrieved successfully",
  "data": {
    "items": [...],
    "total": 150,
    "page": 1,
    "per_page": 10
  }
}
```

### Authentication

Most endpoints require authentication via JWT tokens in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

Admin endpoints additionally require the user to have admin role (`role: "admin"`).

### Rate Limiting

The API implements Redis-based rate limiting with configurable limits per endpoint type and user role exemptions for admins.

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

**EchoBrief** - Transforming news into conversations, one podcast at a time.
