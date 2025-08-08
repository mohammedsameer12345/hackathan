import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import re

load_dotenv()
# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GroqAPI:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
    
    def get_system_prompt(self, query_type):
        """Generate system prompt based on query type"""
        prompts = {
            "general": "You're a helpful assistant answering document-based questions. Respond politely and help people to find the information they need. If the question seems to be about a specific aspect of the insurance policy (like coverage, exclusions, claims, premium, duration, terms, or definitions), suggest which query type would be most appropriate for getting more detailed information.",
            
            "coverage": "You are an insurance policy expert specializing in coverage details. Analyze the provided context to answer questions about what is covered under the insurance policy. Be specific about coverage limits, conditions, and inclusions.",
            
            "exclusions": "You are an insurance policy expert specializing in policy exclusions. Analyze the provided context to answer questions about what is not covered under the insurance policy. Clearly identify specific exclusions, limitations, and conditions that void coverage.",
            
            "claims": "You are an insurance claims specialist. Analyze the provided context to answer questions about the claims process. Provide clear, step-by-step guidance on how to file claims, required documentation, and claim timelines.",
            
            "premium": "You are an insurance premium specialist. Analyze the provided context to answer questions about premium payments, costs, fees, and payment schedules. Include information about grace periods, late payment consequences, and payment options.",
            
            "duration": "You are an insurance policy duration expert. Analyze the provided context to answer questions about policy periods, term lengths, renewal conditions, and coverage timeframes. Be specific about start and end dates, renewal processes, and policy continuity.",
            
            "terms": "You are an insurance terms and conditions specialist. Analyze the provided context to answer questions about policy terms, conditions, and contractual obligations. Explain legal terms in clear language and highlight important conditions policyholders should be aware of.",
            
            "definitions": "You are an insurance terminology expert. Analyze the provided context to answer questions about defined terms in the policy. Provide clear definitions for insurance-specific terminology and explain how these definitions apply to the policy coverage.",
        }
        
        return prompts.get(query_type, prompts["general"])
    
    def suggest_query_type(self, query):
        """Suggest a more specific query type based on the question content"""
        query_lower = query.lower()
        
        # Define keyword patterns for each query type
        query_type_patterns = {
            "coverage": [
                r'\bcoverage\b', r'\bcovered\b', r'\bbenefits\b', r'\bincluded\b', r'\bprotection\b',
                r'\bwhat\s+is\s+covered\b', r'\bwhat\s+does\s+it\s+cover\b'
            ],
            "exclusions": [
                r'\bexclusion\b', r'\bexcluded\b', r'\bnot\s+covered\b', r'\blimitation\b', r'\brestriction\b',
                r'\bwhat\s+is\s+not\s+covered\b', r'\bwhat\s+are\s+the\s+exclusions\b'
            ],
            "claims": [
                r'\bclaim\b', r'\bclaims\s+process\b', r'\bfile\s+a\s+claim\b', r'\bhow\s+to\s+claim\b',
                r'\bclaim\s+procedure\b', r'\bclaim\s+timeline\b'
            ],
            "premium": [
                r'\bpremium\b', r'\bcost\b', r'\bprice\b', r'\bpayment\b', r'\bfee\b', r'\binstallment\b',
                r'\bhow\s+much\b', r'\bpayment\s+schedule\b'
            ],
            "duration": [
                r'\bduration\b', r'\bperiod\b', r'\bterm\b', r'\bpolicy\s+term\b', r'\bpolicy\s+period\b',
                r'\bhow\s+long\b', r'\blength\b', r'\bvalidity\b', r'\bwhen\s+does\s+it\s+expire\b'
            ],
            "terms": [
                r'\bterms\b', r'\bconditions\b', r'\bterms\s+and\s+conditions\b', r'\bcontractual\b',
                r'\bobligation\b', r'\brequirements\b'
            ],
            "definitions": [
                r'\bdefinition\b', r'\bdefine\b', r'\bmeaning\b', r'\bterminology\b', r'\bglossary\b',
                r'\bwhat\s+does\s+\w+\s+mean\b'
            ]
        }
        
        # Check each query type for matching patterns
        for query_type, patterns in query_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    logger.debug(f"Suggested query type: {query_type} for query: {query}")
                    return query_type
        
        # No specific query type identified
        return None
    
    def query_document(self, query, context, query_type="general"):
        # Get the appropriate system prompt based on query type
        system_prompt = self.get_system_prompt(query_type)
        
        # Create the user prompt with context and question
        user_prompt = f"Context:\n{context}\n\nQuestion:\n{query}"
        
        # Log the query type for debugging
        logger.debug(f"Groq API called with query_type: {query_type}")
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            token_usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # For general queries, suggest a more specific query type if applicable
            suggested_query_type = None
            if query_type == "general":
                suggested_query_type = self.suggest_query_type(query)
                
                # If a more specific query type is suggested, add a note to the answer
                if suggested_query_type:
                    suggestion_note = f"\n\n💡 Tip: For more specific information about this topic, try using the '{suggested_query_type}' query type."
                    answer += suggestion_note
                    logger.debug(f"Added suggestion note for query type: {suggested_query_type}")
            
            # Log successful response with query type
            logger.debug(f"Groq API response received for query_type: {query_type}, tokens used: {token_usage['total_tokens']}")
            
            # Include query type and suggestion in the response for debugging
            response_data = {
                "answer": answer, 
                "token_usage": token_usage,
                "query_type_used": query_type,
                "debug_info": f"Answered using {query_type} mode"
            }
            
            # Add suggested query type if applicable
            if suggested_query_type:
                response_data["suggested_query_type"] = suggested_query_type
                response_data["debug_info"] += f" (suggested: {suggested_query_type})"
            
            return response_data
        
        except Exception as e:
            logger.error(f"Groq API error with query_type {query_type}: {str(e)}")
            raise Exception(f"Groq API error: {str(e)}")