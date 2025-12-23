# MENA Signal

> AI Funding & Companies Intelligence with MENA Market Applicability Analysis

MENA Signal is an MVP web application that ingests global AI funding news and company launches, then generates MENA (Middle East & North Africa) market applicability scores and insights using LLM-powered analysis.

![MENA Signal Dashboard](https://via.placeholder.com/800x400?text=MENA+Signal+Dashboard)

## Features

- **📊 Real-time AI News Ingestion**: Automatically fetches from 10+ RSS sources including TechCrunch, VentureBeat, Crunchbase News, and more
- **🎯 MENA Fit Scoring**: LLM-powered analysis generates 0-100 scores with rubric breakdown
- **⭐ Favorites & Tags**: Save interesting items and organize with custom tags
- **📝 Notes**: Add personal notes to any item
- **🔍 Advanced Filtering**: Filter by type, score, date range, tags, and search
- **👤 User Authentication**: Email/password auth with JWT
- **⚙️ Source Management**: Add, enable/disable, and manage RSS sources
- **🔄 Scheduled Ingestion**: Automatic updates every 30 minutes

## Tech Stack

### Backend
- **FastAPI** (Python 3.11) - REST API
- **SQLAlchemy 2.0** - ORM
- **Alembic** - Database migrations
- **PostgreSQL 16** - Database
- **Redis** - Task queue
- **RQ (Redis Queue)** - Background jobs
- **OpenAI API** - LLM analysis

### Frontend
- **Next.js 14** (App Router) - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Lucide Icons** - Icons

### Infrastructure
- **Docker Compose** - Container orchestration
- All services run locally with one command

## Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) OpenAI API key for LLM-powered analysis

### 1. Clone and Setup

```bash
cd mena-signal

# Copy environment file
cp env.sample .env

# Edit .env and add your OpenAI API key (optional)
# If no API key is provided, stub analysis will be used
```

### 2. Start Services

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Backend API** on port 8000
- **Frontend** on port 3000
- **Background Worker** for processing jobs
- **Scheduler** for periodic ingestion

### 3. Run Initial Seed (First Time)

```bash
# In a new terminal, run the seed script
docker-compose exec backend python seed.py
```

This will:
- Load RSS sources from `sources.yaml`
- Create a demo user
- Run initial ingestion

### 4. Access the App

Open [http://localhost:3000](http://localhost:3000)

**Demo Credentials:**
- Email: `demo@menasignal.com`
- Password: `demo123`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database user | `mena` |
| `POSTGRES_PASSWORD` | Database password | `mena_secret` |
| `POSTGRES_DB` | Database name | `mena_signal` |
| `SECRET_KEY` | JWT signing key | Change in production! |
| `OPENAI_API_KEY` | OpenAI API key | (optional) |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |

## Adding New Sources

### Via YAML Configuration

Edit `backend/sources.yaml`:

```yaml
sources:
  - name: My Custom Source
    type: rss
    url: https://example.com/feed.xml
    category: funding  # or: companies, news
    enabled: true
```

Then restart the scheduler or run:

```bash
docker-compose exec backend python -c "from app.services.ingestion import load_sources_from_yaml; load_sources_from_yaml()"
```

### Via UI

1. Navigate to `/settings/sources`
2. Click "Add Source"
3. Fill in the source details
4. Click "Add Source"

### Via API

```bash
curl -X POST http://localhost:8000/api/sources \
  -H "Content-Type: application/json" \
  -H "Cookie: mena_signal_token=YOUR_TOKEN" \
  -d '{
    "name": "My Source",
    "type": "rss",
    "url": "https://example.com/feed.xml",
    "category": "funding"
  }'
```

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login user |
| `/api/auth/logout` | POST | Logout user |
| `/api/auth/me` | GET | Get current user |

### Items

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/items` | GET | List items (with filters) |
| `/api/items/{id}` | GET | Get single item |
| `/api/items` | POST | Create manual item |
| `/api/items/{id}/hide` | PATCH | Hide item |

**Query Parameters for `/api/items`:**
- `type`: `funding` or `company`
- `q`: Search query
- `min_score`: Minimum MENA fit score
- `tag`: Filter by tag ID
- `date_range`: `24h`, `7d`, or `30d`
- `page`: Page number
- `page_size`: Items per page

### Favorites

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/favorites` | GET | List favorites |
| `/api/favorites/{item_id}` | POST | Add favorite |
| `/api/favorites/{item_id}` | DELETE | Remove favorite |

### Tags

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tags` | GET | List user's tags |
| `/api/tags` | POST | Create tag |
| `/api/tags/{id}` | DELETE | Delete tag |
| `/api/tags/items/{item_id}` | POST | Assign tags to item |

### Notes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notes/items/{item_id}` | GET | Get notes for item |
| `/api/notes/items/{item_id}` | POST | Create note |
| `/api/notes/{id}` | PATCH | Update note |
| `/api/notes/{id}` | DELETE | Delete note |

### Sources

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sources` | GET | List sources |
| `/api/sources` | POST | Create source |
| `/api/sources/{id}` | PATCH | Update source |
| `/api/sources/{id}` | DELETE | Delete source |

### Ingestion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest/run` | POST | Trigger ingestion |
| `/api/ingest/runs` | GET | List ingestion runs |

## MENA Fit Scoring

The MENA applicability analysis evaluates each item across 5 dimensions (0-20 points each):

1. **Budget Buyer Exists** - MENA buyers with budget for this solution
2. **Localization Ease** - Arabic/bilingual adaptation requirements
3. **Regulatory Path** - Higher score = easier regulatory compliance
4. **Distribution Path** - Clear go-to-market channels in MENA
5. **Time to Revenue** - Speed to generate MENA revenue

**Score Interpretation:**
- 70-100: High potential for MENA market
- 40-69: Moderate MENA market fit
- 0-39: Lower MENA market applicability

### Stub Mode

If no OpenAI API key is configured, the system uses a stub scorer that returns:
- Score: 50
- Generic summary
- Equal rubric values (10 each)

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

## Project Structure

```
mena-signal/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── auth.py           # Authentication
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # DB connection
│   │   ├── main.py           # FastAPI app
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── scheduler.py      # Background scheduler
│   │   └── schemas.py        # Pydantic schemas
│   ├── tests/                # Unit tests
│   ├── sources.yaml          # Source registry
│   ├── requirements.txt      # Python dependencies
│   └── seed.py               # Seed script
├── frontend/
│   ├── app/                  # Next.js pages
│   ├── components/           # React components
│   │   └── ui/               # shadcn/ui components
│   ├── lib/                  # Utilities & API client
│   └── package.json          # Node dependencies
├── docker-compose.yml
├── env.sample
└── README.md
```

## Troubleshooting

### Services won't start

```bash
# Reset everything
docker-compose down -v
docker-compose up --build
```

### Database connection errors

```bash
# Check if postgres is healthy
docker-compose ps

# View postgres logs
docker-compose logs postgres
```

### Ingestion not working

```bash
# Check worker logs
docker-compose logs worker

# Check scheduler logs
docker-compose logs scheduler

# Manually trigger ingestion
docker-compose exec backend python -c "from app.services.ingestion import ingest_all_sources; print(ingest_all_sources())"
```

### Analysis not running

```bash
# Check if OpenAI key is set
docker-compose exec backend python -c "from app.config import get_settings; print('Key set:', bool(get_settings().openai_api_key))"

# Check worker is processing jobs
docker-compose logs -f worker
```

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Built with ❤️ for the MENA tech ecosystem
