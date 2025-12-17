"""
PubChem API Integration Module for Drug Calculator.

This module provides functionality to lookup molecular weights and chemical
properties from the PubChem database using the PubChemPy library.

Author: Steffi
Created: 2025
"""

import pubchempy as pcp
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime


class ChemicalLookupError(Exception):
    """Custom exception for chemical database lookup errors."""
    pass


class PubChemAPI:
    """
    Interface to PubChem database for chemical property lookup.
    
    This class provides methods to search for compounds by various identifiers
    and retrieve molecular weights and other properties. Includes caching for
    offline access and faster repeated lookups.
    
    Attributes
    ----------
    cache_file : Path
        Path to JSON file storing cached lookup results
    cache : dict
        In-memory cache of lookup results
    """
    
    def __init__(self, cache_file: Optional[Path] = None):
        """
        Initialize PubChem API interface with optional caching.
        
        Parameters
        ----------
        cache_file : Path, optional
            Path to cache file. If None, uses default location in user directory.
            
        Examples
        --------
        >>> api = PubChemAPI()
        >>> result = api.lookup("Cisplatin")
        >>> print(result['molecular_weight'])
        300.1
        """
        if cache_file is None:
            cache_file = Path.home() / ".drug_calculator" / "pubchem_cache.json"
        
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """
        Load cached results from disk.
        
        Returns
        -------
        dict
            Dictionary of cached lookup results
        """
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load cache file: {e}")
            return {}
    
    def _save_cache(self):
        """Save current cache to disk."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save cache file: {e}")
    
    def _create_cache_key(self, identifier: str, id_type: str) -> str:
        """
        Create unique cache key for identifier.
        
        Parameters
        ----------
        identifier : str
            Chemical identifier
        id_type : str
            Type of identifier
            
        Returns
        -------
        str
            Cache key
        """
        return f"{id_type}:{identifier.strip().lower()}"
    
    def detect_identifier_type(self, identifier: str) -> str:
        """
        Automatically detect the type of chemical identifier.
        
        Parameters
        ----------
        identifier : str
            Chemical identifier string
            
        Returns
        -------
        str
            Detected identifier type: 'name', 'cid', 'formula', or 'inchi'
            
        Examples
        --------
        >>> api = PubChemAPI()
        >>> api.detect_identifier_type("50-18-0")
        'name'
        >>> api.detect_identifier_type("2244")
        'cid'
        >>> api.detect_identifier_type("Cisplatin")
        'name'
        
        Notes
        -----
        - CAS numbers (XX-XX-X format) are searched as names
        - Pure numbers are treated as PubChem CIDs
        - ChEMBL IDs are searched as names (PubChem has cross-references)
        - Everything else is treated as a name search
        """
        identifier = identifier.strip()
        
        # CAS number pattern: digits separated by hyphens
        if re.match(r'^\d{1,7}-\d{2}-\d$', identifier):
            return 'name'  # PubChem accepts CAS as name search
        
        # Pure number: likely PubChem CID
        if identifier.isdigit():
            return 'cid'
        
        # ChEMBL ID pattern
        if re.match(r'^CHEMBL\d+$', identifier.upper()):
            return 'name'  # Search as name, PubChem has ChEMBL crossrefs
        
        # InChI pattern
        if identifier.startswith('InChI='):
            return 'inchi'
        
        # Default: treat as name
        return 'name'
    
    def lookup(self, identifier: str, id_type: Optional[str] = None,
               use_cache: bool = True) -> Optional[Dict]:
        """
        Look up compound information from PubChem.
        
        Parameters
        ----------
        identifier : str
            Chemical identifier (name, CAS, CID, etc.)
        id_type : str, optional
            Type of identifier. If None, will auto-detect.
            Valid types: "name", "cid", "formula", "smiles", "inchi", "inchikey"
        use_cache : bool, default=True
            Whether to use cached results if available
            
        Returns
        -------
        dict or None
            Dictionary containing compound properties if found, None otherwise.
            Keys include:
            - 'molecular_weight': float
            - 'molecular_formula': str
            - 'iupac_name': str
            - 'cid': int (PubChem Compound ID)
            - 'synonyms': list of str (common names)
            - 'connectivity_smiles': str
            - 'cached': bool (whether from cache)
            - 'lookup_date': str (ISO format datetime)
            
        Examples
        --------
        >>> api = PubChemAPI()
        >>> result = api.lookup("Cisplatin")
        >>> print(f"MW: {result['molecular_weight']} g/mol")
        MW: 300.1 g/mol
        
        >>> result = api.lookup("50-18-0")  # CAS number
        >>> print(result['molecular_formula'])
        C6H12Cl2N2Pt
        
        >>> result = api.lookup("2244")  # PubChem CID (Aspirin)
        >>> print(result['iupac_name'])
        2-acetoxybenzoic acid
        
        Notes
        -----
        Results are automatically cached to speed up repeated lookups and
        enable offline access. Cache is stored in ~/.drug_calculator/
        """
        if not identifier or not identifier.strip():
            return None
        
        # Auto-detect identifier type if not specified
        if id_type is None:
            id_type = self.detect_identifier_type(identifier)
        
        # Check cache first
        cache_key = self._create_cache_key(identifier, id_type)
        if use_cache and cache_key in self.cache:
            result = self.cache[cache_key].copy()
            result['cached'] = True
            return result
        
        # Query PubChem API
        try:
            compounds = pcp.get_compounds(identifier, id_type)
            
            if not compounds:
                return None
            
            # Get first result (most relevant)
            compound = compounds[0]
            
            # Build result dictionary
            result = {
                'molecular_weight': float(compound.molecular_weight),
                'molecular_formula': compound.molecular_formula,
                'iupac_name': compound.iupac_name,
                'cid': compound.cid,
                'synonyms': compound.synonyms[:10] if compound.synonyms else [],
                'connectivity_smiles': compound.connectivity_smiles,  # Updated from deprecated canonical_smiles
                'cached': False,
                'lookup_date': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = result.copy()
            self._save_cache()
            
            return result
            
        except Exception as e:
            raise ChemicalLookupError(
                f"Error looking up '{identifier}' as {id_type}: {str(e)}"
            )
    
    def robust_lookup(self, identifier: str) -> Tuple[Optional[Dict], List[str]]:
        """
        Try multiple strategies to find a compound.
        
        This method attempts several search strategies in order:
        1. Try identifier as-is with auto-detected type
        2. Try with cleaned identifier (remove spaces, special characters)
        3. Try different identifier types if applicable
        
        Parameters
        ----------
        identifier : str
            Chemical identifier to search for
            
        Returns
        -------
        tuple
            (result_dict, attempted_strategies)
            - result_dict: Dict with compound info if found, None otherwise
            - attempted_strategies: List of strategies tried (for debugging)
            
        Examples
        --------
        >>> api = PubChemAPI()
        >>> result, strategies = api.robust_lookup("Platinol")
        >>> print(result['synonyms'][:3])
        ['Cisplatin', 'Platinol', 'cis-DDP']
        >>> print(f"Found after trying: {strategies}")
        Found after trying: ['name:platinol']
        """
        attempted_strategies = []
        
        # Strategy 1: Try as-is
        id_type = self.detect_identifier_type(identifier)
        strategy = f"{id_type}:{identifier}"
        attempted_strategies.append(strategy)
        
        try:
            result = self.lookup(identifier, id_type)
            if result:
                return result, attempted_strategies
        except ChemicalLookupError:
            pass
        
        # Strategy 2: Clean identifier (remove spaces, special chars except hyphens)
        cleaned = re.sub(r'[^\w\-]', '', identifier)
        if cleaned != identifier:
            strategy = f"{id_type}:{cleaned}"
            attempted_strategies.append(strategy)
            
            try:
                result = self.lookup(cleaned, id_type)
                if result:
                    return result, attempted_strategies
            except ChemicalLookupError:
                pass
        
        # Strategy 3: If it looks numeric, try as CID
        if identifier.replace('-', '').isdigit() and id_type != 'cid':
            cid_candidate = identifier.replace('-', '')
            strategy = f"cid:{cid_candidate}"
            attempted_strategies.append(strategy)
            
            try:
                result = self.lookup(cid_candidate, 'cid')
                if result:
                    return result, attempted_strategies
            except ChemicalLookupError:
                pass
        
        return None, attempted_strategies
    
    def clear_cache(self):
        """
        Clear all cached lookup results.
        
        This removes both in-memory cache and cache file from disk.
        Useful for troubleshooting or freeing disk space.
        """
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
    
    def get_cache_info(self) -> Dict:
        """
        Get information about the current cache.
        
        Returns
        -------
        dict
            Dictionary with cache statistics:
            - 'size': Number of cached entries
            - 'file_path': Path to cache file
            - 'file_exists': Whether cache file exists on disk
            - 'file_size_kb': Size of cache file in KB (if exists)
        """
        info = {
            'size': len(self.cache),
            'file_path': str(self.cache_file),
            'file_exists': self.cache_file.exists(),
            'file_size_kb': 0
        }
        
        if self.cache_file.exists():
            info['file_size_kb'] = self.cache_file.stat().st_size / 1024
        
        return info


# Convenience function for simple usage
def lookup_molecular_weight(identifier: str) -> Optional[float]:
    """
    Simple function to quickly lookup molecular weight.
    
    This is a convenience wrapper around PubChemAPI for scripts that only
    need the molecular weight without other properties.
    
    Parameters
    ----------
    identifier : str
        Chemical identifier (name, CAS, CID)
        
    Returns
    -------
    float or None
        Molecular weight in g/mol, or None if not found
        
    Examples
    --------
    >>> mw = lookup_molecular_weight("Cisplatin")
    >>> print(f"MW: {mw} g/mol")
    MW: 300.1 g/mol
    """
    api = PubChemAPI()
    result = api.lookup(identifier)
    return result['molecular_weight'] if result else None


if __name__ == "__main__":
    # Example usage and testing
    print("PubChem API Module - Example Usage\n")
    
    # Create API instance
    api = PubChemAPI()
    
    # Test various identifier types
    test_compounds = [
        ("Cisplatin", "Common name"),
        ("50-18-0", "CAS number"),
        ("5702", "PubChem CID"),
        ("Platinol", "Brand name"),
        ("Doxorubicin", "Another oncology drug"),
    ]
    
    for identifier, description in test_compounds:
        print(f"\nLooking up: {identifier} ({description})")
        print("-" * 50)
        
        try:
            result, strategies = api.robust_lookup(identifier)
            
            if result:
                print(f"✓ Found: {result['molecular_formula']}")
                print(f"  Molecular Weight: {result['molecular_weight']} g/mol")
                print(f"  IUPAC Name: {result['iupac_name']}")
                print(f"  PubChem CID: {result['cid']}")
                print(f"  Common names: {', '.join(result['synonyms'][:3])}")
                print(f"  {'[CACHED]' if result['cached'] else '[FRESH]'}")
            else:
                print(f"✗ Not found. Tried: {strategies}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Show cache info
    print("\n" + "=" * 50)
    cache_info = api.get_cache_info()
    print(f"Cache contains {cache_info['size']} entries")
    print(f"Cache file: {cache_info['file_path']}")
    print(f"Cache size: {cache_info['file_size_kb']:.2f} KB")
