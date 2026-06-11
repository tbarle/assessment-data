-- ==========================================
-- WORKSPACES
-- ==========================================

CREATE TABLE workspaces (
    workspace_id VARCHAR(50) PRIMARY KEY,
    workspace_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- CLIENTS
-- ==========================================

CREATE TABLE clients (
    client_id BIGSERIAL PRIMARY KEY,
    workspace_id VARCHAR(50) NOT NULL,
    client_name VARCHAR(255) NOT NULL,

    CONSTRAINT fk_clients_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES workspaces(workspace_id),

    CONSTRAINT uq_client_name_per_workspace
        UNIQUE (workspace_id, client_name)
);

-- ==========================================
-- METHODOLOGIES
-- ==========================================

CREATE TABLE methodologies (
    methodology_id BIGSERIAL PRIMARY KEY,
    methodology_code VARCHAR(20) NOT NULL UNIQUE,
    methodology_name VARCHAR(255) NOT NULL,
    description TEXT
);

-- ==========================================
-- PROJECTS
-- ==========================================

CREATE TABLE projects (
    project_id VARCHAR(50) PRIMARY KEY,

    workspace_id VARCHAR(50) NOT NULL,
    client_id BIGINT NOT NULL,
    methodology_id BIGINT NOT NULL,

    project_name VARCHAR(255) NOT NULL,
    research_topic VARCHAR(255),

    start_date DATE NOT NULL,
    end_date DATE,

    sample_size INTEGER,
    budget DECIMAL(12,2),

    country_code CHAR(2),

    status VARCHAR(30) NOT NULL,

    notes TEXT,

    CONSTRAINT fk_projects_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES workspaces(workspace_id),

    CONSTRAINT fk_projects_client
        FOREIGN KEY (client_id)
        REFERENCES clients(client_id),

    CONSTRAINT fk_projects_methodology
        FOREIGN KEY (methodology_id)
        REFERENCES methodologies(methodology_id)
);

-- ==========================================
-- PANELISTS
-- ==========================================

CREATE TABLE panelists (
    panelist_id BIGINT PRIMARY KEY,

    workspace_id VARCHAR(50) NOT NULL,

    phone VARCHAR(50),

    CONSTRAINT fk_panelists_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES workspaces(workspace_id)
);

-- ==========================================
-- PANELIST EMAILS
-- ==========================================

CREATE TABLE panelist_emails (
    id BIGSERIAL PRIMARY KEY,

    panelist_id BIGINT NOT NULL,
    email_hash VARCHAR(70) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_panelist_emails_panelist
        FOREIGN KEY (panelist_id)
        REFERENCES panelists(panelist_id)
);

-- ==========================================
-- AGENTS
-- ==========================================

CREATE TABLE agents (
    agent_id BIGSERIAL PRIMARY KEY,

    workspace_id VARCHAR(50) NOT NULL,

    agent_name VARCHAR(255) NOT NULL,

    CONSTRAINT fk_agents_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES workspaces(workspace_id),

    CONSTRAINT uq_agent_workspace_name
        UNIQUE(workspace_id, agent_name)
);

-- ==========================================
-- ISSUE TYPES
-- ==========================================

CREATE TABLE issue_types (
    issue_type_id BIGSERIAL PRIMARY KEY,
    issue_name VARCHAR(100) NOT NULL UNIQUE
);

-- ==========================================
-- INTERACTIONS
-- ==========================================

CREATE TABLE interactions (
    interaction_id VARCHAR(100) PRIMARY KEY,

    workspace_id VARCHAR(50) NOT NULL,

    panelist_id BIGINT NOT NULL,
    project_id VARCHAR(50),
    agent_id BIGINT NOT NULL,
    issue_type_id BIGINT,

    interaction_date TIMESTAMP NOT NULL,

    channel VARCHAR(50),

    issue_description TEXT,
    resolution TEXT,

    resolved BOOLEAN NOT NULL,

    resolution_time_hours DECIMAL(6,2),

    satisfaction_score SMALLINT,

    CONSTRAINT fk_interactions_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES workspaces(workspace_id),

    CONSTRAINT fk_interactions_panelist
        FOREIGN KEY (panelist_id)
        REFERENCES panelists(panelist_id),

    CONSTRAINT fk_interactions_project
        FOREIGN KEY (project_id)
        REFERENCES projects(project_id),

    CONSTRAINT fk_interactions_agent
        FOREIGN KEY (agent_id)
        REFERENCES agents(agent_id),

    CONSTRAINT fk_interactions_issue_type
        FOREIGN KEY (issue_type_id)
        REFERENCES issue_types(issue_type_id),

    CONSTRAINT chk_satisfaction_score
        CHECK (
            satisfaction_score IS NULL
            OR satisfaction_score BETWEEN 1 AND 5
        )
);

-- ==========================================
-- KNOWLEDGE CATEGORIES
-- ==========================================

CREATE TABLE knowledge_categories (
    category_id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- ==========================================
-- FAQ
-- ==========================================

CREATE TABLE faq (
    id BIGSERIAL PRIMARY KEY,

    category_id BIGINT NOT NULL,

    question TEXT NOT NULL,
    answer TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_category
        FOREIGN KEY (category_id)
        REFERENCES knowledge_categories(category_id)
);

-- ==========================================
-- INDEXES FOR AI QUERIES
-- ==========================================

CREATE INDEX idx_projects_workspace_status
ON projects(workspace_id, status);

CREATE INDEX idx_projects_methodology
ON projects(methodology_id);

CREATE INDEX idx_interactions_project
ON interactions(project_id);

CREATE INDEX idx_interactions_panelist
ON interactions(panelist_id);

CREATE INDEX idx_interactions_agent
ON interactions(agent_id);

CREATE INDEX idx_interactions_date
ON interactions(interaction_date);

CREATE INDEX idx_interactions_workspace
ON interactions(workspace_id);

CREATE INDEX idx_panelists_workspace
ON panelists(workspace_id);

CREATE INDEX idx_panelist_emails_panelist
ON panelist_emails(panelist_id);

CREATE INDEX idx_faq_category
ON faq(category_id);