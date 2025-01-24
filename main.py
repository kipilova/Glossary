import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import uvicorn

app = FastAPI()

# Настройки базы данных
DATABASE_URL = "sqlite:///./glossary.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Модель базы данных
class GlossaryTerm(Base):
    __tablename__ = "glossary"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Удалена аннотация "Column(String)"
    description = Column(String)

# Создание таблицы
Base.metadata.create_all(bind=engine)

# Pydantic модель
class TermCreate(BaseModel):
    name: str
    description: str

class TermResponse(TermCreate):
    id: int

    class Config:
        from_attributes = True  # Для совместимости с Pydantic v2

# Получение базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD эндпоинты
@app.post("/terms", response_model=TermResponse)
def create_term(term: TermCreate, db: Session = Depends(get_db)):
    db_term = db.query(GlossaryTerm).filter(GlossaryTerm.name == term.name).first()
    if db_term:
        raise HTTPException(status_code=400, detail="Term already exists")
    new_term = GlossaryTerm(name=term.name, description=term.description)
    db.add(new_term)
    db.commit()
    db.refresh(new_term)
    return new_term

@app.get("/terms/", response_model=List[TermResponse])
def get_all_terms(db: Session = Depends(get_db)):
    return db.query(GlossaryTerm).all()

@app.get("/terms/{term_id}", response_model=TermResponse)
def get_term(term_id: int, db: Session = Depends(get_db)):
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return term

@app.put("/terms/{term_id}", response_model=TermResponse)
def update_term(term_id: int, updated_term: TermCreate, db: Session = Depends(get_db)):
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    term.name = updated_term.name
    term.description = updated_term.description
    db.commit()
    db.refresh(term)
    return term

@app.delete("/terms/{term_id}", response_model=dict)
def delete_term(term_id: int, db: Session = Depends(get_db)):
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    db.delete(term)
    db.commit()
    return {"detail": f"Term with ID {term_id} has been deleted"}

# Тестовый маршрут
@app.get("/")
def read_root():
    return {"message": "Welcome to the Glossary API"}

if __name__ == "__main__":
    print("Starting the FastAPI server...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
