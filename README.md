# Emotional Companion Backend

A FastAPI-based backend service for an **Emotional Companion chatbot** that provides empathetic responses and emotional support.

TEAM: Emotional Companion

MEMBER: Mich Baldonado, Kitiyaporn Takham, Kristi, FNU Renu

## Resources
- Presentation slide: https://docs.google.com/presentation/d/1FBNdxEIudpJs6W_kRj7lG0HO_aS5iQYFjExGIlmrshQ/edit?usp=sharing
- Emotional Model: https://github.com/micahbaldonado/AI-Therapist
- Front-end: https://gitlab.com/kristibaishya/ai-emotional-companion.git
- Back-end: https://github.com/Kitiyaparnnn/Emotional-Companion-Back-end-.git

## Features

- User authentication with JWT
- Empathetic chat responses
- Chat history tracking
- MongoDB integration
- Docker support
- OAuth integration (Google)

## Prerequisites

- Python 3.11+
- MongoDB
- Docker and Docker Compose

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd emotional-companion-backend
```

2. Create a `.env` file in the root directory with the following variables:
```env
MONGODB_URL=your-mongoDB-connection
DATABASE_NAME=emotional_companion
JWT_SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key-32bytes-long!!
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

3. Build and run with Docker Compose:
```bash
docker compose up -d --build
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Main Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/token` - Login and get access token
- `POST /api/v1/auth/google` - Google OAuth authentication

### User Management
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update current user info

### Chat
- `POST /api/v1/chat/send` - Send a message to the chatbot
- `GET /api/v1/chat/history` - Get chat history
- `GET /api/v1/chat/sessions/{user_id}` - Get user's chat sessions

## Development

To run the project locally without Docker:

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 
