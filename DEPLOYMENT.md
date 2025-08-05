# Deployment Guide

This guide will help you deploy the Intelligent Document Query System to various platforms.

## 🚀 Local Development

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start
1. **Install Dependencies**
   ```bash
   pip install Flask PyMuPDF python-docx requests
   ```

2. **Run the Application**
   ```bash
   # On Windows (use the batch file)
   run_app.bat
   
   # Or directly with Python 3
   C:\Users\salma\AppData\Local\Programs\Python\Python312\python.exe app.py
   
   # On Linux/Mac
   python3 app.py
   ```

3. **Access the Application**
   - Open your browser and go to: `http://localhost:5000`
   - The application will be ready to use!

## 🌐 Heroku Deployment

### 1. Install Heroku CLI
Download and install from: https://devcenter.heroku.com/articles/heroku-cli

### 2. Prepare Your Application
Make sure you have these files in your repository:
- `app.py` - Main application
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku configuration
- `templates/index.html` - Web interface

### 3. Deploy to Heroku
```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Add your files to git
git add .
git commit -m "Initial deployment"

# Deploy to Heroku
git push heroku main

# Open your app
heroku open
```

### 4. Set Environment Variables (Optional)
```bash
# Set your Perplexity API key (optional)
heroku config:set PERPLEXITY_API_KEY=your_api_key_here

# Set Flask secret key
heroku config:set FLASK_SECRET_KEY=your_secret_key_here
```

## 🚂 Railway Deployment

### 1. Connect to Railway
1. Go to [Railway.app](https://railway.app/)
2. Sign up/Login with your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"

### 2. Configure Your Project
1. Select your repository
2. Railway will automatically detect it's a Python app
3. Set environment variables in the Railway dashboard:
   - `PERPLEXITY_API_KEY` (optional)
   - `FLASK_SECRET_KEY`

### 3. Deploy
Railway will automatically deploy your application and provide you with a URL.

## 🐳 Docker Deployment

### 1. Build the Docker Image
```bash
docker build -t document-query-system .
```

### 2. Run the Container
```bash
docker run -p 5000:5000 document-query-system
```

### 3. Access the Application
Open your browser and go to: `http://localhost:5000`

### 4. Docker Compose (Optional)
Create a `docker-compose.yml` file:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
    volumes:
      - ./uploads:/app/uploads
```

Then run:
```bash
docker-compose up -d
```

## ☁️ Google Cloud Platform (GCP)

### 1. Install Google Cloud SDK
Download from: https://cloud.google.com/sdk/docs/install

### 2. Initialize Your Project
```bash
gcloud init
gcloud config set project YOUR_PROJECT_ID
```

### 3. Deploy to App Engine
```bash
# Create app.yaml file
echo "runtime: python39
entrypoint: gunicorn -b :$PORT app:app" > app.yaml

# Deploy
gcloud app deploy
```

### 4. Access Your App
```bash
gcloud app browse
```

## 🔧 Environment Variables

### Required Variables
- `FLASK_SECRET_KEY` - Secret key for Flask sessions

### Optional Variables
- `PERPLEXITY_API_KEY` - API key for Perplexity AI (for real AI responses)
- `FLASK_ENV` - Set to 'production' for production deployment
- `MAX_FILE_SIZE` - Maximum file upload size (default: 16MB)

### Setting Environment Variables

#### Local Development
Create a `.env` file:
```env
FLASK_SECRET_KEY=your_secret_key_here
PERPLEXITY_API_KEY=your_api_key_here
FLASK_ENV=development
```

#### Production Deployment
Set environment variables in your deployment platform:
- **Heroku**: `heroku config:set VARIABLE_NAME=value`
- **Railway**: Use the Railway dashboard
- **Docker**: Use `-e` flag or docker-compose environment section

## 📊 Monitoring and Logs

### View Logs
```bash
# Heroku
heroku logs --tail

# Railway
# Use the Railway dashboard

# Docker
docker logs container_name

# Local
# Logs will appear in the terminal
```

### Health Check
All deployments include a health check endpoint:
- URL: `https://your-app-url/health`
- Returns: JSON with status, timestamp, and version

## 🔒 Security Considerations

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Use a strong `FLASK_SECRET_KEY`
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Set up proper file upload limits
- [ ] Configure CORS if needed
- [ ] Set up monitoring and logging

### API Key Security
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Monitor API usage

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 PID  # Linux/Mac
taskkill /PID PID /F  # Windows
```

#### 2. Python Version Issues
```bash
# Check Python version
python --version

# Use specific Python version
python3 app.py
```

#### 3. Missing Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install Flask PyMuPDF python-docx requests
```

#### 4. Permission Issues
```bash
# Make sure uploads directory exists
mkdir uploads

# Set proper permissions
chmod 755 uploads  # Linux/Mac
```

### Getting Help
- Check the logs for error messages
- Verify all dependencies are installed
- Ensure environment variables are set correctly
- Test locally before deploying

## 📈 Performance Optimization

### For Production
1. **Use Gunicorn** (already configured)
2. **Enable Caching** (Redis/Memcached)
3. **Use CDN** for static files
4. **Optimize Database** (if using one)
5. **Monitor Resource Usage**

### Scaling
- **Horizontal Scaling**: Deploy multiple instances
- **Load Balancing**: Use platform load balancers
- **Auto-scaling**: Configure based on traffic

---

**Note**: This deployment guide covers the most common platforms. For specific platform requirements, refer to their official documentation. 