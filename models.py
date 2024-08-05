from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from enums import StatusEnum


class BaseModel():
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())


class Artist(Base, BaseModel):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    songs = relationship("Song", back_populates="artist")


class Song(Base, BaseModel):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    link = Column(String, unique=True)
    original_tuning = Column(String)
    downloaded_song_path = Column(String, unique=True)
    converted_song_path = Column(String, unique=True)
    saved_downloaded = Column(Boolean, default=False)
    saved_converted = Column(Boolean, default=False)
    status = Column(String, default=StatusEnum.UNPROCESSED)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)

    artist = relationship(Artist, back_populates="songs")
