import re
from typing import Optional


def validate_mobile_number(mobile_number: str) -> tuple[bool, Optional[str]]:
    """
    Validate Indian mobile number format.
    
    Rules:
    - Must be exactly 10 digits
    - Should start with 6, 7, 8, or 9 (valid Indian mobile prefixes)
    - Should not contain spaces, dashes, or other characters
    
    Args:
        mobile_number: The mobile number to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not mobile_number:
        return False, "Mobile number is required"
    
    # Remove any spaces, dashes, or other separators
    cleaned_number = re.sub(r'[\s\-\(\)]', '', mobile_number)
    
    # Check if it's exactly 10 digits
    if not cleaned_number.isdigit():
        return False, "Mobile number must contain only digits"
    
    if len(cleaned_number) != 10:
        return False, "Mobile number must be exactly 10 digits"
    
    # Check if it starts with valid Indian mobile prefixes
    valid_prefixes = ['6', '7', '8', '9']
    if cleaned_number[0] not in valid_prefixes:
        return False, "Mobile number must start with 6, 7, 8, or 9"
    
    return True, None


def validate_aadhar_number(aadhar_number: str) -> tuple[bool, Optional[str]]:
    """
    Validate Indian Aadhar card number format.
    
    Rules:
    - Must be exactly 12 digits
    - Should not contain spaces, dashes, or other characters
    - Should not be all zeros or all ones (invalid patterns)
    
    Args:
        aadhar_number: The Aadhar number to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not aadhar_number:
        return False, "Aadhar number is required"
    
    # Remove any spaces, dashes, or other separators
    cleaned_number = re.sub(r'[\s\-]', '', aadhar_number)
    
    # Check if it's exactly 12 digits
    if not cleaned_number.isdigit():
        return False, "Aadhar number must contain only digits"
    
    if len(cleaned_number) != 12:
        return False, "Aadhar number must be exactly 12 digits"
    
    # Check for invalid patterns (all zeros, all ones, etc.)
    if cleaned_number == '000000000000':
        return False, "Aadhar number cannot be all zeros"
    
    if cleaned_number == '111111111111':
        return False, "Aadhar number cannot be all ones"
    
    # Check for other obvious invalid patterns
    if cleaned_number.startswith('0000') or cleaned_number.startswith('1111'):
        return False, "Aadhar number contains invalid pattern"
    
    return True, None


def format_mobile_number(mobile_number: str) -> str:
    """
    Format mobile number by removing spaces, dashes, and other separators.
    
    Args:
        mobile_number: The mobile number to format
        
    Returns:
        str: Formatted mobile number
    """
    return re.sub(r'[\s\-\(\)]', '', mobile_number)


def format_aadhar_number(aadhar_number: str) -> str:
    """
    Format Aadhar number by removing spaces and dashes.
    
    Args:
        aadhar_number: The Aadhar number to format
        
    Returns:
        str: Formatted Aadhar number
    """
    return re.sub(r'[\s\-]', '', aadhar_number) 