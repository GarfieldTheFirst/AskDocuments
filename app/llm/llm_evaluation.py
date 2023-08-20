"""
This script creates a database of information gathered from local text files.
"""

from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain import PromptTemplate
from langchain.chains import RetrievalQA


def load_documents(dir, glob):
    loader = DirectoryLoader(dir, glob=glob, loader_cls=TextLoader)

    # interpret information in the documents
    documents = loader.load()
    return documents


def load_and_store_text(saved_name, dir, glob):
    documents = load_documents(dir, glob)
    if not documents:
        return False
    splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                              chunk_overlap=50)
    texts = splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'})

    # create and save the local database
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(saved_name)
    return True


"""
This script reads the database of information from local text files
and uses a large language model to answer questions about their content.
"""


def load_language_model():
    # load the language model
    # './llama-2-7b-chat.ggmlv3.q8_0.bin'
    # './app/llm/llama-2-7b-chat.ggmlv3.q4_1.bin'
    llm = CTransformers(model='./app/llm/llama-2-7b-chat.ggmlv3.q8_0.bin',
                        model_type='llama',
                        config={'max_new_tokens': 256, 'temperature': 0.01})
    return llm


def load_embeddings(saved_name):
    # load the interpreted information from the local database
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'})
    db = FAISS.load_local(saved_name, embeddings)
    return db


def prepare_pre_loaded_llm(db, llm):
    # prepare the template we will use when prompting the AI
    template = """
    Use the following pieces of information to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try
    to make up an answer.
    Context: {context}
    Question: {question}
    Only return the helpful answer below and nothing else.
    Helpful answer:
    """

    # prepare a version of the llm pre-loaded with the local content
    retriever = db.as_retriever(search_kwargs={'k': 2})
    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question'])
    qa_llm = RetrievalQA.from_chain_type(llm=llm,
                                         chain_type='stuff',
                                         retriever=retriever,
                                         return_source_documents=True,
                                         chain_type_kwargs={'prompt': prompt})
    return qa_llm


def prepare_llm(dir, glob):
    db_save_name = "faiss"
    files_available = load_and_store_text(db_save_name, dir, glob)
    if not files_available:
        return None
    llm = load_language_model()
    db = load_embeddings(db_save_name)
    qa_llm = prepare_pre_loaded_llm(db, llm)
    return qa_llm


def prompt(prompt, qa_llm):
    # ask the AI chat about information in our local files
    prompt = prompt
    output = qa_llm({'query': prompt})
    return output["result"]
