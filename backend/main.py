from fastapi import FastAPI, Depends, Query
from sqlmodel import Session, select
from db.models import PromptResult, SQLModel
from db.session import engine, get_session
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from agents.run_snapshot import run_snapshot_chatgpt

app = FastAPI()

url = "https://chatgpt.com/" 
dataset_id = "gd_m7aof0k82r803d5bjm"    # chatgpt.com

# Allow frontend (localhost:3000) to talk to backend (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables on startup    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    SQLModel.metadata.create_all(engine)
    print("Database tables created")
    yield
    # Optional shutdown code
    print("App shutting down")

@app.post("/api/query")
async def query_agents(prompt: str, session: Session = Depends(get_session)):
    results =  await run_snapshot_chatgpt(url, prompt, dataset_id) 
    if results is None:
        return results
    record = PromptResult(prompt=prompt, results=results[0]["answer_text_markdown"])
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@app.get("/api/results")
def get_results(page: int = Query(1, ge=1),
                page_size: int = Query(10, ge=1, le=100),
                session: Session = Depends(get_session)):
    offset = (page - 1) * page_size
    
    statement = (
        select(PromptResult)
        .order_by(PromptResult.createdAt.desc()) # type: ignore[arg-type]
        .offset(offset)
        .limit(page_size)
    )
    results = session.exec(statement).all()
    
    # total count query
    from sqlalchemy import func
    total = session.exec(select(func.count()).select_from(PromptResult)).one()
    
    total_pages = (total + page_size - 1) // page_size  # integer ceil

    return {
        "results": [r.model_dump() for r in results],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

