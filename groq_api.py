import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GroqAPI:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def query_document(self, query, document_text, query_type="general"):
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes documents and answers user queries."},
            {"role": "user", "content": f"Query type: {query_type}\n\nQuery: {query}\n\nDocument:\n{document_text}"}
        ]
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.7
            )
            return {
                "response": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {
                "response": str(e),
                "success": False
            }
