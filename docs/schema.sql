-- =============================================================================
-- Database Schema Definition
-- =============================================================================
-- Purpose:
-- This file defines the physical database structure for the To-Do List API.
-- It translates the logical Data Model from REQUIREMENTS.md into PostgreSQL tables.
--
-- Key Responsibilities:
-- 1. Structure: Creates tables for Lists, Tasks, and Clients.
-- 2. Integrity: Enforces Primary Keys, Foreign Keys, and Check Constraints.
-- 3. Automation: Sets up default values for UUIDs and Timestamps.
-- =============================================================================

-- Enable UUID extension (if using PostgreSQL < 13, use "uuid-ossp")
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------------------------------------------------------
-- 1. Lists Table
-- Based on Requirements Section 2.1
-- -----------------------------------------------------------------------------
CREATE TABLE lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Extracted from Auth Token (Mandatory for ownership)
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Deferred', 'Deleted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance: Fetching all lists for a specific user
CREATE INDEX idx_lists_user_id ON lists(user_id);

-- -----------------------------------------------------------------------------
-- 2. Tasks Table
-- Based on Requirements Section 2.2
-- -----------------------------------------------------------------------------
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_id UUID NOT NULL REFERENCES lists(id) ON DELETE CASCADE, -- FK to Lists
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'New' CHECK (status IN ('New', 'In-Progress', 'Completed', 'Deferred', 'Deleted')),
    priority VARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High')),
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance: Fetching all tasks for a specific list
CREATE INDEX idx_tasks_list_id ON tasks(list_id);

-- -----------------------------------------------------------------------------
-- 3. Clients Table (Authentication)
-- Based on Requirements Section 2.3
-- -----------------------------------------------------------------------------
CREATE TABLE clients (
    client_id VARCHAR(255) PRIMARY KEY,
    client_secret TEXT NOT NULL, -- Should be hashed in a real production environment
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Trigger to auto-update 'updated_at' (Optional helper)
-- -----------------------------------------------------------------------------
-- Note: In a real implementation, you would create a function and trigger 
-- to automatically update the 'updated_at' column on row modification.