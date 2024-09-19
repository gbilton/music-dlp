from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from sqlalchemy.orm import Session

from enums import StatusEnum
from models import Artist, Song
from schemas import ArtistCreateSchema, ArtistSchema, RefreshSchema, SongCreateSchema, SongSchema
from db import get_db, init_db
from services import SongProcessing


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, you can specify a list of origins instead
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Define pitch mapping
PITCH_MAPPING = {
    "Eb": "+100",
    "E": "-100",
}

class UrlInput(BaseModel):
    url: str
    filename: str
    pitch: str


@app.get("/")
async def health_check():
    return {"health": "OK"}


@app.post("/refresh")
async def refresh(refresh_schema: RefreshSchema, db: Session = Depends(get_db)):
    song_processing = SongProcessing()

    songs = db.query(Song).all()
    for song in songs:
        if song.status != StatusEnum.SUCCESS or refresh_schema.restore:
            song_processing.refresh(song=song)
            db.commit()


# Get all artists
@app.get("/artist", response_model=List[ArtistSchema])
async def get_artists(db: Session = Depends(get_db)):
    return db.query(Artist).all()


# Add a new artist
@app.post("/artist", response_model=ArtistSchema)
async def add_artist(artist: ArtistCreateSchema, db: Session = Depends(get_db)):
    db_artist = Artist(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist


# Delete an artist
@app.delete("/artist/{artist_id}", response_model=ArtistSchema)
async def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    for song in artist.songs:
        db.delete(song)

    db.delete(artist)
    db.commit()
    return artist


# Get all songs
@app.get("/song", response_model=List[SongSchema])
async def get_songs(db: Session = Depends(get_db)):
    return db.query(Song).all()


# Add a new song
@app.post("/song", response_model=SongSchema)
async def add_song(song: SongCreateSchema, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == song.artist_id).first()
    if not artist:
        raise HTTPException(400, detail="Artist not found.")

    db_song = Song(
        name=song.name,
        original_tuning=song.original_tuning,
        link=song.link,
        artist=artist,
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


# Delete a song
@app.delete("/song/{song_id}", response_model=SongSchema)
async def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)

    song_processing = SongProcessing()
    song_processing.delete_song(
        downloaded_song_path=song.downloaded_song_path,
        converted_song_path=song.converted_song_path
        )

    db.commit()
    return song


# Call this function once to create tables
init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
