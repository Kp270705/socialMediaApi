

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from initResources.db import create_db_and_tables, engine
from models.models import Book
from typing import Annotated



@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/books/", response_model=Book)
def create_book(book:Book):
    with Session(engine) as session:
        if book.id is not None:
            existing_book = session.get(Book, book.id)
            if existing_book:
                raise HTTPException( status_code=400, detail=f"Book with id {book.id} already exists" )
            
        session.add(book)
        session.commit()
        session.refresh(book)
        return book
    
@app.get("/books/", response_model=list[Book])
def get_books():
    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id:int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with id-{book_id}, not found")
        return book
    

def say_hello(name: Annotated[str, "this is just metadata"]) -> str:
    return f"Hello {name}"