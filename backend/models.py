from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ResearchTopic(Base):
    __tablename__ = "research_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflow_logs = relationship("WorkflowLog", back_populates="research_topic", cascade="all, delete-orphan")
    research_results = relationship("ResearchResult", back_populates="research_topic", cascade="all, delete-orphan")

class WorkflowLog(Base):
    __tablename__ = "workflow_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    research_topic_id = Column(Integer, ForeignKey("research_topics.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    log_message = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    research_topic = relationship("ResearchTopic", back_populates="workflow_logs")

class ResearchResult(Base):
    __tablename__ = "research_results"
    
    id = Column(Integer, primary_key=True, index=True)
    research_topic_id = Column(Integer, ForeignKey("research_topics.id"), nullable=False)
    article_title = Column(String(500))
    article_url = Column(Text)
    article_summary = Column(Text)
    keywords = Column(ARRAY(String))  # PostgreSQL array for keywords
    source_api = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    research_topic = relationship("ResearchTopic", back_populates="research_results")
