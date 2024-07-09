from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from item import SessionLocal, Item

app = FastAPI()


class ItemCreate(BaseModel):
    user: str
    categories: list[str]
    sentiment: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/items/")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(user=item.user, categories=item.categories[0], sentiment=item.sentiment)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
    return {"message": "hello"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
