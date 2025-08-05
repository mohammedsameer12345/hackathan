import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class PerplexityAPI:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Perplexity API client
        
        Args:
            api_key: Perplexity API key. If not provided, will try to get from environment
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def query_document(self, query: str, document_text: str, query_type: str = "general") -> Dict:
        """
        Query the Perplexity API with document context
        
        Args:
            query: User's question
            document_text: Document content to analyze
            query_type: Type of query (general, coverage, exclusions, claims, legal)
            
        Returns:
            Dictionary containing the API response
        """
        if not self.api_key:
            return self._get_mock_response(query, document_text, query_type)
        
        try:
            # Create system prompt based on query type
            system_prompt = self._create_system_prompt(query_type, document_text)
            
            payload = {
                "model": "sonar-medium-online",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.1,
                "top_p": 0.9
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return self._process_api_response(response.json(), query, document_text)
            else:
                return self._handle_api_error(response.status_code, response.text)
                
        except requests.exceptions.RequestException as e:
            return self._handle_request_error(str(e))
        except Exception as e:
            return self._handle_general_error(str(e))
    
    def _create_system_prompt(self, query_type: str, document_text: str) -> str:
        """Create a specialized system prompt based on query type"""
        base_prompt = f"""You are an intelligent document analysis assistant specializing in insurance, legal, HR, and compliance documents. 

Document Context: {document_text[:8000]}  # Limit context length

Your task is to:
1. Analyze the provided document context
2. Answer the user's question accurately and comprehensively
3. Identify relevant clauses and sections
4. Provide confidence scores for your analysis
5. Explain your reasoning

Query Type: {query_type}

Please structure your response to include:
- Direct answer to the question
- Relevant clauses with section names
- Confidence score (0-1)
- Explanation of your analysis
- Any important caveats or limitations

Focus on providing actionable insights and clear explanations."""
        
        # Add specific instructions based on query type
        if query_type == "coverage":
            base_prompt += "\n\nFocus on coverage details, limits, and what is included in the policy."
        elif query_type == "exclusions":
            base_prompt += "\n\nPay special attention to exclusions, limitations, and what is NOT covered."
        elif query_type == "claims":
            base_prompt += "\n\nFocus on claims procedures, requirements, and processes."
        elif query_type == "legal":
            base_prompt += "\n\nEmphasize legal compliance, regulatory requirements, and legal implications."
        
        return base_prompt
    
    def _process_api_response(self, response_data: Dict, query: str, document_text: str) -> Dict:
        """Process the API response and extract relevant information"""
        try:
            content = response_data['choices'][0]['message']['content']
            
            # Parse the response to extract structured information
            result = self._parse_llm_response(content, query)
            
            # Add metadata
            result.update({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'model_used': response_data.get('model', 'sonar-medium-online'),
                'usage': response_data.get('usage', {})
            })
            
            return result
            
        except (KeyError, IndexError) as e:
            return self._handle_parsing_error(str(e), content)
    
    def _parse_llm_response(self, content: str, query: str) -> Dict:
        """Parse the LLM response to extract structured information"""
        # This is a simplified parser - in production, you might want more sophisticated parsing
        try:
            # Try to extract clauses (look for patterns like "Section:" or "Clause:")
            clauses = []
            lines = content.split('\n')
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['section:', 'clause:', 'article:', 'paragraph:']):
                    # Extract section name and content
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        section = parts[0].strip()
                        clause_text = parts[1].strip()
                        if clause_text:
                            clauses.append({
                                'section': section,
                                'clause': clause_text,
                                'relevance_score': 0.85  # Default score
                            })
            
            # Extract confidence score (look for patterns like "confidence: 0.9" or "95%")
            confidence_score = 0.8  # Default
            confidence_patterns = [
                r'confidence:\s*(\d+\.?\d*)',
                r'(\d+)%\s*confidence',
                r'confidence\s*score:\s*(\d+\.?\d*)'
            ]
            
            import re
            for pattern in confidence_patterns:
                match = re.search(pattern, content.lower())
                if match:
                    score = float(match.group(1))
                    if score <= 1.0:
                        confidence_score = score
                    else:
                        confidence_score = score / 100
                    break
            
            return {
                'answer': content,
                'clauses': clauses[:5],  # Limit to top 5 clauses
                'confidence_score': confidence_score,
                'explanation': f"Analysis based on semantic matching of query '{query}' with document content. Identified {len(clauses)} relevant clauses."
            }
            
        except Exception as e:
            return {
                'answer': content,
                'clauses': [],
                'confidence_score': 0.7,
                'explanation': f"Parsed response with basic analysis. Error in detailed parsing: {str(e)}"
            }
    
    def _get_mock_response(self, query: str, document_text: str, query_type: str) -> Dict:
        """Generate a mock response when API key is not available"""
        mock_clauses = [
            {
                "section": "Policy Coverage",
                "clause": "This policy provides comprehensive coverage for medical expenses up to the specified limit",
                "relevance_score": 0.95
            },
            {
                "section": "Exclusions",
                "clause": "Pre-existing conditions and cosmetic procedures are not covered under this policy",
                "relevance_score": 0.87
            },
            {
                "section": "Claims Process",
                "clause": "Claims must be submitted within 30 days of the incident with proper documentation",
                "relevance_score": 0.82
            }
        ]
        
        # Customize response based on query type
        if query_type == "coverage":
            answer = f"Based on the document analysis, here's what I found regarding coverage for your query: '{query}'. The policy provides comprehensive coverage with specific limits and conditions that apply to your situation."
        elif query_type == "exclusions":
            answer = f"Regarding exclusions for your query: '{query}', I've identified several important limitations and exclusions in the document that you should be aware of."
        elif query_type == "claims":
            answer = f"For claims-related questions about: '{query}', the document outlines specific procedures and requirements that must be followed for successful claim processing."
        elif query_type == "legal":
            answer = f"From a legal compliance perspective regarding: '{query}', the document contains important regulatory requirements and legal obligations that need to be considered."
        else:
            answer = f"Based on the document analysis, here's what I found regarding your query: '{query}'. The document contains relevant information that addresses your question with specific details and conditions."
        
        return {
            "answer": answer,
            "clauses": mock_clauses,
            "confidence_score": 0.92,
            "explanation": "Mock response generated for demonstration purposes. Replace with actual API key for real analysis.",
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "model_used": "mock-model",
            "usage": {}
        }
    
    def _handle_api_error(self, status_code: int, error_text: str) -> Dict:
        """Handle API-specific errors"""
        return {
            "error": f"API Error {status_code}: {error_text}",
            "answer": "Unable to process query due to API error.",
            "clauses": [],
            "confidence_score": 0.0,
            "explanation": f"API returned status code {status_code}. Please check your API key and try again."
        }
    
    def _handle_request_error(self, error_message: str) -> Dict:
        """Handle network/request errors"""
        return {
            "error": f"Request Error: {error_message}",
            "answer": "Unable to connect to the API service.",
            "clauses": [],
            "confidence_score": 0.0,
            "explanation": "Network or connection error occurred. Please check your internet connection and try again."
        }
    
    def _handle_general_error(self, error_message: str) -> Dict:
        """Handle general errors"""
        return {
            "error": f"General Error: {error_message}",
            "answer": "An unexpected error occurred during processing.",
            "clauses": [],
            "confidence_score": 0.0,
            "explanation": "Unexpected error in the application. Please try again or contact support."
        }
    
    def _handle_parsing_error(self, error_message: str, content: str) -> Dict:
        """Handle response parsing errors"""
        return {
            "error": f"Parsing Error: {error_message}",
            "answer": content,
            "clauses": [],
            "confidence_score": 0.5,
            "explanation": "Received response but encountered error while parsing structured data."
        }

# Example usage
if __name__ == "__main__":
    # Initialize the API client
    api_client = PerplexityAPI()
    
    # Example query
    sample_query = "What is covered under this insurance policy?"
    sample_document = "This is a sample insurance policy document..."
    
    # Process the query
    result = api_client.query_document(sample_query, sample_document, "coverage")
    
    # Print the result
    print(json.dumps(result, indent=2)) 