from fastapi import FastAPI, Depends, HTTPException,Query
from sqlalchemy.orm import Session
import models
from models import Movies
from database import SessionLocal, engine
from typing import Annotated, Literal,Optional
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from sqlalchemy import asc, desc


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

class Update_movie(BaseModel):
    title : Optional[str] = None
    director : Optional[str] = Field(default=None,)
    genre : Optional[Literal['action', 'comedy', 'drama', 'thriller']] = None
    duration : Optional[int] = Field(default=None, gt=0)
    rating : Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Enter value from 0 to 5")
 

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

@app.put('/movies/{movie_id}')
def update_data(db: db_dependency, movie_id: int, update_movie: Update_movie):
    movie = db.query(Movies).filter(Movies.movie_id == movie_id).first()

    if movie is None:
        raise HTTPException(status_code=404, detail='Movie Not found')
    update_data = update_movie.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(movie,key,value)

    db.commit()

    return JSONResponse(status_code=200, content={'messege':'Movie Uploaded Successfully'})
@app.delete('/delete/{movie_id}')
def delete_movie(db:db_dependency, movie_id: int):
    movie = db.query(Movies).filter(Movies.movie_id == movie_id).first()

    if movie is None:
        raise HTTPException(status_code=404, detail='Movie not Found')

    db.query(Movies).filter(Movies.movie_id == movie_id).delete()

    db.commit()

    return JSONResponse(status_code=200, content={'messege':'Movie deleted Successfully'})

@app.get('/sort')
def sorted_by(db:db_dependency ,sort_by: str = Query(default='rating', description='Sort on the basis of rating or duration'), order:str= Query(default='desc', description='Select between asc and desc')):
    valid = ['rating', 'duration']

    if sort_by not in valid:
        raise HTTPException(status_code=400, detail=f'Invalid field, select from{valid}')

    if order not in['asc','desc']:
        raise HTTPException(status_code=400,detail='order must be acs or desc')

    data = getattr(Movies, sort_by)

    if order == 'asc':
        movies = db.query(Movies).order_by(asc(data)).all()

    else :
        movies = db.query(Movies).order_by(desc(data)).all()

    return movies