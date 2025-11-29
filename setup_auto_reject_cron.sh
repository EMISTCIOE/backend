#!/bin/bash
# Setup auto-reject cron job for appointment management
# Run this script to add daily auto-rejection of overdue appointments

# Get the current directory (should be the backend directory)
BACKEND_DIR=$(pwd)

# Create the cron job command
CRON_COMMAND="0 2 * * * cd $BACKEND_DIR && python manage.py auto_reject_appointments >> logs/auto_reject.log 2>&1"

echo "Setting up auto-reject cron job for VPS deployment..."
echo "Note: This is designed for VPS hosting, not local development."
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "auto_reject_appointments"; then
    echo "Auto-reject cron job already exists. Current crontab:"
    crontab -l | grep "auto_reject_appointments"
    echo ""
    echo "To remove existing cron job, run:"
    echo "crontab -l | grep -v 'auto_reject_appointments' | crontab -"
    echo ""
    echo "To update, remove the existing one and run this script again."
    exit 0
fi

# Add the cron job
echo "Adding auto-reject cron job..."
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Auto-reject cron job added successfully!"
    echo "The job will run daily at 2:00 AM to auto-reject appointments not approved within 2 days."
    echo ""
    echo "Current crontab:"
    crontab -l | grep "auto_reject_appointments"
    echo ""
    echo "Log file: $BACKEND_DIR/logs/auto_reject.log"
    echo ""
    echo "To test the command manually, run:"
    echo "python manage.py auto_reject_appointments --dry-run"
    echo ""
    echo "To remove the cron job later:"
    echo "crontab -l | grep -v 'auto_reject_appointments' | crontab -"
else
    echo "❌ Failed to add cron job. Please check your crontab setup."
    exit 1
fi