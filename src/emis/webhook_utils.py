"""
Webhook utilities for EMIS email reset requests.
"""

import logging
import requests
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def call_email_reset_webhook(
    action: str,
    primary_email: str,
    secondary_email: str,
    request_id: int,
    full_name: str,
    roll_number: str,
    phone_number: str,
    processed_by_email: str,
    notes: Optional[str] = None
) -> bool:
    """
    Call the webhook for email reset request processing.
    
    Args:
        action: 'approve' or 'reject'
        primary_email: Student's primary email
        secondary_email: Student's secondary email
        request_id: ID of the reset request
        full_name: Student's full name
        roll_number: Student's roll number
        phone_number: Student's phone number
        processed_by_email: Email of the staff who processed the request
        notes: Optional notes from the processor
        
    Returns:
        bool: True if webhook was called successfully, False otherwise

    """
    
    if not settings.EMAIL_RESET_WEBHOOK_URL:
        logger.warning("EMAIL_RESET_WEBHOOK_URL not configured, skipping webhook call")
        return False
    

    # Minimal payload required by the webhook: only college_email and secondary_email
    payload = {
        "college_email": primary_email,
        "secondary_email": secondary_email,
    }
    
    try:
        response = requests.post(
            settings.EMAIL_RESET_WEBHOOK_URL,
            json=payload,
            timeout=10,  # 10 second timeout
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TCIOE-EMIS-Backend/1.0"
            }
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully called webhook for request {request_id} with action {action}")
            return True
        else:
            logger.error(
                f"Webhook call failed for request {request_id}. "
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Webhook call timed out for request {request_id}")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to webhook URL for request {request_id}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error calling webhook for request {request_id}: {str(e)}")
        return False
