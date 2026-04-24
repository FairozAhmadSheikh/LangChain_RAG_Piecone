import streamlit as st
import os


from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# Function that accepts files and loads the data

def load_documents(file):
    """
    This function accepts files with extension '.txt', '.pdf' and '.docx'
    and returns data loaded from the file
    """
    name, extension = os.path.splitext(file)

    if extension == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        print(f'Loading {file}....')
        loader = PyPDFLoader(file)

    elif extension == '.docx':
        from langchain_community.document_loaders import Docx2txtLoader
        print(f'Loading {file}....')
        loader = Docx2txtLoader(file)

    elif extension == '.txt':
        # FIX 1: Correct import path for TextLoader
        from langchain_community.document_loaders import TextLoader
        print(f'Loading the {file}......')
        loader = TextLoader(file)

    else:
        print('Document format is not supported for now')
        return []

    data = loader.load()
    return data


# Function that is used for Chunking the data
def chunk_data(data, chunk_size=256):
    """
    This function takes data loaded from langchain_documentloaders and then chunks them
    data : Data loaded using langchain documents loader
    chunk_size : Provide an integer ranging from 256 to any you like [256, 512, 1024]
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size)
    chunks = text_splitter.split_documents(data)
    return chunks


# Function that creates or fetches embedding
def insert_or_fetch_embedding(index_name, chunks):  # FIX 2: kept correct signature
    import os
    import time
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(), override=True)

    # Pinecone init
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    # LOCAL embeddings (NO API, NO ERRORS)
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    existing_indexes = [i.name for i in pc.list_indexes()]

    if index_name in existing_indexes:
        print(f"Index '{index_name}' exists → loading...")

        vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings
        )

    else:
        print(f"Creating index '{index_name}'...")

        pc.create_index(
            name=index_name,
            dimension=384,   # correct for MiniLM
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        time.sleep(10)

        print("Storing embeddings...")

        vector_store = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=index_name
        )

        print("Index created and data stored")

    return vector_store


# Defining a function for question answering
# FIX 3: Added missing 'k' parameter
def ask_and_get_answers(vector_store, q, k=3):
    """
    Ask question from vector DB using Gemini
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains import RetrievalQA
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(), override=True)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        convert_system_message_to_human=True
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}  # FIX 4: use the k parameter
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )

    result = qa_chain.invoke({"query": q})

    return result["result"]


# Function for calculating embedding cost
def calculate_embedding_cost(texts):
    import tiktoken

    enc = tiktoken.encoding_for_model('text-embedding-ada-002')

    total_tokens = sum(
        len(enc.encode(page.page_content if hasattr(page, "page_content") else page))
        for page in texts
    )

    cost = total_tokens / 1000 * 0.0004

    print(f"Total Tokens: {total_tokens}")
    print(f"Embedding cost in USD $: {cost:.6f}")

    return total_tokens, cost


# Clear session state history using callback functions
def clear_history():
    # FIX 5: Correct condition — check key in session_state, not inside session_state['history']
    if 'history' in st.session_state:
        del st.session_state['history']


# Main app
if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)

    st.image("logo.png")
    st.subheader("DocuMind : RAG Based Question Answering LLM")

    with st.sidebar:
        api_key = st.text_input("Enter the API Key : ", type='password')
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key

        uploaded_file = st.file_uploader('Upload a file : ', type=['pdf', 'docx', 'txt'])

        chunk_size = st.number_input("Chunk Size : ", min_value=100,
                                     max_value=2048,
                                     value=512, on_change=clear_history)
        k = st.number_input("Choose K: ", min_value=1, max_value=20, value=3, on_change=clear_history)

        add_data = st.button("Add Data", on_click=clear_history)

        if uploaded_file and add_data:
            with st.spinner('Reading, Chunking and Embedding...'):
                bytes_data = uploaded_file.read()
                file_name = os.path.join('./', uploaded_file.name)
                with open(file_name, 'wb') as f:
                    f.write(bytes_data)

                # Load document and chunk it
                data = load_documents(file_name)
                chunks = chunk_data(data, chunk_size=chunk_size)

                # Calculate Embedding Cost
                tokens, embedding_cost = calculate_embedding_cost(chunks)
                st.write(f"Estimated embedding cost (USD): ${embedding_cost:.4f}")

                # FIX 6: Derive index_name from file and pass both required arguments
                index_name = os.path.splitext(uploaded_file.name)[0].lower().replace(" ", "-")
                vector_store = insert_or_fetch_embedding(index_name, chunks)

                st.session_state.vs = vector_store
                st.success("File Uploaded, Chunked and Embedded Successfully")

    q = st.text_input("Ask a Question about the content of Your Uploaded File : ")

    if q:
        if 'vs' in st.session_state:
            # FIX 7: Correct session state access — was st.session_state.values
            vector_store = st.session_state['vs']
            st.write(f'k: {k}')
            answer = ask_and_get_answers(vector_store, q, k)
            st.text_area('LLM Answer : ', value=answer)

        st.divider()

        if 'history' not in st.session_state:
            st.session_state.history = ''

        value = f'Q: {q}\nA: {answer}'
        st.session_state.history = f'{value}\n{"─" * 100}\n{st.session_state.history}'

        h = st.session_state.history
        st.text_area(label='Chat History', value=h, key='history', height=400)