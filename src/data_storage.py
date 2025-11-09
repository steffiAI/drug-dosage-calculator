"""
Drug Dosage Calculator - Data storage functionality.

This module handles saving and loading calculation history to/from JSON files.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class CalculationHistory:
    """
    Manage calculation history storage and retrieval.
    
    Calculations are stored as JSON in the data/ directory.
    Each entry includes timestamp, calculation type, inputs, and results.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the calculation history manager.
        
        Parameters
        ----------
        data_dir : str, default="data"
            Directory to store the history JSON file
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "calculation_history.json"
        
        # Create file if it doesn't exist
        if not self.history_file.exists():
            self._save_history([])
    
    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """
        Save history list to JSON file.
        
        Parameters
        ----------
        history : list of dict
            List of calculation entries to save
        """
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save history: {e}")
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Load history from JSON file.
        
        Returns
        -------
        list of dict
            List of all saved calculations
        """
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If file is corrupted, start fresh
            return []
        except Exception as e:
            raise IOError(f"Failed to load history: {e}")
    
    def add_calculation(self, 
                       calculation_type: str,
                       drug_name: str,
                       inputs: Dict[str, Any],
                       results: Dict[str, Any],
                       solvent: str = "") -> None:
        """
        Add a new calculation to history.
        
        Parameters
        ----------
        calculation_type : str
            Type of calculation ("Stock from Powder" or "Working from Stock")
        drug_name : str
            Name of the drug/compound
        inputs : dict
            Input parameters used for calculation
        results : dict
            Calculated results
        solvent : str, optional
            Solvent used for the solution
        """
        history = self._load_history()
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'calculation_type': calculation_type,
            'drug_name': drug_name,
            'solvent': solvent,
            'inputs': inputs,
            'results': results
        }
        
        history.append(entry)
        self._save_history(history)
    
    def get_all_calculations(self) -> List[Dict[str, Any]]:
        """
        Retrieve all saved calculations.
        
        Returns
        -------
        list of dict
            All calculation entries, ordered by timestamp (newest first)
        """
        history = self._load_history()
        # Return in reverse order (newest first)
        return history[::-1]
    
    def clear_history(self) -> None:
        """
        Clear all calculation history.
        
        This creates a backup before clearing.
        """
        history = self._load_history()
        if history:
            # Create backup
            backup_file = self.data_dir / f"history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w') as f:
                json.dump(history, f, indent=2)
        
        # Clear current history
        self._save_history([])
    
    def get_calculation_count(self) -> int:
        """
        Get total number of saved calculations.
        
        Returns
        -------
        int
            Number of calculations in history
        """
        return len(self._load_history())
