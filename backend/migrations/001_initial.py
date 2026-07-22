"""Initial idempotent schema migration for NarrativeOS.

Run with: python migrations/001_initial.py
The model metadata is the schema source of truth for both PostgreSQL and SQLite.
"""
from app.database import Base,engine
import app.models  # registers every mapped table

def upgrade(): Base.metadata.create_all(engine)
def downgrade(): Base.metadata.drop_all(engine)

if __name__=="__main__": upgrade()
