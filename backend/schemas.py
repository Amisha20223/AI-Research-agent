from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Request schemas
class ResearchTopicCreate(BaseModel):
    topic: str

# Response schemas
class WorkflowLogResponse(BaseModel):
    id: int
    step_number: int
    step_name: str
    status: str
    log_message: Optional[str]
    execution_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResearchResultResponse(BaseModel):
    id: int
    article_title: Optional[str]
    article_url: Optional[str]
    article_summary: Optional[str]
    keywords: Optional[List[str]]
    source_api: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResearchTopicResponse(BaseModel):
    id: int
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime
    workflow_logs: List[WorkflowLogResponse] = []
    research_results: List[ResearchResultResponse] = []
    
    class Config:
        from_attributes = True

class ResearchTopicListResponse(BaseModel):
    id: int
    topic: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
