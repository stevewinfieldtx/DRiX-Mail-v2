-- Canonical schema is expressed in app/models.py and created idempotently at boot.
-- Production teams can stamp this file as migration 001; SQLAlchemy owns exact
-- PostgreSQL type rendering to keep local SQLite tests and PostgreSQL aligned.
-- Tables: clients, campaigns, prospects, evidence, emails.
SELECT 1;
