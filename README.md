# Traditional Swedish Fika Register 🇸🇪

A comprehensive web application for discovering authentic Swedish fika experiences across major cities. Built with modern web technologies and Swedish cultural authenticity in mind.

## Features

- **🏙️ City-based Discovery**: Explore fika spots in Stockholm, Gothenberg, Malmö, Uppsala, and Västerås
- **🔍 Smart Search**: AI-powered search with Swedish language support
- **🤖 AI Recommendations**: LangChain-powered personalized suggestions
- **📱 Responsive Design**: Mobile-first, SEO-optimized frontend
- **⚡ High Performance**: Redis caching and optimized database queries
- **🐳 Docker Ready**: Complete development environment with Docker Compose

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **SQLAlchemy**: Database ORM with PostgreSQL
- **LangChain**: AI agent framework for recommendations
- **Redis**: Caching and session management
- **Prometheus**: Metrics and monitoring

### Frontend
- **HTML/CSS/JavaScript**: SEO-friendly progressive enhancement
- **Swedish Design System**: Inspired by Swedish design principles
- **Responsive Grid**: Modern CSS Grid and Flexbox layouts

### Infrastructure
- **Docker**: Containerized development and deployment
- **PostgreSQL**: Primary database with JSON support
- **Redis**: High-performance caching layer
- **Digital Ocean**: Production hosting platform

## Quick Start

### Development Environment (Docker)

1. **Clone and setup**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/traditional-swedish-fika.git
   cd traditional-swedish-fika
   cp .env.example .env
   ```

2. **Configure environment**:
   Edit `.env` with your API keys:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   OPENROUTER_API_KEY=your_openrouter_key
   UPSTASH_REDIS_URL=your_redis_url
   ```

3. **Start with Docker**:
   ```bash
   ./setup.sh
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - AI Dashboard: http://localhost:8000/ai/dashboard
   - API Docs: http://localhost:8000/docs

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── ai/             # AI agents and services
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── frontend/               # Static frontend
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/          # HTML templates
├── docker/                 # Docker configurations
├── nginx/                  # Nginx configuration
└── docs/                   # Documentation

```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Swedish Fika Culture

Fika is more than just a coffee break - it's a Swedish cultural institution that emphasizes slowing down, enjoying quality time with others, and savoring traditional pastries like kanelbullar (cinnamon buns) and prinsesstårta (princess cake).

Our platform celebrates this tradition by helping you discover authentic fika experiences across Sweden's major cities, from historic konditoris that have served communities for generations to modern cafés that continue the tradition with contemporary flair.