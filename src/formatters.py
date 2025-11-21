# src/formatters.py
"""
Number formatting utilities for drug dosage calculator.

This module handles:
- Dynamic decimal precision based on measurement accuracy
- Removing trailing zeros
- Unit-aware formatting
- Input validation for decimal separators

Author: Steffi
Created: 2024-11-21
"""


def format_number(value, unit=None):
    """
    Format a number with appropriate decimal precision.
    
    Why this exists: Lab equipment has limited precision. Showing 
    "499.0000 µl" is misleading because you can't measure that accurately.
    
    Parameters
    ----------
    value : float
        The number to format
    unit : str, optional
        The unit (e.g., 'µl', 'mg'). Helps determine appropriate precision.
        
    Returns
    -------
    str
        Formatted number as string (e.g., "5.23" or "250")
        
    Examples
    --------
    >>> format_number(5.234567, 'µl')
    '5.23'
    >>> format_number(25.789, 'µl')
    '25.8'
    >>> format_number(499.123, 'µl')
    '499'
    >>> format_number(0.00123, 'mg')
    '0.0012'
    
    Notes
    -----
    Precision rules based on pipette accuracy:
    - P1000 (100-1000 µl): ±1 µl → round to integer for values >100
    - P200 (20-200 µl): ±0.2 µl → 1 decimal for values 10-100
    - P20 (2-20 µl): ±0.02 µl → 2 decimals for values <10
    """
    # Handle zero or None
    if value is None or value == 0:
        return "0"
    
    abs_value = abs(value)
    
    # For very small numbers (< 0.01), use scientific notation or 4 decimals
    if abs_value < 0.01:
        # Keep 4 significant figures
        formatted = f"{value:.4g}"
    # Small values (< 10): 2 decimal places
    elif abs_value < 10:
        formatted = f"{value:.2f}"
    # Medium values (10-100): 1 decimal place
    elif abs_value < 100:
        formatted = f"{value:.1f}"
    # Large values (≥ 100): no decimal places
    else:
        formatted = f"{value:.0f}"
    
    # Remove trailing zeros and unnecessary decimal points
    # "5.20" → "5.2" → done
    # "5.00" → "5.0" → "5"
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    
    return formatted


def validate_decimal_input(input_string):
    """
    Validate that user input uses period (.) not comma (,) for decimals.
    
    Why this is needed: Python expects "5.2" but German users might type "5,2"
    because that's their system locale. This catches the error early with a
    helpful message.
    
    Parameters
    ----------
    input_string : str
        The raw input from the user
        
    Returns
    -------
    tuple of (bool, str, str)
        - is_valid: True if input is valid
        - cleaned_value: The value as a string (with . not ,)
        - error_message: Error message if invalid, empty string if valid
        
    Examples
    --------
    >>> validate_decimal_input("5.2")
    (True, "5.2", "")
    >>> validate_decimal_input("5,2")
    (False, "5,2", "Please use period (.) for decimals, not comma (,)")
    >>> validate_decimal_input("abc")
    (False, "abc", "Please enter a valid number")
    """
    # Strip whitespace
    input_string = input_string.strip()
    
    # Empty input
    if not input_string:
        return (False, "", "Please enter a value")
    
    # Check if comma is used instead of period
    if ',' in input_string:
        return (
            False, 
            input_string,
            "Please use period (.) for decimals, not comma (,)"
        )
    
    # Try to convert to float to check if it's a valid number
    try:
        float(input_string)
        return (True, input_string, "")
    except ValueError:
        return (
            False,
            input_string,
            "Please enter a valid number"
        )


def format_result_with_unit(value, unit):
    """
    Format a number with its unit, using appropriate precision.
    
    Parameters
    ----------
    value : float
        The numeric value
    unit : str
        The unit (e.g., 'µl', 'mg', 'mM')
        
    Returns
    -------
    str
        Formatted string like "5.23 mg" or "250 µl"
        
    Examples
    --------
    >>> format_result_with_unit(5.234, 'mg')
    '5.23 mg'
    >>> format_result_with_unit(499.0, 'µl')
    '499 µl'
    """
    formatted_number = format_number(value, unit)
    return f"{formatted_number} {unit}"