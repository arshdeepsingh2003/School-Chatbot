# School Chatbot

A comprehensive AI-powered chatbot system for schools that handles student inquiries about academics, attendance, and advisor information. Built with FastAPI backend and React frontend, featuring admin dashboard, multi-role support, and intelligent intent recognition.

## Features

- **🤖 Intelligent Chatbot**: AI-powered responses using LLM with intent recognition
- **📚 Academic Queries**: Students can ask about marks, scores, and strongest/weakest subjects
- **📅 Attendance Tracking**: Query and analyze attendance records by student and date
- **👨‍🏫 Advisor Information**: Access advisor details and school information
- **🔐 Admin Dashboard**: Manage students, attendance records, and view chat analytics
- **🔒 Security & Validation**: Input filtering, guard responses, and admin authentication
- **🌙 Dark Mode**: Student-friendly light and dark theme support
- **📊 Chat History**: Complete tracking of all conversations
- **⚙️ Multi-Role Support**: Student, parent, and advisor roles with different permissions

## Project Structure

```
School-Chatbot/
├── backend/                          # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── models.py                # SQLAlchemy ORM models (Master, Academics, Attendance, ChatHistory)
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── database.py              # Database connection and configuration
│   │   ├── admin_routes.py          # Admin API endpoints
│   │   ├── admin_auth.py            # JWT authentication for admin
│   │   ├── llm.py                   # LLM integration (Ollama/external LLM calls)
│   │   ├── llm_guard.py             # Safety filter and guard responses
│   │   ├── filters.py               # Input validation and filtering
│   │   ├── academic_intent.py       # Academic query intent recognition
│   │   ├── attendance_intent.py     # Attendance query intent recognition
│   │   ├── advisor_intent.py        # Advisor query intent recognition
│   │   ├── intent.py                # Core intent detection logic
│   │   ├── services.py              # Business logic for fetching and processing data
│   │   ├── time_parser.py           # Date/time parsing utilities
│   │   ├── ollama_warmup.py         # LLM model warm-up on startup
│   │   └── __init__.py
│   ├── requirements.txt              # Python dependencies
│   └── README.md
│
├── frontend/                         # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx                  # Main application component
│   │   ├── main.jsx                 # Entry point
│   │   ├── App.css                  # Main styling
│   │   ├── index.css                # Global styles
│   │   ├── api.js                   # Axios API client configuration
│   │   ├── components/
│   │   │   └── ChatBox.jsx          # Main chat interface component
│   │   ├── services/
│   │   │   └── adminApi.js          # Admin API service
│   │   └── admin/
│   │       ├── AdminLogin.jsx       # Admin login page
│   │       ├── AdminDashboard.jsx   # Admin dashboard main component
│   │       ├── AdminAttendance.jsx  # Attendance management
│   │       ├── AdminStudents.jsx    # Student management
│   │       └── admin.css            # Admin styling
│   │
│   ├── public/                       # Static files
│   ├── index.html                   # HTML entry point
│   ├── package.json                 # NPM dependencies
│   ├── vite.config.js               # Vite configuration
│   ├── eslint.config.js             # ESLint configuration
│   └── README.md
│
└── README.md                         # This file
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database (configurable via DATABASE_URL)
- **Ollama/LLM**: Local or remote language model
- **Pydantic**: Data validation
- **Python-dotenv**: Environment configuration

### Frontend
- **React 19**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **Recharts**: Data visualization
- **CSS3**: Styling

## Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** (for frontend)
- **npm** or **yarn** (package manager)
- **Ollama** or LLM service (optional, for AI features)
- **SQLite** (included with Python)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd School-Chatbot
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./chat.db

# Admin Secret (for JWT tokens)
SECRET_KEY=your_secret_key_here

# LLM Configuration
LLM_MODEL=mistral          # or your preferred model
LLM_BASE_URL=http://localhost:11434/api

# Optional: Other configurations
DEBUG=False
```

### 4. Initialize Database

The database tables are automatically created on first run. To manually create them:

```bash
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"
```

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Running the Application

### Start Backend Server

From the `backend` directory:

```bash
# Make sure venv is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

### Start Frontend Development Server

From the `frontend` directory:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or as shown in terminal)

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

This creates a `dist` folder with optimized production build.

Backend:
```bash
# Use a production WSGI server like Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## API Documentation

### Core Endpoints

#### Chat Endpoint
```
POST /chat
```

**Request:**
```json
{
  "message": "What are my marks in Math?",
  "role": "student",
  "student_id": 1
}
```

**Response:**
```json
{
  "reply": "Your score in Math is 95/100."
}
```

#### Health Check
```
GET /
```

Returns: `{"status": "ok", "message": "Smart School Chatbot Running"}`

### Admin Endpoints

- `POST /admin/login` - Admin authentication
- `GET /admin/students` - List all students
- `POST /admin/students` - Add new student
- `PUT /admin/students/{id}` - Update student
- `DELETE /admin/students/{id}` - Delete student
- `GET /admin/attendance` - Get attendance records
- `POST /admin/attendance` - Add attendance record
- `GET /admin/chat-history` - View chat history

Refer to `/docs` endpoint for complete API documentation.

## Database Schema

### Master Table
- `id` (Integer, PK): Student ID
- `name` (String): Student name

### Academics Table
- `id` (Integer, PK)
- `student_id` (Integer, FK): Reference to Master
- `subject` (String): Subject name
- `score` (Integer): Score obtained

### Attendance Table
- `id` (Integer, PK)
- `student_id` (Integer, FK): Reference to Master
- `date` (Date): Attendance date
- `status` (String): Present/Absent

### ChatHistory Table
- `id` (Integer, PK)
- `student_id` (Integer): Student ID (nullable)
- `role` (String): Student/Parent/Advisor
- `user_message` (Text): User's message
- `bot_reply` (Text): Bot's response
- `timestamp` (DateTime): When message was sent

## Features & How They Work

### Intent Recognition

The chatbot intelligently recognizes user intent and routes queries appropriately:

1. **Academic Intent** (`academic_intent.py`)
   - Detects queries about marks, scores, subjects
   - Fetches student academic data from database
   - Returns personalized academic information

2. **Attendance Intent** (`attendance_intent.py`)
   - Recognizes attendance-related queries
   - Supports date/month filtering
   - Provides attendance summaries

3. **Advisor Intent** (`advisor_intent.py`)
   - Handles requests for advisor information
   - School-related queries
   - Guidance and support information

### Safety & Security

- **Input Filtering** (`filters.py`): Validates and sanitizes user input
- **Guard Responses** (`llm_guard.py`): Blocks inappropriate requests
- **Admin Authentication** (`admin_auth.py`): JWT-based token validation
- **Data Privacy**: Students can only access their own information

### Chat Processing Pipeline

1. **User Input** → 
2. **Safety Filter Check** → 
3. **Intent Detection** → 
4. **Data Retrieval** (if needed) → 
5. **LLM Response Generation** → 
6. **Tone Application** → 
7. **Chat History Save** → 
8. **Response to User**

## Configuration

### LLM Configuration

The system supports:
- **Local Ollama**: Running models locally (recommended for privacy)
- **Remote LLM**: External LLM APIs
- **Custom Models**: Extensible LLM integration

To use Ollama:
```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull mistral

# Start Ollama service
ollama serve
```

Update `LLM_BASE_URL` in `.env` to point to your Ollama instance.

### Database Configuration

Supports multiple database backends through SQLAlchemy:
- SQLite (default): `sqlite:///./chat.db`
- PostgreSQL: `postgresql://user:password@localhost/dbname`
- MySQL: `mysql+pymysql://user:password@localhost/dbname`

## Development

### Backend Development
```bash
cd backend

# With auto-reload
uvicorn app.main:app --reload

# Run tests (if available)
pytest

# Code formatting
black app/

# Linting
flake8 app/
```

### Frontend Development
```bash
cd frontend

# Dev server with hot reload
npm run dev

# Build production bundle
npm run build

# Linting
npm run lint

# Preview production build
npm run preview
```

## Common Issues & Troubleshooting

### Backend Connection Issues
- Ensure backend is running on `http://localhost:8000`
- Check `VITE_API_BASE_URL` in frontend `.env`
- Verify CORS is enabled in backend

### Database Errors
- Check DATABASE_URL is correct in `.env`
- Ensure database file has write permissions
- Delete old `chat.db` and restart to reinitialize

### LLM/Ollama Issues
- Verify Ollama is running: `curl http://localhost:11434`
- Check LLM_BASE_URL and LLM_MODEL in `.env`
- Pull required model: `ollama pull <model-name>`

### Admin Login Issues
- Verify SECRET_KEY is set in `.env`
- Check admin credentials in database
- Clear browser cookies and retry

## Environment Variables Checklist

Backend (`.env` in `backend/`):
- [ ] `DATABASE_URL` - Database connection string
- [ ] `SECRET_KEY` - For JWT token generation
- [ ] `LLM_MODEL` - Language model name (if using local LLM)
- [ ] `LLM_BASE_URL` - LLM service endpoint (if applicable)

Frontend (`.env` in `frontend/`):
- [ ] `VITE_API_BASE_URL` - Backend API URL

## Performance Tips

1. **Database Optimization**
   - Add indexes on frequently queried columns
   - Use database connection pooling for production

2. **Frontend Optimization**
   - Use production build with `npm run build`
   - Enable gzip compression in server
   - Cache static assets with long TTL

3. **LLM Optimization**
   - Use smaller models for faster inference
   - Enable model quantization if available
   - Cache common responses

## Security Recommendations

- ✅ Use strong `SECRET_KEY` (32+ characters, random)
- ✅ Keep Python packages updated: `pip list --outdated`
- ✅ Use HTTPS in production
- ✅ Implement rate limiting for API endpoints
- ✅ Sanitize all user inputs (already done via filters)
- ✅ Use environment variables for sensitive data
- ✅ Enable CORS only for trusted origins in production
- ✅ Implement request signing for admin endpoints

## Deployment

### Using Docker

Create `Dockerfile` for backend:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t school-chatbot-backend .
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./chat.db school-chatbot-backend
```

### Cloud Deployment
- **Backend**: Heroku, Railway, AWS Lambda (with API Gateway), Google Cloud Run
- **Frontend**: Vercel, Netlify, GitHub Pages, AWS S3 + CloudFront

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push branch: `git push origin feature/your-feature`
4. Open a pull request

## Future Enhancements

- [ ] Voice-based chat interface
- [ ] Parent portal for student progress tracking
- [ ] Teacher dashboard for grade management
- [ ] Real-time notifications for announcements
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Mobile app (React Native)
- [ ] Integration with existing school management systems (ERP)

## License

This project is proprietary. Unauthorized copying or distribution is prohibited.

## Support & Contact

For issues, questions, or contributions:
- 📧 Email: [contact@school.com]
- 🐛 Issues: [GitHub Issues]
- 💬 Discussion: [GitHub Discussions]

---

**Version**: 4.6.2  
**Last Updated**: April 2026  
**Status**: Active Development
