"""
Drug Dosage Calculator - Core calculation functions.

This module contains the mathematical logic for calculating drug solution
preparations in laboratory settings.
"""

from typing import Dict, Optional


def calculate_stock_from_powder(
    molecular_weight: float,
    target_concentration: float,
    target_volume: float,
    concentration_unit: str = "mM",
    volume_unit: str = "mL"
) -> Dict[str, float]:
    """
    Calculate mass of powder needed to prepare a stock solution.
    
    Parameters
    ----------
    molecular_weight : float
        Molecular weight of the compound in g/mol
    target_concentration : float
        Desired concentration in specified units
    target_volume : float
        Desired total volume in specified units
    concentration_unit : str, default="mM"
        Unit for concentration (mM, µM, M)
    volume_unit : str, default="mL"
        Unit for volume (mL, µL, L)
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'mass_mg': Mass to weigh in milligrams
        - 'mass_g': Mass to weigh in grams
        - 'volume': Volume of solvent needed
        
    Notes
    -----
    Formula: mass (g) = (concentration × volume × MW) / 1000
    Converts concentration to molarity (M) and volume to liters (L) internally.
    
    Examples
    --------
    >>> result = calculate_stock_from_powder(466.35, 10, 1, "mM", "mL")
    >>> print(f"Weigh {result['mass_mg']:.2f} mg")
    Weigh 4.66 mg
    """
    # Convert concentration to Molarity (M)
    concentration_conversion = {
        "M": 1,
        "mM": 1e-3,
        "µM": 1e-6,
        "nM": 1e-9
    }
    
    # Convert volume to Liters (L)
    volume_conversion = {
        "L": 1,
        "mL": 1e-3,
        "µL": 1e-6
    }
    
    concentration_M = target_concentration * concentration_conversion[concentration_unit]
    volume_L = target_volume * volume_conversion[volume_unit]
    
    # Calculate mass in grams: mass = concentration (mol/L) × volume (L) × MW (g/mol)
    mass_g = concentration_M * volume_L * molecular_weight
    mass_mg = mass_g * 1000
    
    return {
        'mass_mg': mass_mg,
        'mass_g': mass_g,
        'volume': target_volume,
        'volume_unit': volume_unit
    }


def calculate_dilution(
    stock_concentration: float,
    target_concentration: float,
    target_volume: float,
    concentration_unit: str = "mM",
    volume_unit: str = "mL"
) -> Dict[str, float]:
    """
    Calculate volumes needed to dilute a stock solution to working concentration.
    
    Uses the dilution formula: C1 × V1 = C2 × V2
    
    Parameters
    ----------
    stock_concentration : float
        Concentration of stock solution
    target_concentration : float
        Desired final concentration
    target_volume : float
        Desired final volume
    concentration_unit : str, default="mM"
        Unit for concentration (must be same for stock and target)
    volume_unit : str, default="mL"
        Unit for volume
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'stock_volume': Volume of stock solution to use
        - 'solvent_volume': Volume of solvent to add
        - 'total_volume': Final total volume
        - 'dilution_factor': Fold dilution (stock_conc / target_conc)
        
    Notes
    -----
    If target concentration exceeds stock concentration, returns error values.
    
    Examples
    --------
    >>> result = calculate_dilution(10, 1, 10, "mM", "mL")
    >>> print(f"Add {result['stock_volume']:.2f} mL stock to {result['solvent_volume']:.2f} mL solvent")
    Add 1.00 mL stock to 9.00 mL solvent
    """
    # Check if dilution is possible
    if target_concentration > stock_concentration:
        return {
            'error': True,
            'message': 'Target concentration cannot exceed stock concentration'
        }
    
    # C1 × V1 = C2 × V2, solve for V1 (stock volume needed)
    stock_volume = (target_concentration * target_volume) / stock_concentration
    solvent_volume = target_volume - stock_volume
    dilution_factor = stock_concentration / target_concentration
    
    return {
        'stock_volume': stock_volume,
        'solvent_volume': solvent_volume,
        'total_volume': target_volume,
        'volume_unit': volume_unit,
        'dilution_factor': dilution_factor,
        'error': False
    }


def validate_inputs(molecular_weight: Optional[float] = None,
                   concentration: Optional[float] = None,
                   volume: Optional[float] = None) -> tuple[bool, str]:
    """
    Validate numerical inputs for calculations.
    
    Parameters
    ----------
    molecular_weight : float, optional
        Molecular weight to validate
    concentration : float, optional
        Concentration to validate
    volume : float, optional
        Volume to validate
        
    Returns
    -------
    tuple[bool, str]
        (is_valid, error_message) - True if all provided values are valid
        
    Examples
    --------
    >>> is_valid, msg = validate_inputs(molecular_weight=466.35, concentration=10, volume=1)
    >>> print(is_valid)
    True
    """
    if molecular_weight is not None:
        if molecular_weight <= 0:
            return False, "Molecular weight must be positive"
    
    if concentration is not None:
        if concentration <= 0:
            return False, "Concentration must be positive"
    
    if volume is not None:
        if volume <= 0:
            return False, "Volume must be positive"
    
    return True, ""
