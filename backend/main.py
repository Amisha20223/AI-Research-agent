from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import get_db, create_tables
from models import ResearchTopic, WorkflowLog, ResearchResult
from schemas import (
    ResearchTopicCreate, 
    ResearchTopicResponse, 
    ResearchTopicListResponse
)
from research_workflow import ResearchWorkflow
from tasks import process_research_topic

# Create FastAPI app
app = FastAPI(
    title="AI Research Agent API",
    description="An AI-powered research agent that processes topics and returns structured results",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Research Agent API is running"}

# Submit new research topic
@app.post("/research", response_model=ResearchTopicResponse)
async def create_research_topic(
    topic_data: ResearchTopicCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a new research topic and trigger the research workflow.
    """
    # Create new research topic in database
    db_topic = ResearchTopic(topic=topic_data.topic, status="queued")
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    try:
        # Queue the research task with Celery
        task = process_research_topic.delay(db_topic.id)
        
        # Update topic with task ID for tracking
        db_topic.status = "queued"
        db.commit()
        
    except Exception as e:
        # Fallback to FastAPI BackgroundTasks if Celery is not available
        workflow = ResearchWorkflow(db_topic.id, db)
        background_tasks.add_task(workflow.execute_workflow)
        db_topic.status = "processing"
        db.commit()
    
    # Return the created topic with empty logs and results initially
    return ResearchTopicResponse(
        id=db_topic.id,
        topic=db_topic.topic,
        status=db_topic.status,
        created_at=db_topic.created_at,
        updated_at=db_topic.updated_at,
        workflow_logs=[],
        research_results=[]
    )

# Get all research topics
@app.get("/research", response_model=List[ResearchTopicListResponse])
async def get_research_topics(db: Session = Depends(get_db)):
    """
    Get a list of all research topics.
    """
    topics = db.query(ResearchTopic).order_by(ResearchTopic.created_at.desc()).all()
    return [
        ResearchTopicListResponse(
            id=topic.id,
            topic=topic.topic,
            status=topic.status,
            created_at=topic.created_at
        )
        for topic in topics
    ]

# Get specific research topic with logs and results
@app.get("/research/{topic_id}", response_model=ResearchTopicResponse)
async def get_research_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific research topic including logs and results.
    """
    topic = db.query(ResearchTopic).filter(ResearchTopic.id == topic_id).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Research topic not found")
    
    return ResearchTopicResponse(
        id=topic.id,
        topic=topic.topic,
        status=topic.status,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        workflow_logs=topic.workflow_logs,
        research_results=topic.research_results
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
