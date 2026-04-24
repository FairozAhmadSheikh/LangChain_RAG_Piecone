import streamlit as st
import os
import tempfile


# PAGE CONFIG  

st.set_page_config(
    page_title="DocuMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# GLOBAL CSS

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --brand:       #4f8ef7;
    --brand-dim:   #2563c4;
    --surface-0:   #0d0f14;
    --surface-1:   #13161e;
    --surface-2:   #1b1f2b;
    --surface-3:   #232837;
    --border:      rgba(79,142,247,.18);
    --text-1:      #edf0f7;
    --text-2:      #8d95ab;
    --text-3:      #555e74;
    --red:         #e05252;
    --green:       #34c77b;
    --radius-sm:   8px;
    --radius-md:   12px;
    --radius-lg:   18px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--surface-0) !important;
    color: var(--text-1) !important;
}

#MainMenu, footer, header { display: none !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 960px; }

section[data-testid="stSidebar"] {
    background: var(--surface-1) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.25rem !important; }

.hero {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.hero-brand {
    font-size: 2.4rem;
    font-weight: 600;
    letter-spacing: -0.03em;
    background: linear-gradient(110deg, #fff 30%, var(--brand));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}
.hero-tagline {
    font-size: 0.88rem;
    color: var(--text-2);
    font-weight: 400;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3);
    margin: 1.5rem 0 0.5rem;
}

.card {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

.stTextInput > div > div > input,
.stTextArea textarea,
.stNumberInput input {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    transition: border-color .2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,.12) !important;
    outline: none !important;
}

.stButton > button {
    background: var(--brand) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: background .2s, transform .1s !important;
}
.stButton > button:hover { background: var(--brand-dim) !important; }
.stButton > button:active { transform: scale(.97) !important; }

.stFileUploader > div {
    background: var(--surface-2) !important;
    border: 1px dashed var(--border) !important;
    border-radius: var(--radius-md) !important;
}

.stAlert {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

.voice-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 99px;
    background: var(--surface-3);
    border: 1px solid var(--border);
    color: var(--text-2);
    margin-top: 6px;
}
.voice-status.done { color: var(--green); border-color: var(--green); }

.answer-block {
    background: var(--surface-2);
    border-left: 3px solid var(--brand);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 1rem 1.25rem;
    font-size: 0.95rem;
    line-height: 1.8;
    color: var(--text-1);
    margin: 1rem 0;
    white-space: pre-wrap;
}

label, .stNumberInput label { color: var(--text-2) !important; font-size: 0.83rem !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--surface-1); }
::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)



# VOICE HELPERS

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribes WAV bytes server-side using Google Speech Recognition.
    Requires: pip install SpeechRecognition
    """
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        os.unlink(tmp_path)
        return text
    except Exception as e:
        st.warning(f"Transcription error: {e}")
        return ""


def tts_widget(answer_text: str):
    """Browser-native TTS — no mic permission required."""
    import streamlit.components.v1 as components
    safe = answer_text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
    html = f"""
    <style>
      #sp-btn {{
        display: inline-flex; align-items: center; gap: 8px;
        background: transparent; color: #4f8ef7;
        border: 1px solid rgba(79,142,247,.35); border-radius: 8px;
        padding: 7px 18px; font-size: 13px;
        font-family: 'DM Sans', system-ui, sans-serif;
        cursor: pointer; transition: background .2s; margin-top: 8px;
      }}
      #sp-btn:hover {{ background: rgba(79,142,247,.1); }}
      #sp-btn.speaking {{ color: #e05252; border-color: rgba(224,82,82,.4); }}
    </style>
    <button id="sp-btn" onclick="speak()">&#128264;&nbsp; Read answer aloud</button>
    <script>
      function speak() {{
        const btn = document.getElementById('sp-btn');
        if (window.speechSynthesis.speaking) {{
          window.speechSynthesis.cancel();
          btn.innerHTML = '&#128264;&nbsp; Read answer aloud';
          btn.classList.remove('speaking'); return;
        }}
        const u = new SpeechSynthesisUtterance('{safe}');
        u.lang='en-US'; u.rate=1.0; u.pitch=1.0;
        u.onstart = () => {{ btn.innerHTML='&#9209;&nbsp; Stop reading'; btn.classList.add('speaking'); }};
        u.onend   = () => {{ btn.innerHTML='&#128264;&nbsp; Read answer aloud'; btn.classList.remove('speaking'); }};
        window.speechSynthesis.speak(u);
      }}
    </script>
    """
    components.html(html, height=56)


# DOCUMENT HELPERS

def load_documents(file):
    _, extension = os.path.splitext(file)
    if extension == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file)
    elif extension == '.docx':
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(file)
    elif extension == '.txt':
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file)
    else:
        return []
    return loader.load()


def chunk_data(data, chunk_size=256):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size).split_documents(data)


def insert_or_fetch_embedding(index_name, chunks):
    import time
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    existing = [i.name for i in pc.list_indexes()]

    if index_name in existing:
        return PineconeVectorStore(index_name=index_name, embedding=emb)

    pc.create_index(
        name=index_name, dimension=384, metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    time.sleep(10)
    return PineconeVectorStore.from_documents(documents=chunks, embedding=emb, index_name=index_name)


def ask_and_get_answers(vector_store, q, k=3):
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains import RetrievalQA
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite", temperature=0,
        convert_system_message_to_human=True
    )
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
    return chain.invoke({"query": q})["result"]


def calculate_embedding_cost(texts):
    import tiktoken
    enc = tiktoken.encoding_for_model('text-embedding-ada-002')
    total = sum(len(enc.encode(p.page_content if hasattr(p, "page_content") else p)) for p in texts)
    return total, total / 1000 * 0.0004


def clear_history():
    if 'history' in st.session_state:
        del st.session_state['history']


# MAIN

if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)

    # Hero
    st.markdown("""
    <div class="hero">
        <div class="hero-brand">&#129504; DocuMind</div>
        <div class="hero-tagline">Ask your documents anything &mdash; by voice or by text</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        st.markdown('<div class="section-label">API Key</div>', unsafe_allow_html=True)
        api_key = st.text_input("Google Gemini API Key", type='password', label_visibility="collapsed")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key

        st.markdown('<div class="section-label">Document</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop a PDF, DOCX, or TXT",
            type=['pdf', 'docx', 'txt'],
            label_visibility="collapsed"
        )

        st.markdown('<div class="section-label">Retrieval settings</div>', unsafe_allow_html=True)
        chunk_size = st.number_input("Chunk size", min_value=100, max_value=2048, value=512, on_change=clear_history)
        k = st.number_input("Top-K results", min_value=1, max_value=20, value=3, on_change=clear_history)

        st.markdown("---")
        add_data = st.button("⚡ Embed Document", on_click=clear_history, use_container_width=True)

        if uploaded_file and add_data:
            with st.spinner("Reading · Chunking · Embedding…"):
                bytes_data = uploaded_file.read()
                file_name = os.path.join('./', uploaded_file.name)
                with open(file_name, 'wb') as f:
                    f.write(bytes_data)

                data   = load_documents(file_name)
                chunks = chunk_data(data, chunk_size=chunk_size)
                tokens, cost = calculate_embedding_cost(chunks)

                st.markdown(f"""
                <div class="card" style="font-size:0.82rem;color:var(--text-2);">
                    Tokens:&nbsp;<b style="color:var(--text-1)">{tokens:,}</b><br>
                    Est. cost:&nbsp;<b style="color:var(--text-1)">${cost:.4f}</b>
                </div>""", unsafe_allow_html=True)

                index_name = os.path.splitext(uploaded_file.name)[0].lower().replace(" ", "-")
                vector_store = insert_or_fetch_embedding(index_name, chunks)
                st.session_state.vs = vector_store
                st.success("Document ready — start asking!")

        st.markdown("""
        <div style="margin-top:2rem;font-size:0.72rem;color:var(--text-3);line-height:1.7;">
            Powered by Gemini · Pinecone · LangChain
        </div>""", unsafe_allow_html=True)

    # Voice input 
    st.markdown('<div class="section-label">🎙️ Voice input</div>', unsafe_allow_html=True)

    voice_text = ""
    try:
        from audio_recorder_streamlit import audio_recorder

        st.markdown(
            '<p style="font-size:0.82rem;color:var(--text-2);margin-bottom:8px;">'
            'Click the mic &rarr; speak &rarr; click again to stop. '
            'Your words will fill the question box below.</p>',
            unsafe_allow_html=True
        )
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e05252",
            neutral_color="#4f8ef7",
            icon_size="2x",
            pause_threshold=3.0,
        )
        if audio_bytes:
            with st.spinner("Transcribing your voice…"):
                voice_text = transcribe_audio(audio_bytes)
            if voice_text:
                st.markdown(
                    f'<div class="voice-status done">&#10003;&nbsp; Heard: {voice_text}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("Couldn't transcribe — please try again or type below.")

    except ImportError:
        st.info(
            "**Voice support not installed.** Run:\n"
            "```\npip install audio-recorder-streamlit SpeechRecognition\n```\n"
            "Then restart. You can still type questions below."
        )

    # Question input
    st.markdown('<div class="section-label">💬 Your question</div>', unsafe_allow_html=True)
    q = st.text_input(
        "question",
        value=voice_text,
        placeholder="e.g. What are the key findings in this document?",
        label_visibility="collapsed"
    )

    #   Answer 
    answer = ""
    if q:
        if 'vs' not in st.session_state:
            st.warning("Please upload and embed a document first using the sidebar.")
        else:
            vector_store = st.session_state['vs']
            with st.spinner("Thinking…"):
                answer = ask_and_get_answers(vector_store, q, k)

            st.markdown('<div class="section-label">🤖 Answer</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="answer-block">{answer}</div>', unsafe_allow_html=True)
            tts_widget(answer)

            st.divider()

            if 'history' not in st.session_state:
                st.session_state.history = ''
            entry = f"Q: {q}\nA: {answer}"
            st.session_state.history = f'{entry}\n{"─" * 80}\n{st.session_state.history}'

            st.markdown('<div class="section-label">📜 Chat history</div>', unsafe_allow_html=True)
            st.text_area(
                "history_area",
                value=st.session_state.history,
                key='history',
                height=300,
                label_visibility="collapsed"
            )