# Traditional Swedish Fika Register

A comprehensive web application for discovering traditional Swedish fika locations across Sweden's major cities.

## Features

- **Public Frontend**: SEO-friendly pages for each major Swedish city (Stockholm, Gothenburg, Malmö, Uppsala, Västerås)
- **AI-Powered Backend**: Private dashboard with AI recommendations and content management
- **Comprehensive Database**: Curated fika locations with reviews, ratings, and traditional specialties
- **Smart Caching**: Redis-powered caching for optimal performance
- **AI Integration**: LangChain agents with OpenRouter LLM for personalized recommendations

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Database**: Supabase (Production) / SQLite (Development)
- **Caching**: Redis via Upstash
- **AI**: LangChain + OpenRouter
- **Deployment**: Docker + Digital Ocean

## Quick Start

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/swedish-fika-register.git
cd swedish-fika-register
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the development environment:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

5. Load initial data:
```bash
docker-compose exec backend python scripts/load_initial_data.py
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- AI Dashboard: http://localhost:8000/ai/dashboard

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