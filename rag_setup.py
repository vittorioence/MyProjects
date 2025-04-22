import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings # Use OpenAI embeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Load environment variables (especially OPENAI_API_KEY)
load_dotenv()

os.environ["OPENAI_API_KEY"] = "sk-srx09f05a7469b93e02a70514592c789693091c73e6Etcf4"
os.environ["OPENAI_BASE_URL"] = "https://api.gptsapi.net/v1"

def setup_vector_store(data_directory="data"):
    """Loads docs, splits, embeds, and creates a FAISS vector store."""
    print("Setting up vector store...")
    all_docs = []
    # Load all .txt files from the data directory
    for filename in os.listdir(data_directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(data_directory, filename)
            print(f"Loading: {filepath}")
            loader = TextLoader(filepath, encoding='utf-8') # Specify encoding
            all_docs.extend(loader.load())

    if not all_docs:
        print("No documents found in data directory.")
        return None

    # Split documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = text_splitter.split_documents(all_docs)
    print(f"Split into {len(documents)} chunks.")

    # Create embeddings
    # Ensure OPENAI_API_KEY is set in your environment
    # If using a proxy, you might need to configure embeddings differently
    # depending on whether the proxy supports the embedding endpoint.
    # Check your proxy documentation. If needed, pass base_url etc. here too.

    embeddings = OpenAIEmbeddings(
        # openai_api_key=os.getenv("OPENAI_API_KEY"),
        # openai_api_base=os.getenv("OPENAI_BASE_URL"),
        model="text-embedding-3-large"
        # model="text-embedding-ada-002" # You can specify the model if needed, defaults often work
        # chunk_size=... # Optional: adjust if needed and supported
    )
    print("Embeddings model loaded.")

    # Create FAISS vector store and embed documents
    try:
        vectorstore = FAISS.from_documents(documents, embeddings)
        print("Vector store created successfully.")
        # Optional: Save the vector store for later use
        vectorstore.save_local("faiss_index")
        return vectorstore
    except Exception as e:
        print(f"Error creating vector store: {e}")
        # Consider if embedding requires OPENAI_BASE_URL if using proxy
        if "base_url" in str(e).lower():
             print("Hint: Does your proxy URL handle the embeddings endpoint?")
        return None

if __name__ == "__main__":
    # Example usage: Run this script directly to create the index
    vector_store = setup_vector_store()
    if vector_store:
        print("FAISS index created (or loaded if saving/loading implemented).")
        # Optional: Test retrieval
        results = vector_store.similarity_search("What is patient autonomy?", k=1)
        print("\nTest retrieval:", results)
    else:
        print("Failed to create vector store.")