# Chat Bot Web Application

A real-time chat application with AI-powered responses using FastAPI and React.

## Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
```

4. Run the backend:
```bash
cd backend
uvicorn main:app --reload
```

## Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the frontend:
```bash
npm start
```

## Features

- Real-time chat interface
- AI-powered responses using OpenAI
- Message history stored in PostgreSQL
- Modern React frontend
- FastAPI backend with WebSocket support 