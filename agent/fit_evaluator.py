from llama_index.llms.openai import OpenAI
import os

def evaluate_candidate_fit(resume_text, job_description, must_haves, nice_to_haves, api_key=None):
    llm = OpenAI(
        model="gpt-4o",
        api_key=api_key or os.getenv("OPENAI_API_KEY")
    )

    prompt = f"""
You are an AI assistant helping a recruiter evaluate a candidate's fit for a role.

### Job Description
{job_description}

### Must-Have Criteria
{must_haves}

### Nice-to-Have Criteria
{nice_to_haves}

### Candidate Resume
{resume_text}

Respond with:
1. **Decision**: One of [Advance to Interview, Review More, Not a Match]
2. **Confidence Score**: 0–100
3. **Rationale**, broken into:
   a. Strengths / Alignments
   b. Gaps or Unknowns (clearly distinguish “missing info” from “does not have”)

Be fair, don’t assume facts that aren’t present, and explain any uncertainty.
"""

    response = llm.complete(prompt)
    return response.text.strip()