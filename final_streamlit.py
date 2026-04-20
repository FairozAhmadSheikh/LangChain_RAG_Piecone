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


# Chunk the Data 
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
