from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
import fitz  # PyMuPDF
from docx import Document
import re
from datetime import datetime
import requests
from io import BytesIO
import base64
from groq_api import GroqAPI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

TEAM_BEARER_TOKEN = os.getenv("TEAM_BEARER_TOKEN")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != TEAM_BEARER_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or missing authorization token")
    return True

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Groq API client
groq_client = GroqAPI()


# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return "Error extracting text from PDF: " + str(e)

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return "Error extracting text from DOCX: " + str(e)

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return "Error extracting text from TXT: " + str(e)

def process_document(file_path):
    """Process document and extract text based on file type"""
    file_extension = file_path.rsplit('.', 1)[1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == 'docx':
        return extract_text_from_docx(file_path)
    elif file_extension == 'txt':
        return extract_text_from_txt(file_path)
    else:
        return "Unsupported file format"

def analyze_document_content(document_text):
    """Analyze document content to determine type and extract key information"""
    text_lower = document_text.lower()
    
    # Determine document type based on content
    document_type = "General Document"
    if any(keyword in text_lower for keyword in ['insurance', 'policy', 'coverage', 'premium']):
        document_type = "Insurance Policy"
    elif any(keyword in text_lower for keyword in ['contract', 'agreement', 'terms', 'conditions']):
        document_type = "Legal Contract"
    elif any(keyword in text_lower for keyword in ['employment', 'hr', 'human resources', 'employee']):
        document_type = "HR Document"
    elif any(keyword in text_lower for keyword in ['compliance', 'regulation', 'regulatory', 'legal']):
        document_type = "Compliance Document"
    
    # Extract key sections (simplified approach)
    key_sections = []
    if 'coverage' in text_lower:
        key_sections.append('Coverage Details')
    if 'exclusion' in text_lower:
        key_sections.append('Exclusions')
    if 'claim' in text_lower:
        key_sections.append('Claims Process')
    if 'term' in text_lower:
        key_sections.append('Terms and Conditions')
    if 'liability' in text_lower:
        key_sections.append('Liability')
    
    return {
        'document_type': document_type,
        'key_sections': key_sections,
        'word_count': len(document_text.split()),
        'estimated_pages': len(document_text) // 500,
        'summary': "This appears to be a " + document_type.lower() + " containing " + str(len(key_sections)) + " main sections."
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = timestamp + "_" + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the document
        document_text = process_document(file_path)
        
        # Analyze document content
        analysis = analyze_document_content(document_text)
        
        # Store document info
        document_info = {
            'filename': filename,
            'original_name': file.filename,
            'text': document_text,
            'upload_time': datetime.now().isoformat(),
            'file_size': os.path.getsize(file_path),
            'analysis': analysis
        }
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'document': document_info
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/query', methods=['POST'])
def process_query():
    data = request.get_json()
    query = data.get('query', '')
    document_text = data.get('document_text', '')
    query_type = data.get('query_type', 'general')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    if not document_text:
        return jsonify({'error': 'No document text provided'}), 400
    
    # Process the query using the Groq API
    result = groq_client.query_document(query, document_text, query_type)
    
    return jsonify(result)

@app.route('/analyze', methods=['POST'])
def analyze_document():
    data = request.get_json()
    document_text = data.get('document_text', '')
    
    if not document_text:
        return jsonify({'error': 'No document text provided'}), 400
    
    # Analyze document structure and extract key information
    analysis = analyze_document_content(document_text)
    
    return jsonify(analysis)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/health')
def health_check():
    """Health check endpoint for deployment"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 