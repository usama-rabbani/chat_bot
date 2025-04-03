# from fpdf import FPDF

# # Create 5 empty PDF files
# file_names = [
#     "Program_Executed_Report.pdf",
#     "System_Executed_Report.pdf",
#     "Unit_Endorsed_Report.pdf",
#     "User_Signed_Report.pdf",
#     "Final_Summary_Report.pdf"
# ]

# # Loop through and create PDFs
# for name in file_names:
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.cell(200, 10, txt="", ln=True, align="C")  # Empty content
#     pdf.output(name)

# print("PDF files created successfully!")

from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

app = FastAPI()

# Chroma client setup
client = chromadb.PersistentClient(
    path=r"C:\Users\Dell\Downloads\2cbf3e21-ea74-4942-94cb-d40d8856a1c3"
)

# Setup collection
collection_name = "my_collection"
collections = client.list_collections()

if collection_name not in [c.name for c in collections]:  # Fixed this line
    print(f"Creating collection: {collection_name}")
    client.create_collection(name=collection_name)

collection = client.get_collection(name=collection_name)

# Pydantic models for request validation
class AddDocumentRequest(BaseModel):
    ids: list[str]
    documents: list[str]
    metadatas: list[dict] = []  # Optional metadata

class QueryRequest(BaseModel):
    query_text: str
    n_results: int = 3

# GET Root endpoint
@app.get("/")
async def root():
    return {"message": f"Collection '{collection_name}' is ready!"}

# POST: Add documents
@app.post("/add_documents/")
@app.post("/add_documents")
async def add_documents(request: AddDocumentRequest):
    try:
        collection.add(
            ids=request.ids,
            documents=request.documents,
            metadatas=request.metadatas if request.metadatas else None
        )
        return {"message": "Documents added successfully!"}
    except Exception as e:
        return {"error": str(e)}

# POST: Query documents (existing endpoint)
@app.post("/query/")
async def query_collection(request: QueryRequest):
    try:
        results = collection.query(
            query_texts=[request.query_text],
            n_results=request.n_results
        )
        return results
    except Exception as e:
        return {"error": str(e)}

# ✅ NEW GET Endpoint for Power Query (GET request)
@app.get("/query/")
async def query_collection_get(query_text: str, n_results: int = 3):
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
    except Exception as e:
        return {"error": str(e)}
