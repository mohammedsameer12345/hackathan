# 🛠️ Insurance Policy Analysis System - Deployment Guide

This guide will help you deploy the Insurance Policy Analysis System to various platforms.

---

## 🚀 Local Development

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

#### Install Dependencies
```bash
pip install Flask PyMuPDF python-docx requests sentence-transformers faiss-cpu numpy python-dotenv openai
```

#### Set Up Environment Variables
Create a `.env` file in the root directory with the following content:
```
GROQ_API_KEY=your_groq_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
TEAM_BEARER_TOKEN=your_team_bearer_token_here
```

#### Run the Application
```bash
# On Windows
run_app.bat

# Or directly
python app.py

# On Linux/Mac
python3 app.py
```

#### Access the Application
Open your browser and go to: [http://localhost:5000](http://localhost:5000)

---

## 🌐 Heroku Deployment

### 1. Install Heroku CLI
[Install Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

### 2. Prepare Your Application
Ensure your repo contains:
- `app.py`
- `requirements.txt`
- `Procfile`
- `templates/index.html`
- `document_analyzer.py`
- `groq_api.py`

### 3. Create `requirements.txt`
```txt
Flask==2.3.3
PyMuPDF==1.23.8
python-docx==0.8.11
requests==2.31.0
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.3
python-dotenv==1.0.0
openai==1.3.8
gunicorn==21.2.0
```

### 4. Create `Procfile`
```
web: gunicorn --bind 0.0.0.0:$PORT app:app
```

### 5. Deploy to Heroku
```bash
heroku login
heroku create your-app-name
git add .
git commit -m "Initial deployment"
git push heroku main
heroku open
```

### 6. Set Environment Variables
```bash
heroku config:set GROQ_API_KEY=your_groq_api_key_here
heroku config:set FLASK_SECRET_KEY=your_secret_key_here
heroku config:set TEAM_BEARER_TOKEN=your_team_bearer_token_here
```

---

## 🚂 Railway Deployment

1. Go to [Railway.app](https://railway.app) and connect your GitHub repo.
2. Configure Environment Variables:
   - `GROQ_API_KEY`
   - `FLASK_SECRET_KEY`
   - `TEAM_BEARER_TOKEN`
3. Railway auto-deploys your app and provides a public URL.

---

## 🐳 Docker Deployment

### 1. Create `Dockerfile`
```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### 2. Build and Run
```bash
docker build -t insurance-policy-system .
docker run -p 5000:5000 \
  -e GROQ_API_KEY=your_groq_api_key_here \
  -e FLASK_SECRET_KEY=your_secret_key_here \
  -e TEAM_BEARER_TOKEN=your_team_bearer_token_here \
  insurance-policy-system
```

### 3. Docker Compose (Optional)
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - GROQ_API_KEY=${GROQ_API_KEY}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - TEAM_BEARER_TOKEN=${TEAM_BEARER_TOKEN}
    volumes:
      - ./uploads:/app/uploads
```

```bash
docker-compose up -d
```

---

## ☁️ Google Cloud Platform (GCP)

### 1. Install and Init SDK
```bash
gcloud init
gcloud config set project YOUR_PROJECT_ID
```

### 2. Create `app.yaml`
```yaml
runtime: python39
entrypoint: gunicorn -b :$PORT app:app
env_variables:
  FLASK_ENV: production
  GROQ_API_KEY: "your_groq_api_key_here"
  FLASK_SECRET_KEY: "your_secret_key_here"
  TEAM_BEARER_TOKEN: "your_team_bearer_token_here"
```

### 3. Deploy and Access
```bash
gcloud app deploy
gcloud app browse
```

---

## 🔧 Environment Variables

### Required
- `GROQ_API_KEY`
- `FLASK_SECRET_KEY`
- `TEAM_BEARER_TOKEN`

### Optional
- `FLASK_ENV=production`
- `MAX_FILE_SIZE` (default 16MB)

---

## 📊 Monitoring and Logs

### Logs
```bash
# Heroku
heroku logs --tail

# Docker
docker logs container_name
```

### Health Check
```
GET /health
Returns: JSON with status, timestamp, and version
```

---

## 🔒 Security Considerations

- Use strong `FLASK_SECRET_KEY`
- Enable HTTPS
- Limit file size uploads
- Use `.env` to store API keys
- Never commit secrets to version control

---

## 📋 Query Types Supported

- **General Queries**
- **Coverage Details**
- **Exclusions**
- **Claims Process**
- **Premium Info**
- **Policy Duration**
- **Terms & Conditions**
- **Policy Definitions**

### ⚡ Zero-Token Queries
Used for fast answers from structured data before using AI tokens.

---

## 🆘 Troubleshooting

### Common Issues
- **Port in Use**: Kill the conflicting process
- **Version Mismatch**: Use Python 3.8+
- **Vector DB Errors**: Ensure `/uploads/vector_db` exists

---

## 📈 Performance & Scaling

- Use **Gunicorn** in production
- Enable caching/CDNs
- Horizontal scaling and load balancing
