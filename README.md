# TRON Wallet Info Service

A FastAPI-based microservice that provides information about TRON network addresses, including bandwidth, energy, and TRX balance.

## Features

- Get wallet information (TRX balance, bandwidth, energy)
- Store queries in SQLite database
- Paginated query history
- Fully typed with Python type annotations
- Unit and integration tests
- Environment-based configuration

## Installation

## Configuration

The service uses a centralized settings module (`app/settings.py`) to manage all configuration. Settings can be provided through environment variables or a `.env` file.

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```
# Database configuration
DATABASE_URL=sqlite+aiosqlite:///./tron_service.db

# TRON network configuration (mainnet, shasta, nile)
TRON_NETWORK=mainnet

# Test database configuration (used only for testing)
TEST_DATABASE_URL=sqlite+aiosqlite:///./test.db
```

All settings are managed through the `Settings` class in `app/settings.py`. The following settings are available:

- `database_url`: SQLAlchemy database URL (default: sqlite+aiosqlite:///./tron_service.db)
- `tron_network`: TRON network to use (default: mainnet)

### Using Docker Compose (Recommended)

1. Start the service:
```bash
docker-compose up -d
```

2. Stop the service:
```bash
docker-compose down
```

The service will be available at http://localhost:8000

### Using Docker

1. Build the Docker image:
```bash
docker build -t tron-wallet-service .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 tron-wallet-service
```

The service will be available at http://localhost:8000

### Manual Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the service using uvicorn:
```bash
uvicorn app.main:app --reload
```

The service will be available at http://localhost:8000

## API Endpoints

### POST /wallet-info/
Get information about a TRON wallet address.

Request body:
```json
{
    "wallet_address": "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

### GET /wallet-queries/
Get a paginated list of recent wallet queries.

Query parameters:
- page: Page number (default: 1)
- size: Items per page (default: 10)

## Running Tests

Run the tests using pytest:
```bash
pytest tests/
```

## Technologies Used

- FastAPI
- SQLAlchemy (async)
- tronpy
- pytest
- SQLite




