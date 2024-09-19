from pydantic import BaseModel
from typing import List

from enums import TuningEnum


class ArtistBaseSchema(BaseModel):
    name: str


class ArtistCreateSchema(ArtistBaseSchema):
    pass


class ArtistSchema(ArtistBaseSchema):
    id: int
    songs: List["SongSchema"] = []  

    class Config:
        from_attributes = True


class SongBaseSchema(BaseModel):
    name: str
    link: str


class SongCreateSchema(SongBaseSchema):
    artist_id: int
    original_tuning: TuningEnum  


class SongSchema(SongBaseSchema):
    id: int
    original_tuning: str

    class Config:
        from_attributes = True


class RefreshSchema(BaseModel):
    restore: bool = False
