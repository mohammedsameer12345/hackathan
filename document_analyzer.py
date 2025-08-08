import re
import json
from typing import Dict, List, Optional
from datetime import datetime

class DocumentAnalyzer:
    """Intelligent document analyzer that extracts information from insurance policies"""
    
    def __init__(self):
        self.document_type = None
        self.extracted_info = {}
    
    def analyze_document(self, text: str) -> Dict:
        """Analyze document and extract structured information"""
        text = text.strip()
        if not text:
            return {"error": "No text content found"}
        
        # Determine document type
        self.document_type = self._detect_document_type(text)
        
        # Extract information based on document type
        if self.document_type == "insurance_policy":
            return self._analyze_insurance_policy(text)
        else:
            return self._analyze_general_document(text)
    
    def _detect_document_type(self, text: str) -> str:
        """Detect the type of document based on content"""
        text_lower = text.lower()
        
        # Insurance policy indicators
        insurance_keywords = [
            'insurance', 'policy', 'coverage', 'premium', 'claim', 'benefits', 'exclusions',
            'policy period', 'sum insured', 'policyholder', 'insured', 'waiting period',
            'grace period', 'cumulative bonus', 'portability', 'renewal', 'deductible'
        ]
        
        # Count how many insurance keywords appear in the document
        insurance_keyword_count = sum(1 for keyword in insurance_keywords if keyword in text_lower)
        
        # If we have at least 3 insurance keywords, classify as insurance policy
        if insurance_keyword_count >= 3:
            return "insurance_policy"
        
        return "general_document"
    
    def _analyze_insurance_policy(self, text: str) -> Dict:
        """Extract information from insurance policy"""
        info = {
            "document_type": "Insurance Policy",
            "policy_type": self._extract_policy_type(text),
            "coverage_details": self._extract_coverage_details(text),
            "exclusions": self._extract_exclusions(text),
            "claims_process": self._extract_claims_process(text),
            "premium_info": self._extract_premium_info(text),
            "key_terms": self._extract_key_terms(text),
            "terms_conditions": self._extract_terms_conditions(text),
            "definitions": self._extract_definitions(text),
            "key_sections": self._identify_policy_sections(text)
        }
        
        return info
    
    def _analyze_general_document(self, text: str) -> Dict:
        """Extract general information from any document"""
        info = {
            "document_type": "General Document",
            "key_topics": self._extract_key_topics(text),
            "important_dates": self._extract_dates(text),
            "key_entities": self._extract_entities(text),
            "summary": self._generate_summary(text),
            "word_count": len(text.split()),
            "estimated_pages": len(text) // 500
        }
        
        return info
    
    def _find_section(self, text: str, section_names: List[str]) -> str:
        """Find a specific section in the document"""
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line starts a new section
            if any(name in line_lower for name in section_names):
                in_section = True
                continue
            
            # If we're in the section, collect content
            if in_section:
                if line.strip() and len(line.strip()) > 2:
                    section_content.append(line.strip())
                else:
                    # Empty line might indicate end of section
                    if len(section_content) > 0:
                        break
        
        return '\n'.join(section_content)
    
    def _extract_policy_type(self, text: str) -> str:
        """Extract insurance policy type"""
        policy_types = ['health', 'life', 'auto', 'home', 'property', 'liability']
        text_lower = text.lower()
        
        for policy_type in policy_types:
            if policy_type in text_lower:
                return policy_type.title() + " Insurance"
        
        return "Insurance Policy"
    
    def _extract_coverage_details(self, text: str) -> List[str]:
        """Extract coverage details from policy"""
        coverage = []
        coverage_section = self._find_section(text, ['coverage', 'benefits', 'what is covered'])
        
        if coverage_section:
            lines = coverage_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    coverage.append(line.strip())
        
        return coverage[:5]
    
    def _extract_exclusions(self, text: str) -> List[str]:
        """Extract exclusions from policy"""
        exclusions = []
        exclusion_section = self._find_section(text, ['exclusions', 'what is not covered', 'limitations'])
        
        if exclusion_section:
            lines = exclusion_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    exclusions.append(line.strip())
        
        return exclusions[:5]
    
    def _extract_claims_process(self, text: str) -> List[str]:
        """Extract claims process information"""
        claims = []
        claims_section = self._find_section(text, ['claims', 'claim process', 'filing claims'])
        
        if claims_section:
            lines = claims_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    claims.append(line.strip())
        
        return claims[:5]
    
    def _extract_premium_info(self, text: str) -> str:
        """Extract premium information"""
        premium_section = self._find_section(text, ['premium', 'payment', 'cost'])
        if premium_section:
            return premium_section[:200] + "..." if len(premium_section) > 200 else premium_section
        return "Premium information not found"
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from policy"""
        terms = []
        terms_section = self._find_section(text, ['terms', 'conditions', 'provisions', 'key terms'])
        
        if terms_section:
            lines = terms_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    terms.append(line.strip())
        
        # Prioritize duration-related terms
        duration_terms = []
        for term in terms:
            term_lower = term.lower()
            if any(keyword in term_lower for keyword in ["duration", "period", "term", "policy term", "policy period"]):
                duration_terms.append(term)
        
        if duration_terms:
            return duration_terms[:5]
        
        return terms[:5]
    
    def _extract_terms_conditions(self, text: str) -> List[str]:
        """Extract terms and conditions from policy"""
        terms_conditions = []
        terms_section = self._find_section(text, ['terms and conditions', 'terms & conditions', 'policy terms'])
        
        if terms_section:
            lines = terms_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    terms_conditions.append(line.strip())
        
        # Prioritize duration-related terms
        duration_terms = []
        for term in terms_conditions:
            term_lower = term.lower()
            if any(keyword in term_lower for keyword in ["duration", "period", "term", "policy term", "policy period"]):
                duration_terms.append(term)
        
        if duration_terms:
            return duration_terms[:5]
        
        return terms_conditions[:5]
    
    def _extract_definitions(self, text: str) -> List[str]:
        """Extract definitions from policy"""
        definitions = []
        definitions_section = self._find_section(text, ['definitions', 'defined terms'])
        
        if definitions_section:
            lines = definitions_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    definitions.append(line.strip())
        
        # Prioritize duration-related definitions
        duration_definitions = []
        for definition in definitions:
            definition_lower = definition.lower()
            if any(keyword in definition_lower for keyword in ["duration", "period", "term", "policy term", "policy period"]):
                duration_definitions.append(definition)
        
        if duration_definitions:
            return duration_definitions[:5]
        
        return definitions[:5]
    
    def _identify_policy_sections(self, text: str) -> List[str]:
        """Identify key sections in insurance policy"""
        sections = []
        section_keywords = ['coverage', 'exclusions', 'claims', 'premium', 'terms', 'conditions', 'definitions']
        
        for keyword in section_keywords:
            if keyword in text.lower():
                sections.append(keyword.title())
        
        return sections
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from general document"""
        # Simple keyword extraction
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            if len(word) > 4 and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from document"""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))[:5]
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (companies, organizations, etc.)"""
        entities = []
        
        # Look for capitalized phrases that might be entities
        lines = text.split('\n')
        for line in lines:
            words = line.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 2:
                    # Check if it's part of a multi-word entity
                    entity = word
                    j = i + 1
                    while j < len(words) and words[j][0].isupper():
                        entity += " " + words[j]
                        j += 1
                    if len(entity.split()) >= 2:
                        entities.append(entity)
        
        return list(set(entities))[:10]
    
    def _generate_summary(self, text: str) -> str:
        """Generate a summary of the document"""
        sentences = text.split('.')
        if len(sentences) > 3:
            summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = text
        
        return summary[:300] + "..." if len(summary) > 300 else summary