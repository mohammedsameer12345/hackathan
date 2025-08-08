from fileinput import filename
from typing import Dict, List
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
import time
import math
from functools import wraps
from document_analyzer import DocumentAnalyzer
import logging
import numpy as np
from sentence_transformers import SentenceTransformer, util
import faiss
import pickle

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b97176f45315f8b8619a91bcd13888339bfe7f7993767f98764cf5e21fc9192f'
app.config['UPLOAD_FOLDER'] = 'Uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['VECTOR_DB_PATH'] = os.path.join(app.config['UPLOAD_FOLDER'], 'vector_db')

# Ensure upload and vector DB directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VECTOR_DB_PATH'], exist_ok=True)

# Load TEAM_BEARER_TOKEN from environment
TEAM_BEARER_TOKEN = os.getenv("TEAM_BEARER_TOKEN")
if not TEAM_BEARER_TOKEN:
    logger.error("TEAM_BEARER_TOKEN not set in environment")
    raise ValueError("TEAM_BEARER_TOKEN environment variable is required")

# Initialize Groq API client, DocumentAnalyzer, and embedding model
groq_client = GroqAPI()
document_analyzer = DocumentAnalyzer()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def estimate_tokens(text):
    """Estimate token count (approximate: 1 token ~ 4 chars in English text)"""
    return len(text) // 4

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
    
    document_type = "General Document"
    
    # Enhanced insurance policy detection with more keywords
    insurance_keywords = [
        'insurance', 'policy', 'coverage', 'premium', 'sum insured', 'policy period',
        'policyholder', 'insured', 'claim', 'exclusion', 'waiting period', 'grace period',
        'cumulative bonus', 'portability', 'renewal', 'deductible', 'co-payment'
    ]
    
    # Count how many insurance keywords appear in the document
    insurance_keyword_count = sum(1 for keyword in insurance_keywords if keyword in text_lower)
    
    # If we have at least 3 insurance keywords, classify as insurance policy
    if insurance_keyword_count >= 3:
        document_type = "Insurance Policy"
    elif any(keyword in text_lower for keyword in ['contract', 'agreement', 'terms', 'conditions']):
        document_type = "Legal Contract"
    elif any(keyword in text_lower for keyword in ['employment', 'hr', 'human resources', 'employee']):
        document_type = "HR Document"
    elif any(keyword in text_lower for keyword in ['compliance', 'regulation', 'regulatory', 'legal']):
        document_type = "Compliance Document"
    
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

def split_document(text, chunk_size=300):
    """Split the document into chunks of specified size."""
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def create_vector_index(chunks, filename):
    """Create and save FAISS index for document chunks."""
    embeddings = embedding_model.encode(chunks, convert_to_tensor=False)
    embeddings = np.array(embeddings, dtype='float32')
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    vector_db_path = os.path.join(app.config['VECTOR_DB_PATH'], f"{filename}.faiss")
    chunks_path = os.path.join(app.config['VECTOR_DB_PATH'], f"{filename}_chunks.pkl")
    faiss.write_index(index, vector_db_path)
    with open(chunks_path, 'wb') as f:
        pickle.dump(chunks, f)
    
    logger.debug(f"Created FAISS index for {filename}, {len(chunks)} chunks")
    return vector_db_path, chunks_path

def retrieve_relevant_chunks(query, filename, max_tokens=1500, top_k=3):
    """Retrieve top-k relevant chunks from FAISS index."""
    vector_db_path = os.path.join(app.config['VECTOR_DB_PATH'], f"{filename}.faiss")
    chunks_path = os.path.join(app.config['VECTOR_DB_PATH'], f"{filename}_chunks.pkl")
    
    if not os.path.exists(vector_db_path) or not os.path.exists(chunks_path):
        logger.error(f"Vector DB or chunks not found for {filename}")
        return []
    
    index = faiss.read_index(vector_db_path)
    with open(chunks_path, 'rb') as f:
        chunks = pickle.load(f)
        
    # Check if index has any vectors
    if index.ntotal == 0:
        logger.error(f"FAISS index is empty for {filename}")
        return []
        
    # Encode query and reshape to 2D array
    query_embedding = embedding_model.encode(query, convert_to_tensor=False).astype('float32')
    query_embedding = query_embedding.reshape(1, -1)  # Reshape to (1, embedding_dim)
    
    distances, indices = index.search(query_embedding, top_k)
    
    relevant_chunks = []
    total_tokens = 0
    for idx in indices[0]:
        if idx < len(chunks):
            chunk = chunks[idx]
            chunk_tokens = estimate_tokens(chunk)
            if total_tokens + chunk_tokens <= max_tokens:
                relevant_chunks.append(chunk)
                total_tokens += chunk_tokens
            else:
                remaining_tokens = max_tokens - total_tokens
                chars_to_keep = remaining_tokens * 4
                truncated_chunk = chunk[:chars_to_keep]
                if truncated_chunk:
                    relevant_chunks.append(truncated_chunk)
                break
    
    logger.debug(f"Retrieved {len(relevant_chunks)} chunks for query '{query}', total tokens: {total_tokens}, distances: {distances[0].tolist()}")
    return relevant_chunks

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Retry a function with exponential backoff."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if 'rate_limit_exceeded' in str(e) and attempt < max_retries - 1:
                    retry_time = 10
                    match = re.search(r'Please try again in ([\d.]+)s', str(e))
                    if match:
                        retry_time = float(match.group(1))
                    delay = base_delay * (2 ** attempt) + retry_time
                    logger.debug(f"Rate limit hit, retrying after {delay}s")
                    time.sleep(delay)
                    continue
                raise e
        raise Exception("Max retries reached")
    return wrapper

def try_structured_extraction(query, analysis, document_type, query_type):
    """Attempt to answer query using structured extraction from DocumentAnalyzer."""
    logger.debug(f"Attempting structured extraction for query: {query}, document_type: {document_type}, query_type: {query_type}")
    
    if document_type == "Insurance Policy":
        query_lower = query.lower()
        
        # Duration queries - only check relevant sections
        if query_type == "duration" or any(keyword in query_lower for keyword in ["duration", "period", "term", "policy term", "policy period", "length", "how long"]):
            # Define duration pattern to look for actual time periods
            duration_pattern = r'(\d+)\s*(year|years|month|months|day|days)'
            
            # Only check sections that are likely to contain duration information
            duration_sections = [
                ("key_terms", analysis.get("key_terms", [])),
                ("terms_conditions", analysis.get("terms_conditions", [])),
                ("definitions", analysis.get("definitions", []))
            ]
            
            for section_name, section_content in duration_sections:
                for term in section_content:
                    term_lower = term.lower()
                    # Check if the term contains duration keywords AND has a duration pattern
                    if any(keyword in term_lower for keyword in ["duration", "period", "term", "policy term", "policy period"]):
                        # Look for actual duration values
                        match = re.search(duration_pattern, term_lower)
                        if match:
                            logger.debug(f"Found duration with pattern in {section_name}: {term}")
                            return {"answer": term, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
            
            # If no term with duration pattern found, try to find any term that has the keyword
            for section_name, section_content in duration_sections:
                for term in section_content:
                    term_lower = term.lower()
                    if any(keyword in term_lower for keyword in ["duration", "period", "term", "policy term", "policy period"]):
                        logger.debug(f"Found duration keyword in {section_name} (without pattern): {term}")
                        return {"answer": term, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
        
        # Coverage queries - only check coverage section
        elif query_type == "coverage" or any(keyword in query_lower for keyword in ["coverage", "covered", "protection", "benefits"]):
            coverage_details = analysis.get("coverage_details", [])
            if coverage_details:
                # Look for terms that actually mention coverage
                for detail in coverage_details:
                    detail_lower = detail.lower()
                    if any(keyword in detail_lower for keyword in ["coverage", "covered", "benefits", "included"]):
                        logger.debug(f"Found relevant coverage detail: {detail}")
                        return {"answer": detail, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
        
        # Exclusion queries - only check exclusions section
        elif query_type == "exclusions" or any(keyword in query_lower for keyword in ["exclusion", "excluded", "not covered"]):
            exclusions = analysis.get("exclusions", [])
            if exclusions:
                # Look for terms that actually mention exclusions
                for exclusion in exclusions:
                    exclusion_lower = exclusion.lower()
                    if any(keyword in exclusion_lower for keyword in ["exclusion", "excluded", "not covered", "limitation"]):
                        logger.debug(f"Found relevant exclusion: {exclusion}")
                        return {"answer": exclusion, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
        
        # Claims process queries - only check claims section
        elif query_type == "claims" or any(keyword in query_lower for keyword in ["claim", "file a claim", "claims process", "how to claim"]):
            claims_process = analysis.get("claims_process", [])
            if claims_process:
                # Look for terms that actually mention claims
                for claim in claims_process:
                    claim_lower = claim.lower()
                    if any(keyword in claim_lower for keyword in ["claim", "claims", "file", "process", "procedure"]):
                        logger.debug(f"Found relevant claims process: {claim}")
                        return {"answer": claim, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
        
        # Premium queries - only check premium section
        elif query_type == "premium" or any(keyword in query_lower for keyword in ["premium", "cost", "price", "payment", "fee"]):
            premium_info = analysis.get("premium_info", [])
            if premium_info:
                # Look for terms that actually mention premium
                premium_lower = premium_info.lower()
                if any(keyword in premium_lower for keyword in ["premium", "cost", "price", "payment", "fee"]):
                    logger.debug(f"Found relevant premium info: {premium_info}")
                    return {"answer": premium_info, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
        
        # Terms & Conditions queries - only check terms section
        elif query_type == "terms" or any(keyword in query_lower for keyword in ["terms", "conditions", "terms and conditions"]):
            terms_conditions = analysis.get("terms_conditions", [])
            if terms_conditions:
                # Look for terms that actually mention terms and conditions
                for term in terms_conditions:
                    term_lower = term.lower()
                    if any(keyword in term_lower for keyword in ["terms", "conditions", "provision", "clause"]):
                        logger.debug(f"Found relevant terms and conditions: {term}")
                        return {"answer": term, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
        
        # Definitions queries - only check definitions section
        elif query_type == "definitions" or any(keyword in query_lower for keyword in ["definition", "define", "meaning"]):
            definitions = analysis.get("definitions", [])
            if definitions:
                # Look for terms that actually contain definitions
                for definition in definitions:
                    definition_lower = definition.lower()
                    if any(keyword in definition_lower for keyword in ["definition", "defined as", "means", "refers to"]):
                        logger.debug(f"Found relevant definition: {definition}")
                        return {"answer": definition, "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}
    
    logger.debug("No structured answer found, falling back to RAG")
    return None

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
        
        document_text = process_document(file_path)
        chunks = split_document(document_text)
        vector_db_path, chunks_path = create_vector_index(chunks, filename)
        
        # Get detailed analysis from document_analyzer
        detailed_analysis = document_analyzer.analyze_document(document_text)
        
        # Get simple analysis with improved document type detection
        simple_analysis = analyze_document_content(document_text)
        
        # If detailed analysis classified as Resume/CV but simple analysis says Insurance Policy,
        # override the document type in detailed_analysis
        if detailed_analysis.get('document_type') == 'Resume/CV' and simple_analysis.get('document_type') == 'Insurance Policy':
            detailed_analysis['document_type'] = 'Insurance Policy'
            logger.debug("Overrode document type from Resume/CV to Insurance Policy")
        
        logger.debug(f"Detailed analysis: {detailed_analysis}")
        logger.debug(f"Simple analysis: {simple_analysis}")
        
        document_info = {
            'filename': filename,
            'original_name': file.filename,
            'text': document_text,
            'upload_time': datetime.now().isoformat(),
            'file_size': os.path.getsize(file_path),
            'analysis': simple_analysis,
            'detailed_analysis': detailed_analysis,
            'vector_db_path': vector_db_path,
            'chunks_path': chunks_path
        }
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'document': document_info
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/query', methods=['POST'])
@retry_with_backoff
def process_query():
    data = request.get_json()
    query = data.get('query', '')
    document_text = data.get('document_text', '')
    query_type = data.get('query_type', 'general')
    detailed_analysis = data.get('detailed_analysis', {})
    filename = data.get('filename', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    if not document_text or not filename:
        return jsonify({'error': 'No document text or filename provided'}), 400
    
    # Try structured extraction first
    document_type = detailed_analysis.get('document_type', 'General Document')
    result = try_structured_extraction(query, detailed_analysis, document_type, query_type)
    if result:
        logger.debug(f"Structured extraction succeeded for query: {query}")
        return jsonify(result)
    
    # Fall back to RAG if structured extraction fails
    relevant_chunks = retrieve_relevant_chunks(query, filename, max_tokens=1500, top_k=3)
    context = "\n".join(relevant_chunks)
    result = groq_client.query_document(query, context, query_type)
    
    logger.debug(f"RAG pipeline used, tokens: {result['token_usage']['total_tokens']}")
    return jsonify(result)

@app.route('/analyze', methods=['POST'])
def analyze_document():
    data = request.get_json()
    document_text = data.get('document_text', '')
    
    if not document_text:
        return jsonify({'error': 'No document text provided'}), 400
    
    simple_analysis = analyze_document_content(document_text)
    detailed_analysis = document_analyzer.analyze_document(document_text)
    
    # If detailed analysis classified as Resume/CV but simple analysis says Insurance Policy,
    # override the document type in detailed_analysis
    if detailed_analysis.get('document_type') == 'Resume/CV' and simple_analysis.get('document_type') == 'Insurance Policy':
        detailed_analysis['document_type'] = 'Insurance Policy'
        logger.debug("Overrode document type from Resume/CV to Insurance Policy")
    
    return jsonify({
        'simple_analysis': simple_analysis,
        'detailed_analysis': detailed_analysis
    })

@app.route('/hackrx/run', methods=['POST'])
@retry_with_backoff
def hackrx_run():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid authorization header"}), 401
    
    token = auth_header.split(" ")[1]
    if token != TEAM_BEARER_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    document_url = data.get("documents")
    questions = data.get("questions", [])
    
    if not document_url or not questions:
        return jsonify({"error": "Missing documents or questions"}), 400
    
    try:
        response = requests.get(document_url)
        if response.status_code != 200:
            return jsonify({"error": "Unable to fetch document"}), 400
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_temp_doc.pdf"
        temp_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(temp_filename, 'wb') as f:
            f.write(response.content)
        
        document_text = extract_text_from_pdf(temp_filename)
        chunks = split_document(document_text)
        create_vector_index(chunks, filename)
        
        detailed_analysis = document_analyzer.analyze_document(document_text)
        
        # If detailed analysis classified as Resume/CV but simple analysis says Insurance Policy,
        # override the document type in detailed_analysis
        simple_analysis = analyze_document_content(document_text)
        if detailed_analysis.get('document_type') == 'Resume/CV' and simple_analysis.get('document_type') == 'Insurance Policy':
            detailed_analysis['document_type'] = 'Insurance Policy'
            logger.debug("Overrode document type from Resume/CV to Insurance Policy")
        
        answers = []
        for question in questions:
            # Try structured extraction first
            document_type = detailed_analysis.get('document_type', 'General Document')
            result = try_structured_extraction(question, detailed_analysis, document_type, "hackathon")
            if result:
                answers.append(result["answer"])
                continue
            
            # Fall back to RAG if structured extraction fails
            relevant_chunks = retrieve_relevant_chunks(question, filename, max_tokens=1500, top_k=3)
            context = "\n".join(relevant_chunks)
            result = groq_client.query_document(question, context, query_type="hackathon")
            answer = result.get("answer", "No answer returned")
            answers.append(answer)
        
        return jsonify({"answers": answers})
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

@app.route('/download/<filename>')
def download_file():
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