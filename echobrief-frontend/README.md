# EchoBrief Frontend

[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5+-purple.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3+-teal.svg)](https://tailwindcss.com/)

EchoBrief is a modern web application that transforms news articles into engaging podcast audio content. This frontend provides an intuitive interface for users to manage their news preferences, generate AI-powered podcasts, and consume content in audio format.

## Overview

The EchoBrief frontend delivers a sleek, responsive user experience with a distinctive "brutal" design aesthetic. Users can:

- Browse and search news articles from multiple sources
- Generate personalized podcast content based on selected topics
- Listen to AI-generated audio podcasts with a built-in player
- Manage subscriptions and user preferences
- Access admin controls for content management (admin users)

## Key Features

### 🎧 Podcast Player
- **Built-in Audio Player**: Play, pause, and seek through generated podcasts
- **Volume Control**: Adjustable volume with mute toggle
- **Persistent Player**: Bottom-docked player that persists across navigation

### 📰 Article Management
- **Topic Filtering**: Filter articles by topic categories
- **Search Functionality**: Debounced search for articles and podcasts
- **Pagination**: Load more content with infinite scroll pattern

### 👤 User Experience
- **Onboarding Flow**: Guided setup for new users (plan selection, topics, avatar)
- **Profile Management**: Update username, avatar, and topic preferences
- **Global Search**: Search across articles, topics, and sources

### 🔐 Authentication
- **JWT Authentication**: Secure token-based authentication
- **Google OAuth**: Social login integration
- **Token Refresh**: Automatic token refresh handling

### 🛠️ Admin Dashboard
- **User Management**: View and edit user roles/plans
- **Content CRUD**: Manage sources and topics
- **System Operations**: Trigger news aggregation and subscription checks

## Tech Stack

### Core Technologies
- **Build Tool**: [Vite](https://vitejs.dev/) - Next-generation frontend tooling
- **Framework**: [React 18+](https://reactjs.org/) with functional components and hooks
- **Language**: [TypeScript](https://www.typescriptlang.org/) for type-safe development
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) with custom brutal design system

### UI Components
- **Component Library**: [shadcn/ui](https://ui.shadcn.com/) - Re-usable components built on Radix UI
- **Icons**: [Lucide React](https://lucide.dev/) - Beautiful & consistent icons
- **Toast Notifications**: [Sonner](https://sonner.emilkowal.ski/) for elegant notifications

### State & Data
- **Routing**: [React Router v6](https://reactrouter.com/) for client-side navigation
- **HTTP Client**: [Axios](https://axios-http.com/) with interceptors for auth handling
- **Query Management**: [@tanstack/react-query](https://tanstack.com/query) for server state

### Development
- **Code Quality**: ESLint with TypeScript rules
- **Package Manager**: npm
- **API Proxy**: Vite proxy configuration for backend API

## Pages Overview

| Page | Path | Description |
|------|------|-------------|
| Landing | `/` | Public landing page |
| Auth | `/auth` | Login and registration |
| Onboarding | `/onboarding` | New user setup flow |
| Dashboard | `/dashboard` | User home with stats and recent content |
| Articles | `/articles` | Browse and filter articles |
| Article Detail | `/articles/:id` | Single article view |
| Podcasts | `/podcasts` | Podcast listing with audio player |
| Search | `/search` | Global search across all content |
| Profile | `/profile` | User settings and preferences |
| Admin | `/admin` | Admin dashboard (admin only) |


## Design System

EchoBrief uses a custom "Brutal" design system with:

- **Bold Borders**: 2-3px solid borders
- **Shadow Effects**: Offset box shadows for depth
- **Vibrant Colors**: Primary (yellow), Secondary (pink), Accent (blue)
- **Typography**: Bold, uppercase headings with strong hierarchy

Custom components include:
- `BrutalButton` - Bold buttons with shadow effects
- `BrutalCard` - Cards with thick borders
- `BrutalBadge` - Status badges
- `BrutalInputField` - Styled form inputs
- `BrutalModal` - Dialog modals

---

**EchoBrief** - Transforming news into conversations, one podcast at a time.
