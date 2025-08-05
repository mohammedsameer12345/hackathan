import re
import json
from typing import Dict, List, Optional
from datetime import datetime

class DocumentAnalyzer:
    """Intelligent document analyzer that extracts information from various document types"""
    
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
        if self.document_type == "resume":
            return self._analyze_resume(text)
        elif self.document_type == "insurance_policy":
            return self._analyze_insurance_policy(text)
        elif self.document_type == "legal_contract":
            return self._analyze_legal_contract(text)
        elif self.document_type == "hr_document":
            return self._analyze_hr_document(text)
        else:
            return self._analyze_general_document(text)
    
    def _detect_document_type(self, text: str) -> str:
        """Detect the type of document based on content"""
        text_lower = text.lower()
        
        # Resume indicators
        resume_keywords = ['resume', 'cv', 'curriculum vitae', 'experience', 'skills', 'education', 'objective', 'summary']
        if any(keyword in text_lower for keyword in resume_keywords):
            return "resume"
        
        # Insurance policy indicators
        insurance_keywords = ['insurance', 'policy', 'coverage', 'premium', 'claim', 'benefits', 'exclusions']
        if any(keyword in text_lower for keyword in insurance_keywords):
            return "insurance_policy"
        
        # Legal contract indicators
        legal_keywords = ['contract', 'agreement', 'terms', 'conditions', 'party', 'obligations', 'liability']
        if any(keyword in text_lower for keyword in legal_keywords):
            return "legal_contract"
        
        # HR document indicators
        hr_keywords = ['employment', 'employee', 'hr', 'human resources', 'job description', 'policy']
        if any(keyword in text_lower for keyword in hr_keywords):
            return "hr_document"
        
        return "general_document"
    
    def _analyze_resume(self, text: str) -> Dict:
        """Extract information from resume/CV"""
        info = {
            "document_type": "Resume/CV",
            "candidate_name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "summary": self._extract_summary(text),
            "key_sections": self._identify_resume_sections(text)
        }
        
        return info
    
    def _analyze_insurance_policy(self, text: str) -> Dict:
        """Extract information from insurance policy"""
        info = {
            "document_type": "Insurance Policy",
            "policy_type": self._extract_policy_type(text),
            "coverage_details": self._extract_coverage_details(text),
            "exclusions": self._extract_exclusions(text),
            "claims_process": self._extract_claims_process(text),
            "premium_info": self._extract_premium_info(text),
            "key_sections": self._identify_policy_sections(text)
        }
        
        return info
    
    def _analyze_legal_contract(self, text: str) -> Dict:
        """Extract information from legal contract"""
        info = {
            "document_type": "Legal Contract",
            "parties": self._extract_parties(text),
            "contract_type": self._extract_contract_type(text),
            "key_terms": self._extract_key_terms(text),
            "obligations": self._extract_obligations(text),
            "liability": self._extract_liability(text),
            "key_sections": self._identify_contract_sections(text)
        }
        
        return info
    
    def _analyze_hr_document(self, text: str) -> Dict:
        """Extract information from HR document"""
        info = {
            "document_type": "HR Document",
            "document_type_specific": self._extract_hr_document_type(text),
            "policies": self._extract_policies(text),
            "procedures": self._extract_procedures(text),
            "requirements": self._extract_requirements(text),
            "key_sections": self._identify_hr_sections(text)
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
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from resume"""
        # Look for common name patterns
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                # Look for title case names (first letter of each word capitalized)
                words = line.split()
                if len(words) >= 2 and len(words) <= 4:
                    if all(word[0].isupper() and word.isalpha() for word in words):
                        return line
        
        # Fallback: look for patterns like "Name:" or "Full Name:"
        name_patterns = [
            r'name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'full name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'candidate:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Name not found"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "Email not found"
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\+\d{1,3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return "Phone not found"
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume"""
        skills = []
        
        # Look for skills section
        skills_section = self._find_section(text, ['skills', 'technical skills', 'competencies', 'expertise'])
        if skills_section:
            # Extract skills (words separated by commas, semicolons, or bullets)
            skill_pattern = r'[•\-\*]\s*([^,\n]+)|([^,\n]+)(?=,|\n|$)'
            matches = re.findall(skill_pattern, skills_section)
            for match in matches:
                skill = (match[0] or match[1]).strip()
                if skill and len(skill) > 2:
                    skills.append(skill)
        
        return skills[:10]  # Limit to top 10 skills
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        
        # Look for experience section
        exp_section = self._find_section(text, ['experience', 'work experience', 'employment history', 'professional experience'])
        if exp_section:
            # Simple extraction - look for job titles and companies
            lines = exp_section.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 10 and any(keyword in line.lower() for keyword in ['inc', 'corp', 'ltd', 'company', 'assistant', 'manager', 'developer', 'engineer']):
                    experience.append({"description": line})
        
        return experience[:5]  # Limit to top 5 experiences
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        
        # Look for education section
        edu_section = self._find_section(text, ['education', 'academic', 'qualifications'])
        if edu_section:
            lines = edu_section.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 10 and any(keyword in line.lower() for keyword in ['university', 'college', 'school', 'degree', 'bachelor', 'master', 'phd']):
                    education.append({"description": line})
        
        return education[:3]  # Limit to top 3 education entries
    
    def _extract_summary(self, text: str) -> str:
        """Extract summary/objective"""
        summary_section = self._find_section(text, ['summary', 'objective', 'profile', 'about'])
        if summary_section:
            return summary_section[:200] + "..." if len(summary_section) > 200 else summary_section
        return "Summary not found"
    
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
    
    def _identify_resume_sections(self, text: str) -> List[str]:
        """Identify key sections in resume"""
        sections = []
        section_keywords = [
            'contact', 'summary', 'objective', 'experience', 'education', 
            'skills', 'projects', 'certifications', 'awards', 'languages'
        ]
        
        for keyword in section_keywords:
            if keyword in text.lower():
                sections.append(keyword.title())
        
        return sections
    
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
    
    def _identify_policy_sections(self, text: str) -> List[str]:
        """Identify key sections in insurance policy"""
        sections = []
        section_keywords = ['coverage', 'exclusions', 'claims', 'premium', 'terms', 'conditions']
        
        for keyword in section_keywords:
            if keyword in text.lower():
                sections.append(keyword.title())
        
        return sections
    
    def _extract_parties(self, text: str) -> List[str]:
        """Extract parties from contract"""
        parties = []
        # Look for party definitions
        party_patterns = [
            r'between\s+([^,]+)',
            r'party\s+([^,]+)',
            r'(\w+\s+\w+)\s+\(.*?\)'
        ]
        
        for pattern in party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            parties.extend(matches)
        
        return list(set(parties))[:3]
    
    def _extract_contract_type(self, text: str) -> str:
        """Extract contract type"""
        contract_types = ['employment', 'service', 'purchase', 'lease', 'partnership', 'licensing']
        text_lower = text.lower()
        
        for contract_type in contract_types:
            if contract_type in text_lower:
                return contract_type.title() + " Contract"
        
        return "Contract"
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from contract"""
        terms = []
        terms_section = self._find_section(text, ['terms', 'conditions', 'provisions'])
        
        if terms_section:
            lines = terms_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    terms.append(line.strip())
        
        return terms[:5]
    
    def _extract_obligations(self, text: str) -> List[str]:
        """Extract obligations from contract"""
        obligations = []
        obligation_section = self._find_section(text, ['obligations', 'duties', 'responsibilities'])
        
        if obligation_section:
            lines = obligation_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    obligations.append(line.strip())
        
        return obligations[:5]
    
    def _extract_liability(self, text: str) -> str:
        """Extract liability information"""
        liability_section = self._find_section(text, ['liability', 'damages', 'indemnification'])
        if liability_section:
            return liability_section[:200] + "..." if len(liability_section) > 200 else liability_section
        return "Liability information not found"
    
    def _identify_contract_sections(self, text: str) -> List[str]:
        """Identify key sections in contract"""
        sections = []
        section_keywords = ['parties', 'terms', 'obligations', 'liability', 'termination', 'governing law']
        
        for keyword in section_keywords:
            if keyword in text.lower():
                sections.append(keyword.title())
        
        return sections
    
    def _extract_hr_document_type(self, text: str) -> str:
        """Extract specific HR document type"""
        hr_types = ['policy', 'procedure', 'job description', 'employee handbook', 'code of conduct']
        text_lower = text.lower()
        
        for hr_type in hr_types:
            if hr_type in text_lower:
                return hr_type.title()
        
        return "HR Document"
    
    def _extract_policies(self, text: str) -> List[str]:
        """Extract policies from HR document"""
        policies = []
        policy_section = self._find_section(text, ['policy', 'policies'])
        
        if policy_section:
            lines = policy_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    policies.append(line.strip())
        
        return policies[:5]
    
    def _extract_procedures(self, text: str) -> List[str]:
        """Extract procedures from HR document"""
        procedures = []
        procedure_section = self._find_section(text, ['procedure', 'procedures', 'process'])
        
        if procedure_section:
            lines = procedure_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    procedures.append(line.strip())
        
        return procedures[:5]
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements from HR document"""
        requirements = []
        requirement_section = self._find_section(text, ['requirements', 'qualifications', 'criteria'])
        
        if requirement_section:
            lines = requirement_section.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    requirements.append(line.strip())
        
        return requirements[:5]
    
    def _identify_hr_sections(self, text: str) -> List[str]:
        """Identify key sections in HR document"""
        sections = []
        section_keywords = ['policy', 'procedure', 'requirements', 'responsibilities', 'benefits']
        
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

# Example usage
if __name__ == "__main__":
    analyzer = DocumentAnalyzer()
    
    # Test with sample resume
    sample_resume = """
    John Doe
    john.doe@email.com
    (555) 123-4567
    
    SUMMARY
    Experienced software developer with 5 years of experience in Python and web development.
    
    EXPERIENCE
    Senior Developer at Tech Corp (2020-2023)
    - Developed web applications using Python and Flask
    - Led team of 5 developers
    
    SKILLS
    Python, JavaScript, Flask, Django, SQL
    """
    
    result = analyzer.analyze_document(sample_resume)
    print(json.dumps(result, indent=2)) 