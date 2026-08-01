from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from models import Movies
from database import SessionLocal, engine
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class New_movie(BaseModel):
    movie_id : int
    title : str
    director : str
    genre : Literal['action', 'comedy', 'drama', 'thriller'] = Field(description="select one from 'action', 'comedy', 'drama' and 'thriller")
    duration : int = Field(gt=0)
    rating : float = Field(ge=0.0, le=5.0, description="Enter value from 0 to 5")

@app.get('/movies')
def movies(db: db_dependency):
    return db.query(Movies).all()


@app.get('/movies/{movie_id}')
def single_movie(db: db_dependency, movie_id: int):
    single_movie = db.query(Movies).filter(Movies.movie_id == movie_id).first()
    if single_movie is not None:
        return single_movie
    else:
        raise HTTPException(status_code=404, detail='Movie do not Found')


@app.post('/create_movies')
def new_movie(db: db_dependency, new_movie: New_movie):
    existing_movie = db.query(Movies).filter(Movies.movie_id == new_movie.movie_id).first()

    if existing_movie is None:
        new_movie_model = Movies(**new_movie.model_dump())
        db.add(new_movie_model)
        db.commit()
        return JSONResponse(status_code=201, content={'message':'New Movie Added Successfully'})
    else:
        raise HTTPException(status_code=400, detail='This Movie all ready Exist')
