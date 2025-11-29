#!/bin/bash
# VPS Production Setup Script for TCIOE Appointment System
# Run this script as root or with sudo privileges

set -e

echo "🚀 Setting up TCIOE Appointment System on VPS..."
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git curl

# Create application user
echo "👤 Creating application user..."
if ! id "tcioe" &>/dev/null; then
    useradd -m -s /bin/bash tcioe
    usermod -aG sudo tcioe
fi

# Create application directories
echo "📁 Creating application directories..."
mkdir -p /var/www/tcioe
mkdir -p /var/log/tcioe
mkdir -p /etc/tcioe

# Set ownership
chown -R tcioe:tcioe /var/www/tcioe
chown -R tcioe:tcioe /var/log/tcioe

echo "✅ Basic VPS setup completed!"
echo ""
echo "Next steps:"
echo "1. Run the database setup script"
echo "2. Deploy your Django backend"
echo "3. Configure Nginx"
echo "4. Set up SSL certificates"
echo "5. Configure appointment automation"