from celery import current_task
from celery_app import celery_app
from research_workflow import ResearchWorkflow
from database import SessionLocal
from models import ResearchTopic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="tasks.process_research_topic")
def process_research_topic(self, topic_id: int):
    """
    Celery task to process a research topic asynchronously.
    """
    db = SessionLocal()
    
    try:
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"current_step": 0, "total_steps": 5, "message": "Starting research workflow"}
        )
        
        # Get the research topic
        topic = db.query(ResearchTopic).filter(ResearchTopic.id == topic_id).first()
        if not topic:
            raise ValueError(f"Research topic with ID {topic_id} not found")
        
        logger.info(f"Starting research workflow for topic: {topic.topic}")
        
        # Initialize and execute workflow
        workflow = ResearchWorkflow(topic_id, db)
        
        # Execute workflow with progress updates
        import asyncio
        asyncio.run(workflow.execute_workflow_with_progress(self))
        
        logger.info(f"Completed research workflow for topic: {topic.topic}")
        
        return {
            "status": "completed",
            "topic_id": topic_id,
            "message": "Research workflow completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing research topic {topic_id}: {str(e)}")
        
        # Update topic status to failed
        topic = db.query(ResearchTopic).filter(ResearchTopic.id == topic_id).first()
        if topic:
            topic.status = "failed"
            db.commit()
        
        # Update task state
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "topic_id": topic_id}
        )
        
        raise
    
    finally:
        db.close()

@celery_app.task(name="tasks.cleanup_old_tasks")
def cleanup_old_tasks():
    """
    Periodic task to clean up old completed research topics.
    """
    db = SessionLocal()
    
    try:
        from datetime import datetime, timedelta
        
        # Delete research topics older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_topics = db.query(ResearchTopic).filter(
            ResearchTopic.created_at < cutoff_date,
            ResearchTopic.status.in_(["completed", "failed"])
        ).all()
        
        count = len(old_topics)
        
        for topic in old_topics:
            db.delete(topic)
        
        db.commit()
        
        logger.info(f"Cleaned up {count} old research topics")
        
        return {"cleaned_up": count, "cutoff_date": cutoff_date.isoformat()}
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise
    
    finally:
        db.close()

# Configure periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "tasks.cleanup_old_tasks",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}
