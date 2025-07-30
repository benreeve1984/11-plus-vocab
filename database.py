import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Use Vercel Postgres URL (try multiple possible env vars) or fallback to local SQLite
DATABASE_URL = (
    os.getenv('POSTGRES_URL') or 
    os.getenv('DATABASE_URL') or 
    os.getenv('POSTGRES_URL_NON_POOLING') or
    'sqlite:///vocab.db'
)

print(f"Database URL being used: {DATABASE_URL[:50]}...")  # Print first 50 chars for debugging

# Handle Vercel Postgres URL format
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create engine with proper connection settings for Vercel Postgres
if 'postgresql://' in DATABASE_URL:
    # Vercel Postgres settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections after 1 hour
        connect_args={"sslmode": "require"}  # SSL for Postgres
    )
else:
    # Local SQLite settings
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VocabWord(Base):
    __tablename__ = "vocab_words"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Create tables with error handling
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    
    # Test the connection by trying a simple query
    db = SessionLocal()
    try:
        db.execute('SELECT 1')
        print("Database connection test successful")
    except Exception as test_e:
        print(f"Database connection test failed: {test_e}")
    finally:
        db.close()
        
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print(f"Database URL being attempted: {DATABASE_URL}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_word(word: str):
    try:
        db = SessionLocal()
        try:
            existing = db.query(VocabWord).filter(VocabWord.word == word).first()
            if not existing:
                vocab_word = VocabWord(word=word.strip())
                db.add(vocab_word)
                db.commit()
                print(f"Successfully added word: {word}")
                return True
            print(f"Word already exists: {word}")
            return False
        finally:
            db.close()
    except Exception as e:
        print(f"Error adding word '{word}': {e}")
        return False

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
    db = SessionLocal()
    try:
        # Check if database already has words
        existing_count = db.query(VocabWord).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} words, skipping initialization")
            return
            
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
        
        print(f"Initializing database with {len(default_words)} default words")
        for word in default_words:
            vocab_word = VocabWord(word=word)
            db.add(vocab_word)
        db.commit()
        print("Default words added successfully")
    finally:
        db.close()

# Initialize database with default words on first run only
try:
    init_default_words()
except Exception as e:
    print(f"Warning: Could not initialize default words: {e}")