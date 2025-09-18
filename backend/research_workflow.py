import asyncio
import time
import httpx
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from models import ResearchTopic, WorkflowLog, ResearchResult
from database import SessionLocal
from api_clients import ExternalAPIManager

class ResearchWorkflow:
    def __init__(self, topic_id: int, db: Session = None):
        self.topic_id = topic_id
        self.db = db or SessionLocal()
        self.api_manager = ExternalAPIManager()
        self.steps = [
            "Input Parsing",
            "Data Gathering",
            "Processing",
            "Result Persistence",
            "Completion"
        ]
    
    async def execute_workflow(self):
        """Execute the complete research workflow"""
        try:
            # Update topic status to processing
            topic = self.db.query(ResearchTopic).filter(ResearchTopic.id == self.topic_id).first()
            if not topic:
                return
            
            topic.status = "processing"
            self.db.commit()
            
            # Execute each step
            await self.step_1_input_parsing()
            await self.step_2_data_gathering()
            await self.step_3_processing()
            await self.step_4_result_persistence()
            await self.step_5_completion()
            
            # Update final status
            topic.status = "completed"
            topic.updated_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            # Handle errors and update status
            topic = self.db.query(ResearchTopic).filter(ResearchTopic.id == self.topic_id).first()
            if topic:
                topic.status = "failed"
                topic.updated_at = datetime.utcnow()
                self.db.commit()
            
            # Log the error
            self._log_step(len(self.steps) + 1, "Error", "failed", str(e), 0)
    
    async def execute_workflow_with_progress(self, celery_task=None):
        """Execute workflow with Celery progress updates"""
        try:
            # Update topic status to processing
            topic = self.db.query(ResearchTopic).filter(ResearchTopic.id == self.topic_id).first()
            if not topic:
                return
            
            topic.status = "processing"
            self.db.commit()
            
            # Execute each step with progress updates
            steps = [
                (self.step_1_input_parsing, "Input Parsing"),
                (self.step_2_data_gathering, "Data Gathering"),
                (self.step_3_processing, "Processing"),
                (self.step_4_result_persistence, "Result Persistence"),
                (self.step_5_completion, "Completion")
            ]
            
            for i, (step_func, step_name) in enumerate(steps):
                if celery_task:
                    celery_task.update_state(
                        state="PROGRESS",
                        meta={
                            "current_step": i + 1,
                            "total_steps": len(steps),
                            "message": f"Executing {step_name}",
                            "step_name": step_name
                        }
                    )
                
                await step_func()
            
            # Update final status
            topic.status = "completed"
            topic.updated_at = datetime.utcnow()
            self.db.commit()
            
            if celery_task:
                celery_task.update_state(
                    state="SUCCESS",
                    meta={
                        "current_step": len(steps),
                        "total_steps": len(steps),
                        "message": "Research workflow completed successfully"
                    }
                )
            
        except Exception as e:
            # Handle errors and update status
            topic = self.db.query(ResearchTopic).filter(ResearchTopic.id == self.topic_id).first()
            if topic:
                topic.status = "failed"
                topic.updated_at = datetime.utcnow()
                self.db.commit()
            
            # Log the error
            self._log_step(len(self.steps) + 1, "Error", "failed", str(e), 0)
            
            if celery_task:
                celery_task.update_state(
                    state="FAILURE",
                    meta={"error": str(e)}
                )
            
            raise
    
    async def step_1_input_parsing(self):
        """Step 1: Validate input and store request"""
        start_time = time.time()
        
        try:
            topic = self.db.query(ResearchTopic).filter(ResearchTopic.id == self.topic_id).first()
            
            # Validate topic length and content
            if not topic or not topic.topic.strip():
                raise ValueError("Invalid or empty research topic")
            
            if len(topic.topic) > 500:
                raise ValueError("Research topic too long (max 500 characters)")
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(1, "Input Parsing", "completed", 
                         f"Successfully validated topic: '{topic.topic[:50]}...'", execution_time)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(1, "Input Parsing", "failed", str(e), execution_time)
            raise
    
    async def step_2_data_gathering(self):
        """Step 2: Fetch relevant articles from external APIs"""
        start_time = time.time()
        
        try:
            topic = self.db.query(ResearchTopic).filter(ResearchTopic.id == self.topic_id).first()
            
            articles = await self.api_manager.fetch_articles(topic.topic, total_limit=10)
            
            # Store raw articles data temporarily
            self.raw_articles = articles
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Create detailed log message with source breakdown
            source_counts = {}
            for article in articles:
                source = article.get("source", "Unknown")
                source_counts[source] = source_counts.get(source, 0) + 1
            
            source_summary = ", ".join([f"{count} from {source}" for source, count in source_counts.items()])
            
            self._log_step(2, "Data Gathering", "completed", 
                         f"Successfully fetched {len(articles)} articles from external APIs ({source_summary})", 
                         execution_time)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(2, "Data Gathering", "failed", str(e), execution_time)
            raise
    
    async def step_3_processing(self):
        """Step 3: Extract top 5 articles, summarize each, and extract keywords"""
        start_time = time.time()
        
        try:
            # Process the top 5 articles
            top_articles = self.raw_articles[:5]
            processed_articles = []
            
            for article in top_articles:
                processed_article = {
                    "title": article["title"],
                    "url": article["url"],
                    "summary": self._generate_summary(article["content"]),
                    "keywords": self._extract_keywords(article["content"], article["title"]),
                    "source_api": article["source"]
                }
                processed_articles.append(processed_article)
            
            self.processed_articles = processed_articles
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(3, "Processing", "completed", 
                         f"Successfully processed {len(processed_articles)} articles with summaries and keywords", 
                         execution_time)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(3, "Processing", "failed", str(e), execution_time)
            raise
    
    async def step_4_result_persistence(self):
        """Step 4: Save processed results to database"""
        start_time = time.time()
        
        try:
            # Save each processed article to the database
            for article in self.processed_articles:
                result = ResearchResult(
                    research_topic_id=self.topic_id,
                    article_title=article["title"],
                    article_url=article["url"],
                    article_summary=article["summary"],
                    keywords=article["keywords"],
                    source_api=article["source_api"]
                )
                self.db.add(result)
            
            self.db.commit()
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(4, "Result Persistence", "completed", 
                         f"Successfully saved {len(self.processed_articles)} research results to database", 
                         execution_time)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(4, "Result Persistence", "failed", str(e), execution_time)
            raise
    
    async def step_5_completion(self):
        """Step 5: Final completion step"""
        start_time = time.time()
        
        try:
            # Final validation and cleanup
            results_count = self.db.query(ResearchResult).filter(
                ResearchResult.research_topic_id == self.topic_id
            ).count()
            
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(5, "Completion", "completed", 
                         f"Research workflow completed successfully with {results_count} results", 
                         execution_time)
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_step(5, "Completion", "failed", str(e), execution_time)
            raise
    
    def _log_step(self, step_number: int, step_name: str, status: str, message: str, execution_time: int):
        """Log a workflow step to the database"""
        log = WorkflowLog(
            research_topic_id=self.topic_id,
            step_number=step_number,
            step_name=step_name,
            status=status,
            log_message=message,
            execution_time_ms=execution_time
        )
        self.db.add(log)
        self.db.commit()
    
    def _generate_summary(self, content: str) -> str:
        """Generate a summary of the article content"""
        if not content:
            return "No content available for summarization."
        
        # Clean the content
        content = content.strip()
        sentences = content.split('. ')
        
        # If content is short, return as is
        if len(content) <= 200:
            return content
        
        # For longer content, take first few sentences up to ~200 characters
        summary_parts = []
        char_count = 0
        
        for sentence in sentences:
            if char_count + len(sentence) > 200:
                break
            summary_parts.append(sentence)
            char_count += len(sentence) + 2  # +2 for '. '
        
        summary = '. '.join(summary_parts)
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary or content[:200] + "..."
    
    def _extract_keywords(self, content: str, title: str = "") -> List[str]:
        """Extract keywords from the article content and title"""
        import re
        
        # Combine title and content for keyword extraction
        text = f"{title} {content}".lower()
        
        # Remove common words and punctuation
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those",
            "it", "its", "they", "them", "their", "we", "us", "our", "you", "your", "he", "him", "his",
            "she", "her", "i", "me", "my", "from", "up", "about", "into", "through", "during", "before",
            "after", "above", "below", "between", "among", "within", "without", "against", "toward",
            "towards", "upon", "across", "behind", "beyond", "under", "over", "around", "near", "far",
            "here", "there", "where", "when", "while", "until", "since", "because", "if", "unless",
            "although", "though", "however", "therefore", "thus", "hence", "moreover", "furthermore",
            "nevertheless", "nonetheless", "meanwhile", "otherwise", "instead", "rather", "quite",
            "very", "more", "most", "less", "least", "much", "many", "few", "several", "some", "any",
            "all", "both", "each", "every", "either", "neither", "one", "two", "three", "first",
            "second", "third", "last", "next", "previous", "new", "old", "good", "bad", "big", "small",
            "long", "short", "high", "low", "right", "left", "same", "different", "other", "another"
        }
        
        # Extract words (alphanumeric, 3+ characters)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]{2,}\b', text)
        
        # Filter out common words and get unique keywords
        keywords = []
        word_freq = {}
        
        for word in words:
            if word not in common_words and len(word) >= 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:8]]
        
        # If we don't have enough keywords, add some from title
        if len(keywords) < 5 and title:
            title_words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]{2,}\b', title.lower())
            for word in title_words:
                if word not in common_words and word not in keywords and len(word) >= 3:
                    keywords.append(word)
                    if len(keywords) >= 8:
                        break
        
        return keywords[:5]  # Return top 5 keywords
