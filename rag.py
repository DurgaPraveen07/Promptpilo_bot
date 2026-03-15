import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY

# Define paths
DATA_DIR = "./data"
CHROMA_DB_DIR = "./chroma_db"

def initialize_vector_db():
    """Reads documents from the data directory and initializes the ChromaDB vector store."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created '{DATA_DIR}' directory. Please place your PDF/TXT business knowledge files there.")
        # Create a dummy file so it doesn't fail on first run if empty
        with open(os.path.join(DATA_DIR, "sample.txt"), "w") as f:
            f.write("This is a sample document about our business. We are an AI company providing automated chatbots and 24/7 customer service. You can contact us at support@example.com.")

    # Load documents from the data directory
    print("Loading documents from knowledge base...")
    loader = DirectoryLoader(DATA_DIR, glob="**/*.*", show_progress=True)
    try:
        documents = loader.load()
    except Exception as e:
        print(f"Error loading initial documents: {e}")
        documents = []

    # Split documents into easily digestible chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    # Use HuggingFace local sentence transformers for free, high-quality embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Store in local Chroma DB
    print("Creating local vector database...")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=CHROMA_DB_DIR)
    
    return vectorstore

def get_rag_chain():
    """Returns a LangChain retrieval chain equipped with the business knowledge."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Check if DB exists, else initialize
    if not os.path.exists(CHROMA_DB_DIR):
        vectorstore = initialize_vector_db()
    else:
        # Load existing DB
        vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
        
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Setup the Groq LLM
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama3-70b-8192",
        temperature=0.7
    )

    # Define the system prompt with context from the vector store
    system_prompt = (
        "You are an intelligent, helpful, and professional customer service AI assistant for our business.\n"
        "IMPORTANT: If anyone asks who created you, designed you, or made you, you MUST answer that you were created by 'Durga praveen'.\n"
        "Use the following pieces of retrieved business context to answer the user's question.\n"
        "If you don't know the answer based on the context, you can still try to help using your general knowledge, "
        "but clarify if it's outside the standard business context.\n"
        "Keep your answers concise and conversational.\n\n"
        "Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Create the RAG chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain

def query_rag(query: str, chat_history: list = None):
    """
    Queries the RAG chain with the provided user text.
    (Note: the simple chain above doesn't natively handle conversational history injection yet,
    so we can append history as context if needed, but for MVP we pass the query.)
    """
    try:
        chain = get_rag_chain()
        response = chain.invoke({"input": query})
        return response["answer"]
    except Exception as e:
        print(f"RAG Error: {e}")
        return "I'm having trouble accessing my knowledge base right now."

if __name__ == "__main__":
    # Test initialization
    print("Initializing knowledge base...")
    initialize_vector_db()
    print("Knowledge base ready!")
    
    # Test query
    res = query_rag("What does your business do?")
    print(f"RAG Response: {res}")
