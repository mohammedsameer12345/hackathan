# Intelligent Document Query System

A modern, AI-powered web application for processing and analyzing documents in insurance, legal, HR, and compliance domains. This system uses LLM technology to provide intelligent query responses with explainable decision rationale.

## 🚀 Features

### Core Capabilities
- **Multi-Format Document Support**: Process PDF, DOCX, and TXT files
- **Intelligent Query Processing**: Ask natural language questions about your documents
- **Semantic Search**: AI-powered content analysis and retrieval
- **Clause Extraction**: Identify and highlight relevant document sections
- **Confidence Scoring**: Get accuracy assessments for responses
- **Explainable AI**: Understand the reasoning behind each response

### Document Types Supported
- **Insurance Policies**: Coverage analysis, exclusions, claims processes
- **Legal Contracts**: Terms, conditions, obligations, compliance
- **HR Documents**: Employment agreements, policies, procedures
- **Compliance Documents**: Regulatory requirements, legal obligations

### Query Types
- **General Queries**: Broad questions about document content
- **Coverage Analysis**: Insurance coverage details and limits
- **Exclusions Check**: What's not covered or excluded
- **Claims Process**: Procedures and requirements for claims
- **Legal Compliance**: Regulatory and legal implications

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI/ML**: Perplexity API, Sentence Transformers
- **Document Processing**: PyMuPDF, python-docx
- **Deployment**: Gunicorn, Heroku/Railway ready

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Perplexity API key (optional - system works with mock responses)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/intelligent-document-query.git
cd intelligent-document-query
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables (Optional)
Create a `.env` file in the root directory:
```env
PERPLEXITY_API_KEY=your_perplexity_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

### 4. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📖 Usage Guide

### 1. Upload Documents
- Click the upload area or drag and drop files
- Supported formats: PDF, DOCX, TXT
- Maximum file size: 16MB
- The system will automatically process and analyze your document

### 2. Ask Questions
- Once your document is processed, the query section will appear
- Type your question in natural language
- Select the appropriate query type for better results
- Click "Get Answer" to receive AI-powered analysis

### 3. Review Results
- View the AI-generated answer
- Check relevant clauses with confidence scores
- Read the explanation for the analysis
- Download processed documents if needed

## 🔧 Configuration

### API Configuration
To use real AI responses instead of mock data:

1. Get a Perplexity API key from [Perplexity AI](https://www.perplexity.ai/)
2. Set the environment variable:
   ```bash
   export PERPLEXITY_API_KEY=your_api_key_here
   ```
3. Or add it to your `.env` file

### Customization
- Modify `app.py` to add new document types
- Update `perplexity_api.py` for different AI models
- Customize the UI in `templates/index.html`

## 🚀 Deployment

### Heroku Deployment
1. Create a `Procfile`:
   ```
   web: gunicorn app:app
   ```

2. Deploy to Heroku:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Docker Deployment
1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. Build and run:
   ```bash
   docker build -t document-query-system .
   docker run -p 5000:5000 document-query-system
   ```

## 📁 Project Structure

```
intelligent-document-query/
├── app.py                 # Main Flask application
├── perplexity_api.py      # AI API integration
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/
│   └── index.html        # Main web interface
├── uploads/              # Document storage (created automatically)
└── .env                  # Environment variables (create this)
```

## 🔍 API Endpoints

### Document Processing
- `POST /upload` - Upload and process documents
- `GET /download/<filename>` - Download processed documents

### Query Processing
- `POST /query` - Process natural language queries
- `POST /analyze` - Analyze document content

### System
- `GET /` - Main application interface
- `GET /health` - Health check endpoint

## 🧪 Testing

### Manual Testing
1. Upload a sample document (PDF, DOCX, or TXT)
2. Ask various types of questions
3. Verify responses and confidence scores
4. Test different query types

### Sample Test Cases
- "What is covered under this insurance policy?"
- "What are the exclusions in this document?"
- "How do I file a claim?"
- "What are the legal obligations?"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Perplexity AI](https://www.perplexity.ai/) for AI capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Email: your-email@example.com
- Documentation: [Wiki](https://github.com/yourusername/intelligent-document-query/wiki)

## 🔄 Version History

- **v1.0.0** - Initial release with basic document processing and query capabilities
- **v1.1.0** - Added confidence scoring and clause extraction
- **v1.2.0** - Enhanced UI and improved error handling

---

**Note**: This system is designed for educational and demonstration purposes. For production use, ensure proper security measures, data privacy compliance, and robust error handling. 