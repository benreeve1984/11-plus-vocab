import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///vocab.db')

# Handle Vercel Postgres URL format
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VocabWord(Base):
    __tablename__ = "vocab_words"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_word(word: str):
    db = SessionLocal()
    try:
        existing = db.query(VocabWord).filter(VocabWord.word == word).first()
        if not existing:
            vocab_word = VocabWord(word=word.strip())
            db.add(vocab_word)
            db.commit()
            return True
        return False
    finally:
        db.close()

def remove_word(word_id: int):
    db = SessionLocal()
    try:
        word = db.query(VocabWord).filter(VocabWord.id == word_id).first()
        if word:
            db.delete(word)
            db.commit()
            return True
        return False
    finally:
        db.close()

def get_all_words():
    db = SessionLocal()
    try:
        return db.query(VocabWord).filter(VocabWord.is_active == True).all()
    finally:
        db.close()

def get_active_words():
    db = SessionLocal()
    try:
        return db.query(VocabWord).filter(VocabWord.is_active == True).all()
    finally:
        db.close()

# Initialize with default words
def init_default_words():
    default_words = [
        "aberration", "abhor", "abject", "abridge", "abstemious",
        "acumen", "adamant", "adept", "admonish", "aesthetic",
        "affable", "affluent", "alacrity", "ambiguous", "ameliorate",
        "amiable", "amorphous", "anachronism", "anecdote", "animosity",
        "anomaly", "antagonist", "apathy", "appease", "apprehension",
        "arbitrary", "archaic", "ardent", "articulate", "ascertain",
        "assiduous", "assuage", "astute", "audacious", "auspicious",
        "austere", "avarice", "aversion", "benevolent", "benign",
        "bequeath", "bereft", "blasphemy", "blithe", "bombastic"
    ]
    
    db = SessionLocal()
    try:
        for word in default_words:
            existing = db.query(VocabWord).filter(VocabWord.word == word).first()
            if not existing:
                vocab_word = VocabWord(word=word)
                db.add(vocab_word)
        db.commit()
    finally:
        db.close()

# Initialize database with default words on first run
# init_default_words()  # Commented out to prevent resetting words