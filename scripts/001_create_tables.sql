-- Create the research_topics table to store user research requests
CREATE TABLE IF NOT EXISTS research_topics (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the workflow_logs table to store step-by-step execution logs
CREATE TABLE IF NOT EXISTS workflow_logs (
    id SERIAL PRIMARY KEY,
    research_topic_id INTEGER REFERENCES research_topics(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    log_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the research_results table to store processed articles and summaries
CREATE TABLE IF NOT EXISTS research_results (
    id SERIAL PRIMARY KEY,
    research_topic_id INTEGER REFERENCES research_topics(id) ON DELETE CASCADE,
    article_title VARCHAR(500),
    article_url TEXT,
    article_summary TEXT,
    keywords TEXT[], -- PostgreSQL array for storing keywords
    source_api VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_research_topics_status ON research_topics(status);
CREATE INDEX IF NOT EXISTS idx_research_topics_created_at ON research_topics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_research_topic_id ON workflow_logs(research_topic_id);
CREATE INDEX IF NOT EXISTS idx_research_results_research_topic_id ON research_results(research_topic_id);
