# 🧠 AI Prototype App

A local LLM-powered assistant that reads your documents and answers questions conversationally. This app uses Streamlit, LlamaIndex, and ChromaDB to create a vector-based knowledge assistant that can be queried interactively.

---

## 📁 Folder Structure

```
ai-prototype-app/
├── app.py                      # Main Streamlit application
├── .env                        # Stores your OpenAI API key
├── requirements.txt            # Python dependencies
├── vector_store/               # ChromaDB persisted vector store
└── docs/                       # Folder for ingesting documents
    ├── general/                # General documents
    └── college/                # School/college-specific documents
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo and navigate into it

```bash
git clone https://github.com/your-username/ai-prototype-app.git
cd ai-prototype-app
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

Add your OpenAI API key to a file named `.env` in the project root:

```env
OPENAI_API_KEY=sk-...
```

---

## ▶️ Running the App Locally

```bash
streamlit run app.py
```

Navigate to [http://localhost:8501](http://localhost:8501) in your browser to interact with the assistant.

---

## 🌐 Exposing the App with `ngrok`

To expose your local app to the internet:

### 1. Install ngrok

```bash
brew install ngrok  # macOS
# or download from https://ngrok.com/download
```

### 2. Start your Streamlit app

```bash
streamlit run app.py
```

### 3. In a new terminal, expose port 8501

```bash
ngrok http 8501
```

Copy the forwarded `https://...ngrok.io` URL to share the app externally.

---

## 🧪 Testing the App

1. Place `.txt` or `.md` files into the `docs/` folder or its subfolders.
2. Run the app.
3. Ask questions in the Streamlit UI based on the document contents.
4. To verify ingestion:
   - Check logs for how many documents/chunks were loaded.
   - Use test queries to verify the AI is referencing expected content.

---

## 🗂️ Adding More Document Categories

To specialize your assistant:

1. Create a new subfolder in `docs/` (e.g., `docs/resume/`)
2. Place files there.
3. Update your `app.py` logic to load and query documents from that folder as needed.

---

## 💡 Next Steps

- Add user memory/statefulness
- Use metadata filters or query routers
- Implement feedback/correction loop for fine-tuning

---

## 👨‍💻 Maintainer

Jeff Garrett
