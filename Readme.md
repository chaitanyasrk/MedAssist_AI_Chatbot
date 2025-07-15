
# 🏥 Medical Q&A Assistant

An AI-powered medical question-answering application built with **RAG (Retrieval-Augmented Generation)**, **Azure OpenAI**, **FastAPI**, and **React**. This system provides evidence-based medical information while maintaining strict safety protocols and evaluation metrics.

![Architecture](https://img.shields.io/badge/Architecture-Full%20Stack-blue) ![Backend](https://img.shields.io/badge/Backend-Python%20FastAPI-green) ![Frontend](https://img.shields.io/badge/Frontend-React%20TypeScript-blue) ![AI](https://img.shields.io/badge/AI-Azure%20OpenAI-purple)

## 🌟 Features

### 🤖 **AI-Powered Medical Assistance**
- **RAG Implementation** with medical knowledge base
- **Azure OpenAI GPT-4** integration for intelligent responses
- **Medical domain validation** - only answers healthcare questions
- **Context-aware responses** with source citations
- **Response quality evaluation** with multiple metrics

### 🛡️ **Safety & Security**
- **Medical safety guardrails** - no personal medical advice
- **Prompt injection protection** with NVIDIA Guardrails
- **Input validation** and sanitization
- **Rate limiting** and abuse prevention
- **Medical disclaimers** on all responses

### 📊 **Advanced Evaluation**
- **Multi-dimensional scoring**: Relevance, Accuracy, Completeness, Safety
- **Response time tracking**
- **Context utilization metrics**
- **Real-time evaluation display**

### 🎨 **Modern User Interface**
- **Responsive React UI** with TypeScript
- **Real-time chat interface** with message bubbles
- **Chat history management** with session persistence
- **Knowledge source display** with relevance scores
- **Mobile-optimized** design with collapsible sidebar

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌──────────────────┐
│                 │ ←──────────────→ │                  │
│   React UI      │                 │   FastAPI        │
│   (Port 3000)   │                 │   Backend        │
│                 │                 │   (Port 8000)    │
└─────────────────┘                 └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   Azure OpenAI   │
                                    │     GPT-4        │
                                    └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │  Medical Dataset │
                                    │ (MedMCQA/PubMed) │
                                    └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** with pip
- **Node.js 16+** with npm
- **Azure OpenAI** account and API keys
- **Git** for cloning the repository

### 1. Clone the Repository
```bash
git clone 
cd medical-qa-assistant
```

### 2. Backend Setup (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Start the API server
python main.py
```

**Backend will be available at: http://localhost:8000**

### 3. Frontend Setup (React)
```bash
# Navigate to frontend directory (in new terminal)
cd medical-qa-ui

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Update API_URL if needed

# Start the development server
npm start
```

**Frontend will be available at: http://localhost:3000**

## ⚙️ Configuration

### Backend Configuration (.env)
```bash
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Database
DATABASE_URL=sqlite:///./medical_qa.db

# Security
SECRET_KEY=your-secret-key-here

# Dataset
DATASET_NAME=medmcqa
TRAIN_SPLIT_RATIO=0.8
```

### Frontend Configuration (.env)
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# App Configuration
REACT_APP_APP_NAME=Medical Q&A Assistant
REACT_APP_VERSION=1.0.0
```

## 📚 API Documentation

### Core Endpoints

#### Chat Endpoints
- `POST /api/v1/chat/message` - Send a medical question
- `GET /api/v1/chat/history/{session_id}` - Get chat history
- `GET /api/v1/chat/sessions` - List chat sessions
- `DELETE /api/v1/chat/session/{session_id}` - Delete session

#### Evaluation Endpoints
- `POST /api/v1/evaluation/evaluate` - Evaluate single response
- `POST /api/v1/evaluation/batch-evaluate` - Batch evaluation
- `GET /api/v1/evaluation/stats` - Get evaluation statistics

#### Health Endpoints
- `GET /api/v1/health/` - Comprehensive health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### Example API Usage

**Send a Medical Question:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are the symptoms of diabetes?",
       "session_id": "session-123"
     }'
```

**Response:**
```json
{
  "message_id": 1,
  "session_id": "session-123",
  "response": "Diabetes symptoms include frequent urination, excessive thirst...",
  "evaluation_score": 0.87,
  "retrieved_context": [
    {
      "question": "What is diabetes?",
      "answer": "Diabetes is a metabolic disorder...",
      "similarity_score": 0.92
    }
  ],
  "response_time": 2.34,
  "is_medical": true,
  "query_type": "general"
}
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Run unit tests
pytest

# Run with coverage
pytest --cov=src

# Test specific module
pytest tests/test_api/test_chat.py
```

### Frontend Testing
```bash
cd medical-qa-ui

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Integration Testing
```bash
# Start both services
python backend/main.py &
npm start --prefix medical-qa-ui &

# Run integration tests
python backend/test_api.py
```

## 📊 Features Overview

### 🔍 **Intelligent Medical RAG**
- **Knowledge Retrieval**: Semantic search through medical datasets
- **Context Integration**: Combines retrieved knowledge with LLM generation
- **Source Citations**: Shows knowledge sources with relevance scores
- **Domain Filtering**: Only processes medical/healthcare questions

### 📈 **Response Evaluation**
- **Relevance Score**: How well the answer addresses the question
- **Accuracy Score**: Factual correctness compared to reference
- **Completeness Score**: Thoroughness of the explanation
- **Safety Score**: Adherence to medical safety guidelines
- **Overall Score**: Weighted combination of all metrics

### 🎯 **Safety Features**
- **Medical Validation**: Rejects non-medical questions
- **Personal Advice Blocking**: Prevents diagnostic recommendations
- **Guardrails Integration**: Advanced prompt injection protection
- **Medical Disclaimers**: Clear educational purpose statements
- **Emergency Detection**: Identifies and redirects emergency queries

### 💬 **Chat Interface**
- **Real-time Messaging**: Instant responses with loading indicators
- **Message History**: Persistent chat sessions with timestamps
- **Copy/Share**: Easy message copying and sharing
- **Mobile Responsive**: Touch-optimized for all devices
- **Keyboard Shortcuts**: Power-user navigation (Ctrl+N, Ctrl+B, etc.)

## 🔧 Development

### Project Structure
```
medical-qa-assistant/
├── backend/                    # FastAPI Backend
│   ├── src/
│   │   ├── api/               # API routes and models
│   │   ├── services/          # Business logic
│   │   ├── data/              # Data processing
│   │   ├── database/          # Database models
│   │   └── utils/             # Utilities and config
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── main.py               # FastAPI application
│
├── medical-qa-ui/             # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API services
│   │   └── utils/             # Utilities
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   └── tailwind.config.js     # Tailwind CSS config
│
└── README.md                  # This file
```

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: PyTorch, LangChain, Azure OpenAI
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Vector DB**: Chroma/FAISS for similarity search
- **Security**: NVIDIA Guardrails, input validation
- **Testing**: pytest, httpx

#### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: TailwindCSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React hooks + Context
- **Testing**: Jest, React Testing Library

### Code Quality
- **Type Safety**: TypeScript (Frontend), Type hints (Backend)
- **Linting**: ESLint (Frontend), flake8 (Backend)
- **Formatting**: Prettier (Frontend), Black (Backend)
- **Testing**: >90% test coverage for critical paths
- **Documentation**: Comprehensive API docs with OpenAPI

## 🚀 Deployment

### Docker Deployment

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
    
  frontend:
    build: ./medical-qa-ui
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### Production Deployment
1. **Environment Setup**: Configure production environment variables
2. **SSL/TLS**: Enable HTTPS with certificates
3. **Load Balancing**: Use nginx or cloud load balancers
4. **Monitoring**: Set up health checks and logging
5. **Scaling**: Configure horizontal scaling as needed

## 🔒 Security

### Security Features
- **HTTPS Enforcement**: All communication encrypted
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Prevents API abuse
- **CORS Configuration**: Controlled cross-origin access
- **Security Headers**: OWASP recommended headers
- **Prompt Injection Protection**: Advanced guardrails

### Data Privacy
- **No Personal Data Storage**: Chat history stored locally
- **Anonymized Logging**: No PII in application logs
- **Secure API Keys**: Environment-based configuration
- **Medical Compliance**: Designed for HIPAA-awareness

## 📈 Monitoring

### Health Checks
- **API Health**: `/api/v1/health/` endpoint
- **Database Status**: Connection and query health
- **AI Service Status**: Azure OpenAI connectivity
- **Performance Metrics**: Response times and throughput

### Logging
- **Structured Logging**: JSON formatted logs
- **Request Tracing**: Full request/response logging
- **Error Tracking**: Comprehensive error monitoring
- **Performance Metrics**: Response times and resource usage

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** changes with tests
4. **Run** quality checks (linting, testing)
5. **Submit** pull request with description

### Code Standards
- **Backend**: Follow PEP 8, type hints required
- **Frontend**: ESLint + Prettier, TypeScript strict mode
- **Testing**: Maintain >90% coverage for new features
- **Documentation**: Update README and API docs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Azure OpenAI** for providing GPT-4 API access
- **Hugging Face** for medical datasets (MedMCQA, PubMed QA)
- **LangChain** for RAG framework
- **FastAPI** for high-performance API framework
- **React** and **Tailwind CSS** for modern UI development

## 📞 Support

### Getting Help
- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions

### Troubleshooting

**Common Issues:**

1. **API Connection Failed**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/api/v1/health/
   
   # Verify Azure OpenAI credentials
   # Check .env file configuration
   ```

2. **CORS Errors**
   ```bash
   # Ensure proxy is set in package.json
   "proxy": "http://localhost:8000"
   ```

3. **Tailwind CSS Issues**
   ```bash
   # Reinstall Tailwind
   npm uninstall tailwindcss
   npm install -D tailwindcss@latest
   npx tailwindcss init -p
   ```

### Performance Optimization
- **Caching**: Implement response caching for common queries
- **Database**: Use PostgreSQL for production deployments
- **CDN**: Serve static assets via CDN
- **Compression**: Enable gzip/brotli compression

---

## 🎯 **Quick Start Summary**

1. **Clone repository**
2. **Setup backend**: `cd backend && pip install -r requirements.txt && python main.py`
3. **Setup frontend**: `cd medical-qa-ui && npm install && npm start`
4. **Configure Azure OpenAI** credentials in `.env`
5. **Access application** at http://localhost:3000

**🎉 You now have a production-ready Medical Q&A Assistant!**

For detailed setup instructions, troubleshooting, and advanced configuration, refer to the sections above.

---

**Built with ❤️ for healthcare education and AI safety**