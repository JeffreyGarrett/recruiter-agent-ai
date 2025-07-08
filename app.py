import os
os.umask(0)
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
import streamlit as st
# custom ageent imports
from agent.fit_evaluator import evaluate_candidate_fit
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage import StorageContext
import chromadb
import shutil


# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Print all environment variables loaded from .env
# print("Loaded environment variables:")
# print(f"OPENAI_API_KEY = {os.getenv('OPENAI_API_KEY')}")

# Configure LLM and embedding models globally
Settings.llm = OpenAI(model="gpt-4o", api_key=openai_api_key)
Settings.embed_model = OpenAIEmbedding(api_key=openai_api_key)

# Set up ChromaDB vector store

persist_dir = "./vector_store"
if os.path.exists(persist_dir):
    shutil.rmtree(persist_dir)
    print("🧹 Cleared old vector store.")   

chroma_client = chromadb.Client()
chroma_collection = chroma_client.get_or_create_collection("jeff_docs")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# Load documents
documents = SimpleDirectoryReader("docs").load_data()
print(f"📄 Loaded {len(documents)} documents.")

# Use SentenceSplitter to create real chunks
parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)
print(f"🔖 Generated {len(nodes)} chunks.")

# Build index from pre-chunked nodes
index = VectorStoreIndex(nodes, storage_context=storage_context)
index.storage_context.persist(persist_dir)
os.chmod("./vector_store", 0o777)

print("📊 Chroma vector count:", chroma_collection.count())

# Create query engine
query_engine = index.as_query_engine(similarity_top_k=5, verbose=True, llm=OpenAI(
        model="gpt-3.5-turbo",
        api_key=openai_api_key,
        system_prompt="You are JeffBot, a friendly and insightful Director of Technical Product and engineering executive. Respond as if you are Jeff with a profressional leadership and friendly tone and with a quick pun everyonce in a while. Whenever possible you want to provide details and exampels to drive confidence in your ability to lead and deliver results. Try to make people smile when you respond",
        text_qa_template="""
            You are JeffBot, an AI that answers questions based on Jeff Garrett's resume and professional background. 
            Always respond in a tone that is confident, insightful, and grounded, but avoid sounding overly formal.

            When answering, focus on:
            - Jeff’s leadership experience
            - His passion for public service and tech modernization
            - Real-world, practical impact

            If the question is outside the scope of the data, politely let the user know.

            Context: {context_str}
            Question: {query_str}
            Answer:
            """
    ))

# Streamlit UI
st.set_page_config(page_title="Chat with Jeff", page_icon="🤖")
st.title("🤖 Ask Jeff Anything")
st.markdown("This AI has read my professional history. Ask away!")

st.subheader("📄 Job Description & Evaluation Criteria")

job_description = st.text_area(
    "Paste the job description here",
    placeholder="We're hiring a VP of Engineering to lead a multi-disciplinary team and drive platform strategy..."
)

must_haves = st.text_area(
    "What are the must-have qualifications or skills?",
    placeholder="e.g., 10+ years engineering leadership, experience in platform/infra, agile delivery at scale..."
)

nice_to_haves = st.text_area(
    "What are the nice-to-haves?",
    placeholder="e.g., Public sector experience, ML/AI familiarity, distributed org management..."
)

import re
import glob

# Load base resume
with open("docs/resume/resume.md", "r") as f:
    resume_text = f.read()

# Load all role-specific markdown files
role_files = sorted(glob.glob("docs/resume/resume_roles/*.md"))
role_text = ""

for filepath in role_files:
    with open(filepath, "r") as rf:
        role_text += "\n\n" + rf.read()

# Final context for the evaluator
full_resume_context = resume_text + "\n\n" + role_text


if st.button("🔍 Evaluate Jeff’s Fit for This Role"):
    if job_description.strip() and must_haves.strip():
        with st.spinner("Evaluating..."):
            result = evaluate_candidate_fit(
                resume_text=resume_text,
                job_description=job_description,
                must_haves=must_haves,
                nice_to_haves=nice_to_haves,
                api_key=openai_api_key
            )

            import json
            from datetime import datetime

            # Save evaluation result to log
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "job_description": job_description.strip(),
                "must_haves": must_haves.strip(),
                "nice_to_haves": nice_to_haves.strip(),
                "resume_used": "docs/resume.md",
                "raw_output": result
            }

            os.makedirs("logs", exist_ok=True)
            with open("logs/evaluations.jsonl", "a") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")

            # Write human-readable log summary
            summary_log_path = "logs/evaluations_summary.md"

            with open(summary_log_path, "a") as summary_file:
                summary_file.write(f"## 🧪 Evaluation – {log_entry['timestamp']}\n\n")
                decision_match = re.search(r"(?i)decision:\s*(.*)", result)
                confidence_match = re.search(r"(?i)confidence.*?:\s*(\d+)", result)
                strengths_match = re.search(r"(?i)strengths(?:.*?)[:\-]?\s*(.+?)(?=\n\s*(?:gaps|\Z))", result, re.DOTALL)
                gaps_match = re.search(r"(?i)gaps(?:.*?)[:\-]?\s*(.+)", result, re.DOTALL)

                if decision_match:
                    summary_file.write(f"**Decision:** {decision_match.group(1).strip()}\n")
                if confidence_match:
                    summary_file.write(f"**Confidence:** {confidence_match.group(1).strip()}\n\n")

                summary_file.write("### 📄 Job Summary\n")
                summary_file.write(log_entry['job_description'].strip()[:500] + "...\n\n")

                if strengths_match:
                    summary_file.write("### ✅ Strengths\n")
                    summary_file.write(strengths_match.group(1).strip() + "\n\n")

                if gaps_match:
                    summary_file.write("### ⚠️ Gaps or Unknowns\n")
                    summary_file.write(gaps_match.group(1).strip() + "\n\n")

                summary_file.write("---\n\n")

        

            # More forgiving parsing (ignores **, :, etc.)
            decision_match = re.search(r"(?i)\**\s*decision\**.*?:\s*(.+)", result)
            confidence_match = re.search(r"(?i)\**\s*confidence.*?\**.*?:\s*(\d+)", result)
            strengths_match = re.search(r"(?i)\**\s*strengths.*?\**.*?:\s*(.+?)(?=\n\s*(?:\**\s*gaps|\Z))", result, re.DOTALL)
            gaps_match = re.search(r"(?i)\**\s*gaps.*?\**.*?:\s*(.+)", result, re.DOTALL)

            st.markdown("### 🤖 Parsed Summary")

            if decision_match:
                st.subheader(f"🟢 Decision: {decision_match.group(1).strip()}")

            if confidence_match:
                st.markdown(f"**Confidence Score:** {confidence_match.group(1)} / 100")

            if strengths_match:
                st.markdown("**✅ Strengths / Alignments:**")
                st.markdown(strengths_match.group(1).strip())

            if gaps_match:
                st.markdown("**⚠️ Gaps or Unknowns:**")
                st.markdown(gaps_match.group(1).strip())
    else:
        st.warning("Please provide at least the job description and must-have criteria.")




user_input = st.text_input("Your question:")


if user_input:
    with st.spinner("Thinking..."):
        response = query_engine.query(user_input)
        st.markdown(f"**Answer:** {response.response}")