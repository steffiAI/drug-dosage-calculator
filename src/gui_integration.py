"""
GUI Integration Module for PubChem API Lookup.

This module provides tkinter widgets and handlers to integrate molecular weight
lookup functionality into the existing drug calculator GUI.

Author: Steffi
Created: 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Callable
import threading

from pubchem_api import PubChemAPI, ChemicalLookupError


class MolecularWeightLookupWidget:
    """
    Reusable widget for molecular weight lookup functionality.
    
    This widget provides a "Lookup" button and status indicator that can be
    easily integrated into any tkinter frame containing drug name and MW fields.
    
    Attributes
    ----------
    frame : tk.Frame
        Parent frame containing this widget
    api : PubChemAPI
        PubChem API interface instance
    lookup_button : tk.Button
        Button to trigger MW lookup
    status_label : tk.Label
        Label showing lookup status/results
    """
    
    def __init__(self, parent_frame: tk.Frame, 
                 drug_name_var: tk.StringVar,
                 mw_var: tk.StringVar,
                 row: int = 0,
                 column_start: int = 3):
        """
        Initialize the MW lookup widget.
        
        Parameters
        ----------
        parent_frame : tk.Frame
            Parent frame to place widget in
        drug_name_var : tk.StringVar
            StringVar containing drug name
        mw_var : tk.StringVar
            StringVar where MW should be filled
        row : int, default=0
            Grid row for widget placement
        column_start : int, default=3
            Starting grid column for widget placement
            
        Examples
        --------
        >>> frame = tk.Frame(root)
        >>> name_var = tk.StringVar()
        >>> mw_var = tk.StringVar()
        >>> lookup_widget = MolecularWeightLookupWidget(
        ...     frame, name_var, mw_var, row=1, column_start=2
        ... )
        """
        self.frame = parent_frame
        self.drug_name_var = drug_name_var
        self.mw_var = mw_var
        self.api = PubChemAPI()
        
        # Current lookup result (for displaying additional info)
        self.current_result = None
        
        # Create lookup button
        self.lookup_button = tk.Button(
            parent_frame,
            text="🔍 Lookup MW",
            command=self._on_lookup_clicked,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            padx=10,
            pady=5
        )
        self.lookup_button.grid(row=row, column=column_start, padx=5, pady=2, sticky="w")
        
        # Add tooltip
        self._create_tooltip(
            self.lookup_button,
            "Look up molecular weight from PubChem database\n"
            "Supports: drug names, CAS numbers, PubChem CIDs"
        )
        
        # Status label (initially hidden)
        self.status_label = tk.Label(
            parent_frame,
            text="",
            font=("Arial", 8),
            fg="gray"
        )
        self.status_label.grid(row=row, column=column_start+1, columnspan=2, 
                              padx=5, sticky="w")
    
    def _create_tooltip(self, widget, text: str):
        """
        Create a tooltip for a widget.
        
        Parameters
        ----------
        widget : tk.Widget
            Widget to attach tooltip to
        text : str
            Tooltip text to display
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Arial", 8),
                padx=5,
                pady=3
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _on_lookup_clicked(self):
        """Handle lookup button click event."""
        drug_name = self.drug_name_var.get().strip()
        
        if not drug_name:
            messagebox.showwarning(
                "Input Required",
                "Please enter a drug name, CAS number, or PubChem CID first."
            )
            return
        
        # Disable button and show loading state
        self.lookup_button.config(
            text="⏳ Searching...",
            state=tk.DISABLED,
            bg="#808080"
        )
        self.status_label.config(text="Searching PubChem...", fg="blue")
        self.frame.update()
        
        # Run lookup in separate thread to avoid freezing GUI
        thread = threading.Thread(
            target=self._perform_lookup,
            args=(drug_name,),
            daemon=True
        )
        thread.start()
    
    def _perform_lookup(self, identifier: str):
        """
        Perform the actual lookup (runs in background thread).
        
        Parameters
        ----------
        identifier : str
            Chemical identifier to look up
        """
        try:
            # Try robust lookup (multiple strategies)
            result, strategies = self.api.robust_lookup(identifier)
            
            # Update GUI in main thread
            self.frame.after(0, self._handle_lookup_result, result, identifier)
            
        except Exception as e:
            # Handle errors in main thread
            self.frame.after(0, self._handle_lookup_error, str(e))
    
    def _handle_lookup_result(self, result: Optional[dict], identifier: str):
        """
        Handle successful or failed lookup result.
        
        Parameters
        ----------
        result : dict or None
            Lookup result dictionary or None if not found
        identifier : str
            Original identifier searched
        """
        # Re-enable button
        self.lookup_button.config(
            text="🔍 Lookup MW",
            state=tk.NORMAL,
            bg="#4CAF50"
        )
        
        if result:
            # Store result for displaying additional info
            self.current_result = result
            
            # Auto-fill molecular weight using StringVar
            self.mw_var.set(f"{result['molecular_weight']:.2f}")
            
            # Show success status
            cache_indicator = "💾" if result.get('cached') else "🌐"
            status_text = (
                f"{cache_indicator} {result['molecular_formula']} "
                f"(CID: {result['cid']})"
            )
            self.status_label.config(text=status_text, fg="green")
            
            # Show info dialog with compound details
            self._show_compound_info(result)
            
        else:
            # Compound not found
            self.status_label.config(text="❌ Not found", fg="red")
            
            response = messagebox.askyesno(
                "Compound Not Found",
                f"Could not find '{identifier}' in PubChem.\n\n"
                "Suggestions:\n"
                "• Check spelling\n"
                "• Try CAS number (e.g., 50-18-0)\n"
                "• Try PubChem CID\n"
                "• Use alternative drug name\n\n"
                "Would you like to enter the molecular weight manually?"
            )
            
            if response:
                # Prompt for manual entry
                mw = simpledialog.askfloat(
                    "Manual Entry",
                    f"Enter molecular weight for '{identifier}' (g/mol):",
                    minvalue=0,
                    maxvalue=100000
                )
                if mw:
                    self.mw_var.set(f"{mw:.2f}")
                    self.status_label.config(
                        text="✏️ Manually entered",
                        fg="orange"
                    )
    
    def _handle_lookup_error(self, error_msg: str):
        """
        Handle lookup errors.
        
        Parameters
        ----------
        error_msg : str
            Error message to display
        """
        # Re-enable button
        self.lookup_button.config(
            text="🔍 Lookup MW",
            state=tk.NORMAL,
            bg="#4CAF50"
        )
        
        self.status_label.config(text="⚠️ Error", fg="red")
        
        messagebox.showerror(
            "Lookup Error",
            f"An error occurred during lookup:\n\n{error_msg}\n\n"
            "Please check your internet connection and try again."
        )
    
    def _show_compound_info(self, result: dict):
        """
        Display detailed compound information in a popup.
        
        Parameters
        ----------
        result : dict
            Compound information dictionary
        """
        info_window = tk.Toplevel(self.frame)
        info_window.title(f"Compound Information - {result['molecular_formula']}")
        info_window.geometry("500x400")
        info_window.resizable(False, False)
        
        # Create scrollable text widget
        frame = tk.Frame(info_window, padx=15, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Format compound information
        info_text = f"""✓ Compound Found in PubChem

Molecular Formula: {result['molecular_formula']}
Molecular Weight: {result['molecular_weight']:.2f} g/mol
IUPAC Name: {result['iupac_name']}
PubChem CID: {result['cid']}

Common Names / Synonyms:
{chr(10).join(f"  • {syn}" for syn in result['synonyms'][:10])}

SMILES: {result['connectivity_smiles']}

Source: {'Cached data' if result.get('cached') else 'Fresh from PubChem'}
Lookup Date: {result.get('lookup_date', 'Unknown')[:10]}

PubChem Link:
https://pubchem.ncbi.nlm.nih.gov/compound/{result['cid']}

Notes:
The molecular weight has been automatically filled in the calculator.
This information is cached for faster future lookups.
"""
        
        text.insert(1.0, info_text)
        text.config(state=tk.DISABLED)  # Make read-only
        
        # Add close button
        close_btn = tk.Button(
            info_window,
            text="Close",
            command=info_window.destroy,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)
        
        # Center the window
        info_window.update_idletasks()
        x = (info_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (info_window.winfo_screenheight() // 2) - (400 // 2)
        info_window.geometry(f"+{x}+{y}")


class CacheManagerDialog:
    """
    Dialog for managing PubChem lookup cache.
    
    Allows users to view cache statistics and clear cached data.
    """
    
    def __init__(self, parent):
        """
        Create cache manager dialog.
        
        Parameters
        ----------
        parent : tk.Widget
            Parent widget
        """
        self.api = PubChemAPI()
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("PubChem Cache Manager")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Create UI
        self._create_ui()
        
        # Center window
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_ui(self):
        """Create the UI elements."""
        # Title
        title_label = tk.Label(
            self.dialog,
            text="PubChem Lookup Cache",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=15)
        
        # Cache info frame
        info_frame = tk.LabelFrame(
            self.dialog,
            text="Cache Statistics",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=15
        )
        info_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        cache_info = self.api.get_cache_info()
        
        # Display stats
        stats = [
            ("Cached Compounds:", f"{cache_info['size']} entries"),
            ("Cache File:", cache_info['file_path']),
            ("File Size:", f"{cache_info['file_size_kb']:.2f} KB"),
            ("Status:", "Active" if cache_info['file_exists'] else "No cache file")
        ]
        
        for i, (label, value) in enumerate(stats):
            tk.Label(
                info_frame,
                text=label,
                font=("Arial", 9, "bold"),
                anchor="w"
            ).grid(row=i, column=0, sticky="w", pady=5)
            
            tk.Label(
                info_frame,
                text=value,
                font=("Arial", 9),
                anchor="w",
                wraplength=300
            ).grid(row=i, column=1, sticky="w", padx=10, pady=5)
        
        # Benefits info
        benefits_text = (
            "Cache benefits:\n"
            "• Faster repeated lookups\n"
            "• Works offline for cached compounds\n"
            "• Reduces API requests"
        )
        tk.Label(
            self.dialog,
            text=benefits_text,
            font=("Arial", 9),
            justify=tk.LEFT,
            fg="gray"
        ).pack(pady=10)
        
        # Button frame
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=15)
        
        # Clear cache button
        clear_btn = tk.Button(
            btn_frame,
            text="Clear Cache",
            command=self._clear_cache,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            command=self.dialog.destroy,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def _clear_cache(self):
        """Clear the cache after confirmation."""
        response = messagebox.askyesno(
            "Confirm Clear Cache",
            "Are you sure you want to clear all cached compound data?\n\n"
            "This will require re-downloading from PubChem on next lookup."
        )
        
        if response:
            self.api.clear_cache()
            messagebox.showinfo(
                "Cache Cleared",
                "Cache has been cleared successfully."
            )
            self.dialog.destroy()


# Example integration function
def add_lookup_to_existing_gui(frame: tk.Frame, 
                                drug_name_var: tk.StringVar,
                                mw_var: tk.StringVar,
                                row: int = 0) -> MolecularWeightLookupWidget:
    """
    Add MW lookup functionality to an existing GUI frame.
    
    This function demonstrates how to integrate the lookup widget into
    your existing drug calculator GUI.
    
    Parameters
    ----------
    frame : tk.Frame
        Frame containing drug name and MW fields
    drug_name_var : tk.StringVar
        StringVar for drug name
    mw_var : tk.StringVar
        StringVar for molecular weight
    row : int, default=0
        Grid row where MW entry is located
        
    Returns
    -------
    MolecularWeightLookupWidget
        The created widget instance
        
    Examples
    --------
    >>> # In your existing GUI code:
    >>> lookup_widget = add_lookup_to_existing_gui(
    ...     main_frame,
    ...     self.drug_name_var,
    ...     self.mw_var,
    ...     row=2
    ... )
    """
    widget = MolecularWeightLookupWidget(
        frame,
        drug_name_var,
        mw_var,
        row=row,
        column_start=3  # Adjust based on your layout
    )
    return widget


if __name__ == "__main__":
    # Demo application
    print("Starting MW Lookup Widget Demo...")
    
    root = tk.Tk()
    root.title("Drug Calculator - MW Lookup Demo")
    root.geometry("700x300")
    
    # Main frame
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title = tk.Label(
        main_frame,
        text="Drug Calculator with PubChem Integration",
        font=("Arial", 16, "bold")
    )
    title.grid(row=0, column=0, columnspan=4, pady=15)
    
    # Drug name field
    tk.Label(main_frame, text="Drug Name/CAS/CID:", font=("Arial", 10)).grid(
        row=1, column=0, sticky="w", pady=5
    )
    drug_name_var = tk.StringVar(value="Cisplatin")
    tk.Entry(main_frame, textvariable=drug_name_var, width=30, font=("Arial", 10)).grid(
        row=1, column=1, padx=5, pady=5
    )
    
    # MW field
    tk.Label(main_frame, text="Molecular Weight (g/mol):", font=("Arial", 10)).grid(
        row=2, column=0, sticky="w", pady=5
    )
    mw_var = tk.StringVar()
    tk.Entry(main_frame, textvariable=mw_var, width=30, font=("Arial", 10)).grid(
        row=2, column=1, padx=5, pady=5
    )
    
    # Add lookup widget
    lookup_widget = MolecularWeightLookupWidget(
        main_frame,
        drug_name_var,
        mw_var,
        row=2,
        column_start=2
    )
    
    # Add cache manager button
    cache_btn = tk.Button(
        main_frame,
        text="⚙️ Manage Cache",
        command=lambda: CacheManagerDialog(root),
        font=("Arial", 9)
    )
    cache_btn.grid(row=3, column=0, columnspan=2, pady=20)
    
    # Instructions
    instructions = tk.Label(
        main_frame,
        text="Try searching: Cisplatin, 50-18-0, Doxorubicin, 5702",
        font=("Arial", 9),
        fg="gray"
    )
    instructions.grid(row=4, column=0, columnspan=4, pady=10)
    
    root.mainloop()
