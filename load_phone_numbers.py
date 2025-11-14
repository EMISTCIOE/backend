#!/usr/bin/env python
"""
Script to load initial phone numbers data into the database.
Run this script after running migrations.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from src.contact.models import PhoneNumber

User = get_user_model()

def load_phone_numbers():
    """Load initial phone numbers data"""
    
    # Get or create a user for the created_by field
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@tcioe.edu.np',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    phone_numbers_data = [
        {"department_name": "Campus", "phone_number": "+977-1-5971474", "description": "Main campus contact number", "display_order": 1},
        {"department_name": "Admin Section", "phone_number": "+977-1-5971475", "description": "Administrative section contact", "display_order": 2},
        {"department_name": "Account Section", "phone_number": "+977-1-5971476", "description": "Accounts and finance section", "display_order": 3},
        {"department_name": "Store", "phone_number": "+977-1-5971477", "description": "Store and inventory section", "display_order": 4},
        {"department_name": "Library", "phone_number": "+977-1-5971478", "description": "Library services contact", "display_order": 5},
        {"department_name": "EMIS", "phone_number": "+977-1-5971479", "description": "Educational Management Information System", "display_order": 6},
        {"department_name": "Exam Section", "phone_number": "+977-1-5971480", "description": "Examination section contact", "display_order": 7},
        {"department_name": "Civil Department", "phone_number": "+977-1-5971481", "description": "Civil Engineering Department", "display_order": 8},
        {"department_name": "Electronics and Computer Department", "phone_number": "+977-1-5971482", "description": "Electronics and Computer Engineering Department", "display_order": 9},
        {"department_name": "Automobile and Mechanical Department", "phone_number": "+977-1-5971483", "description": "Automobile and Mechanical Engineering Department", "display_order": 10},
        {"department_name": "Industrial Department", "phone_number": "+977-1-5971484", "description": "Industrial Engineering Department", "display_order": 11},
        {"department_name": "Architecture Department", "phone_number": "+977-1-5971485", "description": "Architecture Department", "display_order": 12},
    ]
    
    created_count = 0
    updated_count = 0
    
    for data in phone_numbers_data:
        obj, created = PhoneNumber.objects.get_or_create(
            department_name=data['department_name'],
            defaults={
                'phone_number': data['phone_number'],
                'description': data['description'],
                'display_order': data['display_order'],
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )
        
        if created:
            created_count += 1
            print(f"Created: {obj.department_name} - {obj.phone_number}")
        else:
            # Update existing record
            obj.phone_number = data['phone_number']
            obj.description = data['description']
            obj.display_order = data['display_order']
            obj.updated_by = admin_user
            obj.save()
            updated_count += 1
            print(f"Updated: {obj.department_name} - {obj.phone_number}")
    
    print(f"\nSummary:")
    print(f"Created: {created_count} phone numbers")
    print(f"Updated: {updated_count} phone numbers")
    print(f"Total: {PhoneNumber.objects.count()} phone numbers in database")

if __name__ == '__main__':
    print("Loading phone numbers data...")
    load_phone_numbers()
    print("Phone numbers data loaded successfully!")