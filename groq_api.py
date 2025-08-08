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

    def query_document(self, query, context, query_type="general"):
        prompt = f"Context:\n{context}\n\nQuestion:\n{query}"
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You're a helpful assistant answering document-based questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            answer = response.choices[0].message.content.strip()
            token_usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            return {"answer": answer, "token_usage": token_usage}
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")