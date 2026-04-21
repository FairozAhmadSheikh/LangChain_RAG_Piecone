
# AI-Powered Document Question Answering System (RAG Chatbot)

##  Overview
This project is an AI-based system that allows users to upload documents and ask questions about them.  
It uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-based answers instead of relying on pre-trained knowledge alone.

---

##  Problem Statement
Traditional AI models (like ChatGPT) cannot access or understand **private or custom documents**. This leads to:

- ❌ Inability to answer document-specific questions  
- ❌ Hallucinated (incorrect) responses  
- ❌ Time-consuming manual document search  

---

## 💡 Solution
This project solves the problem by combining:

- **Document Retrieval** (finding relevant information)
- **AI Generation** (creating answers)

###  Working Principle
1. Upload document (PDF/Text)
2. Split into smaller chunks
3. Convert chunks into embeddings (vectors)
4. Store in vector database
5. On query:
   - Retrieve relevant chunks
   - Generate answer using AI

---

##  Key Concept
**Retrieval-Augmented Generation (RAG)**  
A technique where AI retrieves relevant data before generating answers, ensuring higher accuracy and reduced hallucination.

---

##  Tech Stack

### Programming Language
- Python

###  Frameworks & Libraries
- LangChain (LLM orchestration)
- Flask (Web backend)

###  AI Models
- Google Gemini (for answering queries)

###  Embeddings
- HuggingFace / OpenAI Embeddings

###  Vector Database
- Pinecone

###  Environment Management
- python-dotenv

---

## System Architecture

```

User → Upload Document
↓
Text Chunking
↓
Embeddings Generation
↓
Vector Database (Pinecone)
↓
User Query
↓
Retriever (Semantic Search)
↓
LLM (Gemini)
↓
Final Answer

````

---

## Features

-  Document upload and processing  
-  Semantic search (meaning-based retrieval)  
-  Conversational AI with memory  
-  Fast response using vector database  
-  Accurate answers based on context  

---

##  How to Run

###  Clone Repository
```bash
git clone https://github.com/FairozAhmadSheikh/LangChain_RAG_Piecone.git
cd your-repo
````

###  Create Virtual Environment

```bash
python -m venv env
source env/bin/activate   # Mac/Linux
env\Scripts\activate      # Windows
```

###  Install Dependencies

```bash
pip install -r requirements.txt
```

###  Setup Environment Variables

Create a `.env` file:

```
PINECONE_API_KEY=your_key
GOOGLE_API_KEY=your_key
HUGGINGFACEHUB_API_TOKEN=your_token
```

###  Run Application

```bash
streamlit run  final_streamlit.py
```

---

##  Expected Output

* Upload documents
* Ask questions
* Get accurate, context-aware answers

---

##  Future Scope

* Multi-document support
* Voice-based interaction
* Mobile application integration
* Enterprise knowledge assistant

---

##  Use Cases

* 📚 Education (notes, books, study material)
* 🏢 Companies (internal documentation)
* 🔬 Research (paper analysis)

---

##  Conclusion

This project demonstrates how modern AI techniques like RAG can solve real-world problems such as:

* Information overload
* Inefficient document search
* Lack of AI personalization

It is scalable, efficient, and highly relevant in today’s AI-driven world.

---

##  Author

**Fairoz Ahmad Sheikh *

---

## ⭐ If you like this project, give it a star!

