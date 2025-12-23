# Scanno Backend

Scanno Backend is the server-side application for the Scanno system.
It provides API endpoints, admin operations, configuration handling, logging, and shared utilities.
The project is structured to be modular, maintainable, and easy to extend.


## Project Structure
```txt
Scanno-Backend/
│
├── config/                 # Configuration files and settings
├── utils/                  # Shared utility and helper functions
│
├── admin_routes.py         # Admin-specific API routes
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── scanno_ai.log           # Application log file
```


## Technology Stack

- Python

- FastAPI

- Uvicorn

- Pydantic

- Python Logging


## Prerequisites

- Python 3.9 or higher

- pip (Python package manager)



## Create a Virtual Environment (Recommended)
```txt
python -m venv venv
```

### Activate the environment:
```txt
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### Install Dependencies
```txt
pip install -r requirements.txt
```


## Run the Application
```txt
python main.py
```
Or using Uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at:
```bash
http://127.0.0.1:8000
```

API documentation (Swagger UI):
```bash
http://127.0.0.1:8000/docs
```

## API Routing
### Admin Routes
Admin-related endpoints are defined in:
```txt
admin_routes.py
```

These routes are intended for:

- Administrative actions

- System management

- Restricted operations

They should be included in main.py using FastAPI routers.



## Configuration

All configuration-related logic is stored in the config/ directory.

Typical usage includes:

- Environment variables

- Application settings

- API keys

- Feature flags

This separation improves security and maintainability.



## Utilities

The utils/ directory contains reusable helper functions used across the application, such as:

- Common validation logic

- Shared formatting functions

- Reusable business logic


## Logging

Application logs are written to:
```txt
scanno_ai.log
```

Logging is used for:

- Error tracking

- Debugging

- Monitoring application behavior

- For production deployments, logs can be redirected to centralized logging services.


## Deployment Notes

For production environments:

- Use environment variables or .env files

- Run behind a production-grade ASGI server

- Secure admin endpoints with authentication and authorization


## Future Enhancements

- Authentication and authorization

- Database integration

- Docker and Docker Compose support

- CI/CD pipeline

- API rate limiting

- Structured logging and monitoring
