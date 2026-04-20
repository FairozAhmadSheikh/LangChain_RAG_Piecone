import streamlit as st
import os 

from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# Function that accepts files and loads the data 

def load_documnets(file):
    """
    This function accepsts files with extenstion '.txt' , '.pdf' and '.doxc'
    and returns data loaded from the file 

    """
    import os 
    name,extension=os.path.splitext(file)
    
    if extension == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        print(f'Loading {file}....')
        loader=PyPDFLoader(file)

    elif extension == '.docx':
        from langchain_community.document_loaders import Docx2txtLoader
        print(f'Loading {file}....')
        loader=Docx2txtLoader(file)

    elif extension=='.txt':
        from langchain_community import TextLoader
        print(f'Loading the {file}......')
        loader=TextLoader(file)

    else:
        print('Document format is not supported for now ')
    
    data=loader.load()
    return data


# Function that is used for Chunking the data 
def chunk_data(data,chunk_size=256):
    """
    This function takes data loaded from lanchain_documentloaders and then chunks them 
    data : Data loaded using lanchain documents loader
    chunk_size : Provide an in integer ranging from 256 to any you like [256,512,1024 ]
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size)
    chunks=text_splitter.split_documents(data)
    return chunks

# function that creates or fetches embedding
def insert_or_fetch_embedding(index_name, chunks):
    import os
    import time
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(), override=True)

    # Pinecone init
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    #  LOCAL embeddings (NO API, NO ERRORS)
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
        print(f" Creating index '{index_name}'...")

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

        print(" Storing embeddings...")

        vector_store = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=index_name
        )

        print(" Index created and data stored")

    return vector_store

# Defining a function for question answering 

def ask_and_get_answers(vector_store, q):
    """
    Ask question from vector DB using Gemini (FIXED)
    """

    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains import RetrievalQA
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(), override=True)

    # add convert_system_message_to_human=True
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",   # safer model
        temperature=0,
        convert_system_message_to_human=True
    )

    #  correct spelling (retriever)
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    #  use proper constructor
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )

    #  correct input format
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

    cost = total_tokens / 1000 * 0.0004  # update if using newer model

    print(f"Total Tokens: {total_tokens}")
    print(f"Embedding cost in USD $: {cost:.6f}")

    return total_tokens, cost