import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.tools import load_dataset, get_dataset_summary
from backend.agent import ask_agent
import traceback

app = FastAPI(title="Data Scientist Agent API")

UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ChatRequest(BaseModel):
    question: str


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported.")

    save_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        load_dataset(str(save_path))
    except Exception as e:
        raise HTTPException(400, f"Could not read CSV: {e}")

    return {"message": "Dataset loaded successfully.", "summary": get_dataset_summary()}


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = ask_agent(req.question)

        return {
            "answer": result["answer"],
            "code": result["code"],
            "plots": result["plots"],
        }

    except Exception as e:
        # This will print the full error in your Uvicorn terminal
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )



@app.get("/health")
async def health():
    return {"status": "ok"}

