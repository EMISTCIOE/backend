#!/bin/bash
# Database Setup Script for TCIOE Appointment System
# Run this as postgres user or with appropriate privileges

set -e

echo "🗄️  Setting up PostgreSQL database..."
echo "====================================="

# Database configuration
DB_NAME="tcioe_db"
DB_USER="tcioe_user"
DB_PASSWORD="your_secure_password_here"  # Change this!

# Switch to postgres user and create database
sudo -u postgres psql << EOF
-- Create database user
CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Create extensions
\c $DB_NAME
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Exit
\q
EOF

# Configure PostgreSQL for production
echo "🔧 Configuring PostgreSQL..."

# Update pg_hba.conf for local connections
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP "\d+\.\d+" | head -n1)
PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

# Backup original config
cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup"

# Add local connection for tcioe_user
echo "local   $DB_NAME        $DB_USER                                md5" >> "$PG_CONFIG_DIR/pg_hba.conf"

# Restart PostgreSQL
systemctl restart postgresql
systemctl enable postgresql

echo "✅ Database setup completed!"
echo ""
echo "📝 Database Configuration:"
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER" 
echo "Database Password: $DB_PASSWORD"
echo ""
echo "⚠️  IMPORTANT: Change the default password in production!"
echo "Save these credentials for your Django settings."