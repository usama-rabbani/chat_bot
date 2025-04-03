from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

app = FastAPI()

# Chroma client setup
client = chromadb.PersistentClient(
    path=r"C:\Users\Dell\Downloads\chroma_db_backup (1)"  # Update this path as needed
)

# Setup collection
collection_name = "oee_shift_collection"  # Match your collection name
collections = client.list_collections()  # Returns list of strings (collection names)

# Check if collection_name exists in the list of collection names
if collection_name not in collections:
    print(f"Creating collection: {collection_name}")
    client.create_collection(name=collection_name)

collection = client.get_collection(name=collection_name)

# Pydantic models for request validation
class QueryRequest(BaseModel):
    query_text: str
    n_results: int = 3

class AnalyticalQueryRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"message": f"Collection '{collection_name}' is ready!"}

# Existing similarity query endpoint
# @app.post("/query/")
# async def query_collection(request: QueryRequest):
#     try:
#         results = collection.query(
#             query_texts=[request.query_text],
#             n_results=request.n_results
#         )
#         return results
#     except Exception as e:
#         return {"error": str(e)}

# # New endpoint for analytical queries (e.g., max OEE)
# @app.post("/ask/")
# async def ask_question(request: AnalyticalQueryRequest):
#     try:
#         # Fetch all items from the collection
#         all_items = collection.get(include=['metadatas'])

#         # Extract metadata (e.g., OEE) from all items
#         metadata_list = all_items['metadatas']

#         # Simple question parsing (expand this for more questions)
#         question = request.question.lower()
        
#         if "maximum oee" in question or "max oee" in question:
#             # Convert OEE values to float and find the max
#             oee_values = [float(item['OEE']) for item in metadata_list if item['OEE'] != '']
#             if not oee_values:
#                 return {"error": "No valid OEE values found"}
#             max_oee = max(oee_values)
#             max_item = next(item for item in metadata_list if float(item['OEE']) == max_oee)
#             return {
#                 "question": "What is the maximum OEE?",
#                 "answer": f"The maximum OEE is {max_oee}",
#                 "details": max_item
#             }
        
#         elif "morning shift" in question:
#             # Filter metadata for morning shifts
#             morning_shifts = [item for item in metadata_list if "morning" in item['ShiftDesc'].lower()]
#             if not morning_shifts:
#                 return {"answer": "No morning shift data found"}
#             return {
#                 "question": request.question,
#                 "answer": f"Found {len(morning_shifts)} morning shift records",
#                 "details": morning_shifts
#             }
        
#         else:
#             return {"error": "Unsupported question. Try 'What is the maximum OEE?' or 'Tell me about morning shifts'"}
    
#     except Exception as e:
#         return {"error": f"Failed to process question: {str(e)}"}
# @app.get("/debug/")
# async def debug_collection(limit: int = 10):
#     all_items = collection.get(include=['metadatas', 'documents', 'embeddings'])
    
#     # Slice the data to return only 'limit' number of records
#     return {
#         "total_items": min(limit, len(all_items['metadatas'])),
#         "metadatas": all_items['metadatas'][:limit],
#         "documents": all_items['documents'][:limit]
#     }








@app.get("/debug/")
async def debug_collection():
    all_items = collection.get(include=['metadatas'])
    
    # Slice the data to return only 'limit' number of records
    return {
        "total_items": len(all_items['metadatas']),
        "metadatas": all_items['metadatas'],
        "documents": all_items['documents']
    }