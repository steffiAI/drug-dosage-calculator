"""
GUI Integration Module for PubChem API Lookup.

This module provides tkinter widgets and handlers to integrate molecular weight
lookup functionality into the Drug Concentration Calculator.

Author: Stefanie Strasser
Email: s.strasser387@gmail.com
GitHub: https://github.com/steffiAI/drug-dosage-calculator
License: MIT
Version: 2.1.0
Last Updated: December 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional
import threading

from pubchem_api import PubChemAPI, ChemicalLookupError


class MolecularWeightLookupWidget:
    """
    Reusable widget for molecular weight lookup functionality.
    
    This widget provides a "Lookup" button and status indicator that can be
    easily integrated into any tkinter frame containing drug name and MW fields.
    
    The widget handles:
    - Drug name searches (e.g., "Cisplatin", "cisplatin")
    - CAS number searches (e.g., "15663-27-1")
    - Automatic Title Case normalization of compound names
    - Background threading for responsive UI
    - Result caching for offline access
    
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
    current_result : dict or None
        Most recent lookup result for displaying additional info
        
    Notes
    -----
    Developed by Stefanie Strasser for the Drug Concentration Calculator.
    Part of the open-source laboratory tools project.
    
    Examples
    --------
    >>> frame = tk.Frame(root)
    >>> name_var = tk.StringVar()
    >>> mw_var = tk.StringVar()
    >>> lookup_widget = MolecularWeightLookupWidget(
    ...     frame, name_var, mw_var, row=1, column_start=2
    ... )
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
            StringVar containing drug name or CAS number
        mw_var : tk.StringVar
            StringVar where MW should be filled
        row : int, default=0
            Grid row for widget placement
        column_start : int, default=3
            Starting grid column for widget placement
        """
        self.frame = parent_frame
        self.drug_name_var = drug_name_var
        self.mw_var = mw_var
        self.api = PubChemAPI()
        
        # Current lookup result (for displaying additional info)
        self.current_result = None
        
        # Store original search query (for error messages)
        self.original_query = None
        
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
            "Supports: Drug names and CAS numbers\n\n"
            "Examples:\n"
            "  • Cisplatin\n"
            "  • 15663-27-1 (Cisplatin CAS number)"
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
    
    def _get_display_name(self, result: dict) -> str:
        """
        Get the best display name from PubChem result.
        
        This extracts the preferred compound name from PubChem's synonym list
        and normalizes it to Title Case for consistent display.
        
        Parameters
        ----------
        result : dict
            PubChem lookup result containing synonyms
            
        Returns
        -------
        str
            Normalized compound name in Title Case (e.g., "Cisplatin")
            
        Notes
        -----
        If synonyms are not available, falls back to molecular formula.
        
        Examples
        --------
        >>> result = {'synonyms': ['CISPLATIN', 'cis-Platin'], 'molecular_formula': 'Cl2H6N2Pt'}
        >>> self._get_display_name(result)
        'Cisplatin'
        """
        # Try to get first synonym (usually the preferred name)
        if result.get('synonyms') and len(result['synonyms']) > 0:
            preferred_name = result['synonyms'][0]
            # Normalize to Title Case (e.g., "CISPLATIN" -> "Cisplatin")
            return preferred_name.title()
        
        # Fallback to molecular formula if no synonyms
        return result.get('molecular_formula', 'Unknown')
    
    def _on_lookup_clicked(self):
        """
        Handle lookup button click event.
        
        Starts a background lookup to prevent GUI freezing during the API call.
        The user input is sent to PubChem as-is (no pre-normalization).
        """
        user_input = self.drug_name_var.get().strip()
        
        if not user_input:
            messagebox.showwarning(
                "Input Required",
                "Please enter a drug name or CAS number first."
            )
            return
        
        # Store original query for error messages
        self.original_query = user_input
        
        # Disable button and show loading state
        self.lookup_button.config(
            text="⏳ Searching...",
            state=tk.DISABLED,
            bg="#808080"
        )
        self.status_label.config(text="Searching PubChem...", fg="blue")
        self.frame.update()
        
        # Run lookup in background thread (prevents GUI freezing)
        # The API call happens in the background while GUI stays responsive
        thread = threading.Thread(
            target=self._perform_lookup,
            args=(user_input,),
            daemon=True
        )
        thread.start()
    
    def _perform_lookup(self, identifier: str):
        """
        Perform the actual lookup in a background thread.
        
        This runs separately from the main GUI so the interface stays responsive.
        When done, it schedules the GUI update on the main thread using frame.after().
        
        Parameters
        ----------
        identifier : str
            Chemical identifier to look up (drug name or CAS number, as entered by user)
            
        Notes
        -----
        Uses frame.after(0, ...) to ensure GUI updates happen on the main thread.
        This prevents threading issues and potential crashes.
        """
        try:
            # Try robust lookup (multiple strategies)
            result, strategies = self.api.robust_lookup(identifier)
            
            # Schedule GUI update on main thread (thread-safe)
            self.frame.after(0, self._handle_lookup_result, result, identifier)
            
        except Exception as e:
            # Schedule error handling on main thread (thread-safe)
            self.frame.after(0, self._handle_lookup_error, str(e))
    
    def _handle_lookup_result(self, result: Optional[dict], identifier: str):
        """
        Handle successful or failed lookup result (runs in main GUI thread).
        
        Parameters
        ----------
        result : dict or None
            Lookup result dictionary or None if not found
        identifier : str
            Original identifier searched by user
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
            
            # Get normalized display name (e.g., "Cisplatin" from any input format)
            display_name = self._get_display_name(result)
            
            # Auto-fill molecular weight
            self.mw_var.set(f"{result['molecular_weight']:.2f}")
            
            # Show success status with compound name
            cache_indicator = "💾" if result.get('cached') else "🌐"
            status_text = (
                f"{cache_indicator} {display_name} - "
                f"{result['molecular_formula']} "
                f"(CID: {result['cid']})"
            )
            self.status_label.config(text=status_text, fg="green")
            
            # Show info dialog with compound details
            self._show_compound_info(result, display_name)
            
        else:
            # Compound not found
            self.status_label.config(text="❌ Not found", fg="red")
            
            response = messagebox.askyesno(
                "Compound Not Found",
                f"Could not find '{identifier}' in PubChem.\n\n"
                "Suggestions:\n"
                "• Check spelling (e.g., Cisplatin)\n"
                "• Try CAS number (e.g., 15663-27-1)\n"
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
        Handle lookup errors (runs in main GUI thread).
        
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
    
    def _show_compound_info(self, result: dict, display_name: str):
        """
        Display detailed compound information in a popup.
        
        Parameters
        ----------
        result : dict
            Compound information dictionary from PubChem containing:
            - molecular_formula: Chemical formula
            - molecular_weight: MW in g/mol
            - iupac_name: IUPAC nomenclature
            - cid: PubChem compound ID
            - synonyms: List of alternative names
            - connectivity_smiles: SMILES notation
            - cached: Whether data came from cache
            - lookup_date: When data was retrieved
        display_name : str
            Normalized compound name for display (Title Case)
        """
        info_window = tk.Toplevel(self.frame)
        info_window.title(f"Compound Information - {display_name}")
        info_window.geometry("550x500")
        info_window.resizable(False, False)
        
        # Main container frame
        main_frame = tk.Frame(info_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg="#2196F3", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=f"✓ {display_name}",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white"
        ).pack(pady=18)
        
        # Create scrollable text widget
        content_frame = tk.Frame(main_frame, padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(content_frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = tk.Scrollbar(content_frame, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Format compound information
        cache_status = 'Cached data' if result.get('cached') else 'Fresh from PubChem'
        pubchem_url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{result['cid']}"
        
        info_text = f"""Compound Name: {display_name}
Molecular Formula: {result['molecular_formula']}
Molecular Weight: {result['molecular_weight']:.2f} g/mol
IUPAC Name: {result['iupac_name']}
PubChem CID: {result['cid']}

Common Names / Synonyms:
{chr(10).join(f"  • {syn}" for syn in result['synonyms'][:10])}

Data Source: {cache_status}
Lookup Date: {result.get('lookup_date', 'Unknown')[:10]}

PubChem Link:
{pubchem_url}

Notes:
The molecular weight has been automatically filled in the calculator.
This information is cached locally for faster future lookups.
You can copy the PubChem link above to view full details in your browser.
"""
        
        text.insert(1.0, info_text)
        text.config(state=tk.DISABLED)  # Make read-only
        
        # Footer with developer credit
        footer_frame = tk.Frame(main_frame, bg="#f5f5f5", height=70)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        tk.Label(
            footer_frame,
            text="Drug Concentration Calculator v2.1.0",
            font=("Arial", 9),
            bg="#f5f5f5",
            fg="#555"
        ).pack(pady=(12, 2))
        
        tk.Label(
            footer_frame,
            text="Developed by Stefanie Strasser",
            font=("Arial", 8),
            bg="#f5f5f5",
            fg="gray"
        ).pack()
        
        # Close button
        btn_frame = tk.Frame(main_frame, pady=10)
        btn_frame.pack(side=tk.BOTTOM)
        
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            command=info_window.destroy,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=30,
            pady=5,
            cursor="hand2"
        )
        close_btn.pack()
        
        # Center the window
        info_window.update_idletasks()
        x = (info_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (info_window.winfo_screenheight() // 2) - (500 // 2)
        info_window.geometry(f"+{x}+{y}")


class AboutDialog:
    """
    Professional About dialog for the Drug Concentration Calculator.
    
    Displays application information including version, features, author
    contact information, and licensing details.
    
    This dialog provides users with:
    - Current version number and release date
    - Brief feature overview
    - Author contact information
    - GitHub repository link
    - License information
    
    Notes
    -----
    Part of the Drug Concentration Calculator by Stefanie Strasser.
    """
    
    def __init__(self, parent):
        """
        Create About dialog with application and author information.
        
        Parameters
        ----------
        parent : tk.Widget
            Parent widget (usually the main application window)
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About Drug Concentration Calculator")
        self.dialog.geometry("480x560")
        self.dialog.resizable(False, False)
        
        # Try to set icon
        try:
            import sys
            from pathlib import Path
            
            # Get icon path (works for both .py and .exe)
            if getattr(sys, 'frozen', False):
                # Running as .exe
                icon_path = Path(sys._MEIPASS) / "icon.ico"
            else:
                # Running as .py
                icon_path = Path(__file__).parent.parent / "icon.ico"
            
            if icon_path.exists():
                self.dialog.iconbitmap(str(icon_path))
        except Exception:
            pass  # Icon is optional
        
        # App header
        header_frame = tk.Frame(self.dialog, bg="#2196F3", height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="💊 Drug Concentration Calculator",
            font=("Arial", 15, "bold"),
            bg="#2196F3",
            fg="white"
        ).pack(pady=30)
        
        # Main info frame
        info_frame = tk.Frame(self.dialog, padx=30, pady=20)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Version info
        tk.Label(
            info_frame,
            text="Version 2.1.1",
            font=("Arial", 12, "bold"),
            fg="#2196F3"
        ).pack(pady=(0, 5))
        
        tk.Label(
            info_frame,
            text="December 2025",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=(0, 15))
        
        # Description
        description = (
            "A professional tool for calculating stock and working\n"
            "solution concentrations.\n\n"
            "Features automated molecular weight lookup via\n"
            "PubChem database integration and calculation history."
        )
        tk.Label(
            info_frame,
            text=description,
            font=("Arial", 10),
            justify=tk.CENTER,
            fg="#555"
        ).pack(pady=10)
        
        # Separator
        ttk.Separator(info_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Author info
        tk.Label(
            info_frame,
            text="Developed by",
            font=("Arial", 9),
            fg="gray"
        ).pack()
        
        tk.Label(
            info_frame,
            text="Stefanie Strasser",
            font=("Arial", 12, "bold"),
            fg="#2196F3"
        ).pack(pady=(5, 3))
        
        tk.Label(
            info_frame,
            text="s.strasser387@gmail.com",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=(0, 15))
        
        # GitHub link (as text, since no webbrowser module)
        tk.Label(
            info_frame,
            text="GitHub Repository:",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=(10, 3))
        
        tk.Label(
            info_frame,
            text="github.com/steffiAI/drug-dosage-calculator",
            font=("Arial", 9, "bold"),
            fg="#2196F3"
        ).pack()
        
        # Separator
        ttk.Separator(info_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # License
        tk.Label(
            info_frame,
            text="Licensed under MIT License",
            font=("Arial", 8),
            fg="gray"
        ).pack(pady=(5, 0))
        
        tk.Label(
            info_frame,
            text="Open-source software for the research community",
            font=("Arial", 8),
            fg="gray"
        ).pack()
        
        # Close button
        tk.Button(
            info_frame,
            text="Close",
            command=self.dialog.destroy,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=30,
            pady=8,
            cursor="hand2"
        ).pack(pady=20)
        
        # Center window
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (480 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (560 // 2)
        self.dialog.geometry(f"+{x}+{y}")


# Utility function for easy integration
def add_lookup_to_gui(frame: tk.Frame, 
                      drug_name_var: tk.StringVar,
                      mw_var: tk.StringVar,
                      row: int = 0,
                      column_start: int = 3) -> MolecularWeightLookupWidget:
    """
    Add MW lookup functionality to an existing GUI frame.
    
    This is a convenience function for integrating the lookup widget
    into your existing drug calculator GUI.
    
    Parameters
    ----------
    frame : tk.Frame
        Frame containing drug name and MW fields
    drug_name_var : tk.StringVar
        StringVar for drug name input
    mw_var : tk.StringVar
        StringVar for molecular weight output
    row : int, default=0
        Grid row where the lookup widget should be placed
    column_start : int, default=3
        Starting grid column for the lookup widget
        
    Returns
    -------
    MolecularWeightLookupWidget
        The created widget instance
        
    Examples
    --------
    >>> # In your main GUI code:
    >>> lookup_widget = add_lookup_to_gui(
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
        column_start=column_start
    )
    return widget


if __name__ == "__main__":
    # Demo application
    print("=" * 60)
    print("Drug Concentration Calculator - MW Lookup Demo")
    print("Developed by Stefanie Strasser")
    print("=" * 60)
    print()
    
    root = tk.Tk()
    root.title("Drug Calculator - MW Lookup Demo")
    root.geometry("800x400")
    
    # Main frame
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title with author
    title = tk.Label(
        main_frame,
        text="Drug Concentration Calculator",
        font=("Arial", 16, "bold"),
        fg="#2196F3"
    )
    title.grid(row=0, column=0, columnspan=5, pady=(0, 5))
    
    subtitle = tk.Label(
        main_frame,
        text="with PubChem Integration • Developed by Stefanie Strasser",
        font=("Arial", 10),
        fg="gray"
    )
    subtitle.grid(row=1, column=0, columnspan=5, pady=(0, 20))
    
    # Drug name field
    tk.Label(
        main_frame, 
        text="Drug Name / CAS:", 
        font=("Arial", 10)
    ).grid(row=2, column=0, sticky="w", pady=5)
    
    drug_name_var = tk.StringVar(value="Cisplatin")
    drug_entry = tk.Entry(
        main_frame, 
        textvariable=drug_name_var, 
        width=30, 
        font=("Arial", 10)
    )
    drug_entry.grid(row=2, column=1, padx=5, pady=5)
    
    # MW field
    tk.Label(
        main_frame, 
        text="Molecular Weight (g/mol):", 
        font=("Arial", 10)
    ).grid(row=3, column=0, sticky="w", pady=5)
    
    mw_var = tk.StringVar()
    mw_entry = tk.Entry(
        main_frame, 
        textvariable=mw_var, 
        width=30, 
        font=("Arial", 10)
    )
    mw_entry.grid(row=3, column=1, padx=5, pady=5)
    
    # Add lookup widget
    lookup_widget = MolecularWeightLookupWidget(
        main_frame,
        drug_name_var,
        mw_var,
        row=3,
        column_start=2
    )
    
    # Button frame
    btn_frame = tk.Frame(main_frame)
    btn_frame.grid(row=4, column=0, columnspan=5, pady=20)
    
    # About button
    about_btn = tk.Button(
        btn_frame,
        text="ℹ️ About",
        command=lambda: AboutDialog(root),
        font=("Arial", 10),
        padx=15,
        pady=5,
        cursor="hand2"
    )
    about_btn.pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = tk.Label(
        main_frame,
        text=(
            "Try searching:\n"
            "• Cisplatin  (drug name)\n"
            "• 15663-27-1  (Cisplatin CAS number)\n"
            "• Etoposide, Doxorubicin, Paclitaxel"
        ),
        font=("Arial", 9),
        fg="gray",
        justify=tk.LEFT
    )
    instructions.grid(row=5, column=0, columnspan=5, pady=10)
    
    # Developer credit footer
    footer = tk.Label(
        main_frame,
        text="Drug Concentration Calculator v2.1.0 • © 2025 Stefanie Strasser • MIT License",
        font=("Arial", 8),
        fg="#999"
    )
    footer.grid(row=6, column=0, columnspan=5, pady=(20, 0))
    
    root.mainloop()
