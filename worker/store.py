from logger import setup_logger
from models import ArtistData, SongData
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = setup_logger(__name__)

CREATE_ARTISTS_TABLE = """
    CREATE TABLE IF NOT EXISTS artists (
        id SERIAL PRIMARY KEY,
        external_artist_id VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

CREATE_SONGS_TABLE = """
    CREATE TABLE IF NOT EXISTS songs (
        id SERIAL PRIMARY KEY,
        external_song_id VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        external_artist_id VARCHAR NOT NULL,
        title VARCHAR NOT NULL,
        album VARCHAR,
        release_date DATE,
        lyrics_url VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (external_artist_id) REFERENCES artists(external_artist_id)
    )
"""

CREATE_LYRICS_TABLE = """
    CREATE TABLE IF NOT EXISTS lyrics (
        id SERIAL PRIMARY KEY,
        external_song_id VARCHAR NOT NULL,
        lyrics TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (external_song_id) REFERENCES songs(external_song_id),
        UNIQUE(song_id)
    )
"""

INSERT_ARTIST = """
    INSERT INTO artists (external_artist_id, name) 
    VALUES (:external_artist_id, :name)
    ON CONFLICT (external_artist_id) DO NOTHING
"""

INSERT_SONG = """
    INSERT INTO songs (
        external_song_id, name, external_artist_id, title, 
        album, release_date, lyrics_url
    ) 
    VALUES (
        :external_song_id, :name, :external_artist_id, :title,
        :album, :release_date, :lyrics_url
    )
    ON CONFLICT (external_song_id) DO NOTHING
"""

INSERT_LYRICS = """
    INSERT INTO lyrics (external_song_id, lyrics) 
    VALUES (:external_song_id, :lyrics)
    ON CONFLICT (external_song_id) DO NOTHING
"""


class Store:
    def __init__(self, database_url: str):
        self.engine: Engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        self._create_tables()

    def _create_tables(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text(CREATE_ARTISTS_TABLE))
                conn.execute(text(CREATE_SONGS_TABLE))
                conn.execute(text(CREATE_LYRICS_TABLE))
                conn.commit()
                logger.info("✅ Database tables created/verified successfully")

        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise

    def save_artists(self, artists: list[ArtistData]):
        if not artists:
            return

        try:
            with self.engine.connect() as conn:
                for artist in artists:
                    conn.execute(
                        text(INSERT_ARTIST),
                        {"external_artist_id": artist.external_artist_id, "name": artist.name},
                    )
                conn.commit()
                logger.info(f"✅ Saved {len(artists)} artists to database")

        except SQLAlchemyError as e:
            logger.error(f"❌ Error saving artists: {e}")
            raise

    def save_songs(self, songs: list[SongData]):
        if not songs:
            return

        try:
            with self.engine.connect() as conn:
                for song in songs:
                    conn.execute(
                        text(INSERT_SONG),
                        {
                            "external_song_id": song.external_song_id,
                            "name": song.name,
                            "external_artist_id": song.external_artist_id,
                            "title": song.title,
                            "album": song.album,
                            "release_date": song.release_date,
                            "lyrics_url": song.lyrics_url,
                        },
                    )
                conn.commit()
                logger.info(f"✅ Saved {len(songs)} songs to database")

        except SQLAlchemyError as e:
            logger.error(f"❌ Error saving songs: {e}")
            raise

    def save_lyrics(self, external_song_id: str, lyrics: str):
        if not lyrics:
            return

        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text(INSERT_LYRICS),
                    {"external_song_id": external_song_id, "lyrics": lyrics},
                )
                conn.commit()

        except SQLAlchemyError as e:
            logger.error(f"❌ Error saving lyrics for external_song_id {external_song_id}: {e}")
            raise

    def close(self):
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
