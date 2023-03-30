import chromadb
from chromadb.config import Settings
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma-data"))
collection = client.list_collections()
collection = client.get_collection("langchain")
items = collection.get()
print(items)
