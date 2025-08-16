import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Card
from .schemas import CardCreate, CardOut
from .pdf_utils import build_cards_book

# Create tables if they don't exist (beginner-friendly)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=os.getenv("APP_TITLE", "Cards Book"))

# CORS
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/cards", response_model=List[CardOut])
def list_cards(db: Session = Depends(get_db)):
    items = db.query(Card).order_by(Card.created_at.asc(), Card.id.asc()).all()
    return items

@app.post("/cards", response_model=CardOut, status_code=201)
def create_card(payload: CardCreate, db: Session = Depends(get_db)):
    content = (payload.content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    card = Card(content=content)
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

@app.delete("/cards/{card_id}", status_code=204)
def delete_card(card_id: int, db: Session = Depends(get_db)):
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    db.delete(card)
    db.commit()
    return

@app.get("/export/pdf")
def export_pdf(db: Session = Depends(get_db)):
    cards = db.query(Card).order_by(Card.created_at.asc(), Card.id.asc()).all()
    # Convert to dicts for the PDF utility
    data = [
        {"id": c.id, "content": c.content, "created_at": c.created_at}
        for c in cards
    ]
    pdf_bytes = build_cards_book(data, title=os.getenv("APP_TITLE", "Cards Book"))

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=cards_book.pdf"
        },
    )