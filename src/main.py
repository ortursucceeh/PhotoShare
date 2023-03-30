from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from src.database.connect_db import get_db
#from src.routes import

app = FastAPI()

# app.include_router(tags.router, prefix='/api')
# app.include_router(notes.router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello PhotoShare"}

@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")