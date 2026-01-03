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
- **Cache/Queue**: [Redis 7+](https://redis.io/) for caching and task queuing
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

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | User registration with validation |
| `POST` | `/login` | JWT token generation |
| `POST` | `/refresh` | Access token refresh |
| `GET` | `/google` | Google OAuth URL generation |
| `GET` | `/google/callback` | OAuth callback handling |
| `POST` | `/forgot-password` | Password reset request |
| `POST` | `/reset-password` | Password reset confirmation |

### User Management (`/api/v1/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/profile` | Get user profile information |
| `PUT` | `/profile` | Update user profile |
| `POST` | `/avatar` | Upload custom avatar |
| `DELETE` | `/avatar` | Remove current avatar |
| `POST` | `/onboarding` | Complete user onboarding |

### Content Management
#### Articles (`/api/v1/articles`)
- CRUD operations for news articles
- Filtering by topics, sources, and date ranges

#### Sources (`/api/v1/sources`)
- RSS source configuration and management
- Bulk import/export capabilities

#### Topics (`/api/v1/topics`)
- News category management
- User topic preferences

#### Podcasts (`/api/v1/podcasts`)
- Podcast generation requests
- Audio file management and streaming
- Generation status tracking

### Dashboard (`/api/v1/dashboard`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stats` | User dashboard statistics |
| `GET` | `/search` | Global content search |

### Subscriptions (`/api/v1/subscriptions`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/create` | Create new subscription |
| `GET` | `/status` | Current subscription details |
| `DELETE` | `/cancel` | Cancel active subscription |

### Admin Panel (`/api/v1/admin`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | List all users with pagination |
| `PUT` | `/users/{id}` | Update user details/roles |
| `POST` | `/articles` | Create new articles |
| `PUT` | `/articles/{id}` | Update article information |
| `DELETE` | `/articles/{id}` | Remove articles |
| `POST` | `/sources` | Add news sources |
| `POST` | `/sources/bulk` | Bulk source import |
| `PUT` | `/sources/{id}` | Update source details |
| `DELETE` | `/sources/{id}` | Remove sources |
| `POST` | `/topics` | Create news topics |
| `POST` | `/topics/bulk` | Bulk topic import |
| `PUT` | `/topics/{id}` | Update topic information |
| `DELETE` | `/topics/{id}` | Remove topics |
| `DELETE` | `/podcasts/{id}` | Delete podcast content |
| `POST` | `/system/aggregate-news` | Trigger news aggregation |
| `POST` | `/subscriptions/check-expired` | Process expired subscriptions |

### System (`/api/v1/system`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health/db` | Database health check |

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

**EchoBrief** - Transforming news into conversations, one podcast at a time.
