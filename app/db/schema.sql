CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding_vector vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX embedding_vector_idx ON documents 
USING ivfflat (embedding_vector vector_cosine_ops)
WITH (lists = 100); 