import os
import re
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_engine():
    db_path = os.path.join(os.path.dirname(__file__), 'cognisearch.db')
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def fuzzy_search_docs(session, query, limit=10):
    query = query.lower()
    docs = session.query(Document).all()
    results = []
    
    for doc in docs:
        content_lower = doc.content.lower()
        title_lower = doc.title.lower()
        if query in content_lower or query in title_lower:
            # Simple snippet extraction
            snippet = ""
            if query in content_lower:
                idx = content_lower.find(query)
                start = max(0, idx - 40)
                end = min(len(doc.content), idx + len(query) + 40)
                snippet = doc.content[start:end].replace('\n', ' ')
                snippet = f"...{snippet}..."
            
            results.append({
                "id": doc.id,
                "title": doc.title,
                "snippet": snippet,
                "created_at": doc.created_at.isoformat()
            })
            
    return results[:limit]
