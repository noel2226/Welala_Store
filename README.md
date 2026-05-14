# Welala Store - FastAPI Ecommerce API

A high-performance ecommerce API for selling books and general goods, built with FastAPI and SQLAlchemy.

## Features

- ✨ **Type-Safe**: Full type hints with Pydantic v2
- 📚 **Flexible Schema**: Support for books and general goods with category-specific fields
- 🚀 **High Performance**: Async/await with connection pooling
- 📖 **Auto Documentation**: Interactive Swagger UI and ReDoc
- 🔒 **Data Validation**: Comprehensive input validation
- 📝 **Well Structured**: Clean, modular project architecture
- 🗄️ **SQLAlchemy ORM**: Type-safe database operations
- 🌍 **CORS Support**: Ready for multi-origin requests
- 📊 **Pagination**: Built-in pagination for list endpoints
- 🔍 **Search & Filter**: Full-text search and category filtering

## Project Structure

```
Welala_Store/
├── app/
│   ├── api/             # API route handlers
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── utils/           # Utility functions
│   ├── config.py        # Configuration management
│   ├── database.py      # Database setup
│   └── main.py          # App factory
├── .env                 # Environment variables
├── requirements.txt     # Dependencies
└── run.py              # Application runner
```

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/noel2226/Welala_Store.git
   cd Welala_Store
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the app is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Products

#### List Products
```http
GET /products?skip=0&limit=10&category=book&search=gatsby
```

**Query Parameters:**
- `skip` (int): Items to skip (default: 0)
- `limit` (int): Items per page (default: 10, max: 100)
- `category` (string): Filter by 'book' or 'general_good'
- `search` (string): Search in title and description

**Response:**
```json
{
  "total": 100,
  "skip": 0,
  "limit": 10,
  "data": [
    {
      "id": 1,
      "title": "The Great Gatsby",
      "description": "A classic American novel",
      "price": 12.99,
      "stock": 50,
      "category": "book",
      "author": "F. Scott Fitzgerald",
      "isbn": "978-0-7432-7356-5",
      "weight": null,
      "dimensions": null,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

#### Create Product
```http
POST /products
Content-Type: application/json

{
  "title": "The Great Gatsby",
  "description": "A classic American novel",
  "price": 12.99,
  "stock": 50,
  "category": "book",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0-7432-7356-5"
}
```

**Response:** `201 Created`

#### Get Product
```http
GET /products/1
```

**Response:**
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "price": 12.99,
  "stock": 50,
  "category": "book",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0-7432-7356-5",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Update Product
```http
PATCH /products/1
Content-Type: application/json

{
  "stock": 45,
  "price": 11.99
}
```

**Response:** `200 OK` with updated product

#### Delete Product
```http
DELETE /products/1
```

**Response:** `204 No Content`

## Examples

### Add a Book
```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Design Patterns",
    "description": "Learn design patterns in Python",
    "price": 45.99,
    "stock": 20,
    "category": "book",
    "author": "Chetan Giridhar",
    "isbn": "978-1784391900"
  }'
```

### Add General Good
```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop Stand",
    "description": "Adjustable aluminum laptop stand",
    "price": 49.99,
    "stock": 100,
    "category": "general_good",
    "weight": 0.5,
    "dimensions": "30x20x2 cm"
  }'
```

### Search Products
```bash
curl http://localhost:8000/products?search=python&category=book
```

### Get Product Details
```bash
curl http://localhost:8000/products/1
```

### Update Stock
```bash
curl -X PATCH http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{"stock": 15}'
```

## Development

### Run with Auto-reload
The application runs with auto-reload enabled in debug mode. Changes to files will automatically restart the server.

### Database
- Default: SQLite (`ecommerce.db`)
- Location: Project root directory
- Migrations: Currently using SQLAlchemy's `create_all()`. For production, consider using Alembic.

### Logging
- Console output enabled
- Adjustable via `DEBUG` environment variable
- Log format includes timestamp, logger name, level, and message

## Extending the API

### Add New Endpoints
1. Create route functions in `app/api/products.py` or new files in `app/api/`
2. Use the `router` decorator
3. Include the router in `app/main.py`

### Add Fields to Product Model
1. Update `app/models/product.py` with new columns
2. Create Pydantic schemas in `app/schemas/product.py`
3. Update validation logic as needed

### Database Migration
For production systems, use Alembic:
```bash
pip install alembic
alembic init migrations
```

## Performance Considerations

- Connection pooling enabled (default: 10 connections, max 20 overflow)
- Pagination built-in to prevent large result sets
- Database indexing on frequently searched fields (title, category, price)
- Async endpoint handling with Uvicorn workers

## Testing

Add tests using pytest:
```bash
pip install pytest pytest-asyncio httpx
```

Example test structure:
```python
# tests/test_products.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert "data" in response.json()
```

## Production Deployment

### Using Gunicorn + Uvicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Environment Configuration
- Set `DEBUG=False` in `.env`
- Use PostgreSQL or MySQL instead of SQLite
- Enable proper CORS origins
- Set up proper logging infrastructure

## License

MIT

## Contributing

Pull requests are welcome! Please follow PEP 8 and include tests.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
