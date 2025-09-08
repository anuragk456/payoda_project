import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

def generate_questions_and_answers(jd_text: str, resume_text: str) -> str:
    """Call Ollama LLaMA model with JD + Resume and return questions/answers."""
    prompt = f"""
You are an interviewer preparing for a Data Quality Analyst interview. 
Here is the Job Description:
{jd_text}

Here is the Candidate Resume:
{resume_text}

Your task:
- Generate 10–15 interview questions tailored to the role AND the candidate’s background. 
- For each question, provide a strong sample answer that demonstrates the candidate’s likely knowledge.
- Cover: SQL, ETL testing, data quality assurance, Power BI validation, defect management, 
data warehouse concepts, communication, collaboration.
- Keep answers concise (2–5 sentences), but technically correct.
"""

    url = f"{OLLAMA_BASE_URL}/api/generate"
    response = requests.post(
        url,
        json={"model": OLLAMA_MODEL, "prompt": prompt},
        stream=True
    )

    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")

    # Collect streamed chunks into a single text
    output = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            if data.startswith("{"):
                try:
                    import json
                    chunk = json.loads(data)
                    if "response" in chunk:
                        output += chunk["response"]
                except Exception:
                    pass
    return {"prompt": prompt.strip(), "questions_and_answers": output.strip()}
