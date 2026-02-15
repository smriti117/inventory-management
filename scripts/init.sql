
-- Create user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'inventory_user'
   ) THEN
      CREATE USER inventory_user WITH PASSWORD 'inventory_pass';
   END IF;
END
$do$;

-- Create database if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = 'inventory_db'
   ) THEN
      CREATE DATABASE inventory_db OWNER inventory_user;
   END IF;
END
$do$;

-- Set timezone
ALTER DATABASE inventory_db SET timezone = 'UTC';
