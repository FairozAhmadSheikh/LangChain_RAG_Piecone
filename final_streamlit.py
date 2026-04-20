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

