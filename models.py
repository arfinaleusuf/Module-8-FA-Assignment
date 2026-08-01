from database import Base
from sqlalchemy import Column, Integer, String, Float

class Movies(Base):
    __tablename__ = 'movies'

    movie_id = Column(Integer, primary_key=True)
    title = Column(String)
    director = Column(String)
    genre = Column(String)
    duration = Column(Integer)
    rating = Column(Float)
