"""
Drug Dosage Calculator - Main GUI Application.

A laboratory tool for calculating drug solution preparations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from calculators import calculate_stock_from_powder, calculate_dilution, validate_inputs
from data_storage import CalculationHistory
from formatters import format_number, validate_decimal_input, format_result_with_unit, convert_to_readable_unit
from gui_integration import MolecularWeightLookupWidget, CacheManagerDialog


class ToolTip:
    """
    Creates a tooltip (hover text) for a tkinter widget.
    
    How it works:
    - When mouse enters widget → show tooltip
    - When mouse leaves widget → hide tooltip
    - Creates temporary window for the tooltip text
    
    Parameters
    ----------
    widget : tkinter widget
        The widget to attach the tooltip to (e.g., a Label or Button)
    text : str
        The text to display in the tooltip
    
    Example
    -------
    info_icon = ttk.Label(frame, text="ℹ️")
    ToolTip(info_icon, "Use period (.) for decimal numbers")
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # Bind hover events
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Display the tooltip when mouse enters widget."""
        if self.tooltip_window:
            return
        
        # Position tooltip near the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Tooltip content with light yellow background
        label = ttk.Label(
            self.tooltip_window,
            text=self.text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            padding=5
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip when mouse leaves widget."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class DrugCalculatorApp:
    """
    Main application window for drug dosage calculator.
    
    Provides interfaces for:
    - Stock solution preparation (powder → stock)
    - Working solution dilution (stock → working)
    - Calculation history viewing
    """
    
    def __init__(self, root):
        """
        Initialize the main application window.
        
        Parameters
        ----------
        root : tk.Tk
            Root tkinter window
        """
        self.root = root
        self.root.title("Drug Dosage Calculator - Lab Edition")
        self.root.geometry("700x600")
        
        # Initialize data storage
        self.history = CalculationHistory()
        
        # Current calculator mode
        self.current_mode = None
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Show welcome screen
        self.show_welcome_screen()
    
    def clear_frame(self):
        """Clear all widgets from main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    def create_labeled_input(self, parent, row, label_text, tooltip_text=None, 
                            has_unit=False, unit_options=None, default_unit=None):
        """
        Create a labeled input field with optional tooltip and unit selector.
        
        Parameters
        ----------
        parent : tk.Frame
            Parent frame to place widgets in
        row : int
            Grid row number
        label_text : str
            Text for the label
        tooltip_text : str, optional
            Tooltip text for info icon (if None, no icon is shown)
        has_unit : bool, default=False
            Whether to include a unit dropdown
        unit_options : list, optional
            List of unit options for dropdown
        default_unit : str, optional
            Default selected unit
            
        Returns
        -------
        dict
            Dictionary containing 'value_var', 'unit_var' (if applicable)
        """
        # Create frame to hold label + optional info icon together
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=0, sticky=tk.W, pady=5)
        
        # Add label text
        ttk.Label(label_frame, text=label_text).pack(side=tk.LEFT)
        
        # Add info icon with tooltip if tooltip text is provided
        if tooltip_text:
            info_icon = ttk.Label(label_frame, text=" ℹ️", foreground="blue", cursor="hand2")
            info_icon.pack(side=tk.LEFT)
            ToolTip(info_icon, tooltip_text)
        
        # Create entry field for value input
        value_var = tk.StringVar()
        ttk.Entry(parent, textvariable=value_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=5
        )
        
        # Create unit dropdown if requested
        unit_var = None
        if has_unit:
            unit_var = tk.StringVar(value=default_unit or "")
            unit_combo = ttk.Combobox(
                parent,
                textvariable=unit_var,
                values=unit_options or [],
                state="readonly",
                width=8
            )
            unit_combo.grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Return variables in a dictionary for easy access
        result = {'value_var': value_var}
        if unit_var:
            result['unit_var'] = unit_var
        
        return result   

    
    def show_welcome_screen(self):
        """Display welcome screen with calculator selection buttons."""
        self.clear_frame()
        self.current_mode = None
        
        # Title
        title = ttk.Label(
            self.main_frame,
            text="Drug Concentration Calculator",
            font=('Arial', 18, 'bold')
        )
        title.grid(row=0, column=0, pady=20)
        
        subtitle = ttk.Label(
            self.main_frame,
            text="Solution Preparation Tool",
            font=('Arial', 12)
        )
        subtitle.grid(row=1, column=0, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, pady=30)
        
        # Calculator buttons
        stock_btn = ttk.Button(
            button_frame,
            text="Stock Solution Calculator\n(Powder → Stock)",
            command=self.show_stock_calculator,
            width=30
        )
        stock_btn.grid(row=0, column=0, pady=10)
        
        dilution_btn = ttk.Button(
            button_frame,
            text="Working Solution Calculator\n(Stock → Working)",
            command=self.show_dilution_calculator,
            width=30
        )
        dilution_btn.grid(row=1, column=0, pady=10)
        
        history_btn = ttk.Button(
            button_frame,
            text="View Calculation History",
            command=self.show_history,
            width=30
        )
        history_btn.grid(row=2, column=0, pady=10)
        
        # Footer
        count = self.history.get_calculation_count()
        footer = ttk.Label(
            self.main_frame,
            text=f"Total calculations saved: {count}",
            font=('Arial', 9)
        )
        footer.grid(row=3, column=0, pady=20)
    
    def show_stock_calculator(self):
        """Display stock solution calculator interface with input validation tooltips."""
        self.clear_frame()
        self.current_mode = "stock"
        
        # Title
        title = ttk.Label(
            self.main_frame,
            text="Stock Solution Calculator",
            font=('Arial', 16, 'bold')
        )
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        subtitle = ttk.Label(
            self.main_frame,
            text="Calculate mass of powder needed for stock solution",
            font=('Arial', 10)
        )
        subtitle.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Input frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Input Parameters", padding="10")
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # ========== ROW 0: Drug name (no tooltip needed) ==========
        ttk.Label(input_frame, text="Drug Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.drug_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.drug_name_var, width=30).grid(
            row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        
        # ========== ROW 1: Molecular weight (WITH tooltip) ==========
        # Create frame to hold label + info icon together
        mw_label_frame = ttk.Frame(input_frame)
        mw_label_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(mw_label_frame, text="Molecular Weight (g/mol):").pack(side=tk.LEFT)
        
        # Info icon with tooltip
        mw_info = ttk.Label(mw_label_frame, text=" ℹ️", foreground="blue", cursor="hand2")
        mw_info.pack(side=tk.LEFT)
        ToolTip(mw_info, "Use period (.) for decimal numbers")
        
        # Entry field
        self.mw_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.mw_var, width=15).grid(
            row=1, column=1, sticky=tk.W, pady=5
        )

        # Molecular weigth lookup
        self.mw_lookup = MolecularWeightLookupWidget(
            input_frame,
            self.drug_name_var,  # Drug name entry (already exists)
            self.mw_var,         # MW entry (already exists)
            row=1,
            column_start=2
        )
        
        # ========== ROW 2: Target concentration (WITH tooltip) ==========
        conc_label_frame = ttk.Frame(input_frame)
        conc_label_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(conc_label_frame, text="Target Concentration:").pack(side=tk.LEFT)
        
        conc_info = ttk.Label(conc_label_frame, text=" ℹ️", foreground="blue", cursor="hand2")
        conc_info.pack(side=tk.LEFT)
        ToolTip(conc_info, "Use period (.) for decimal numbers")
        
        # Entry field
        self.conc_var = tk.StringVar()
        conc_entry = ttk.Entry(input_frame, textvariable=self.conc_var, width=15)
        conc_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Concentration unit dropdown
        self.conc_unit_var = tk.StringVar(value="mM")
        conc_units = ttk.Combobox(
            input_frame,
            textvariable=self.conc_unit_var,
            values=["M", "mM", "µM", "nM"],
            state="readonly",
            width=8
        )
        conc_units.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # ========== ROW 3: Target volume (WITH tooltip) ==========
        vol_label_frame = ttk.Frame(input_frame)
        vol_label_frame.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(vol_label_frame, text="Target Volume:").pack(side=tk.LEFT)
        
        vol_info = ttk.Label(vol_label_frame, text=" ℹ️", foreground="blue", cursor="hand2")
        vol_info.pack(side=tk.LEFT)
        ToolTip(vol_info, "Use period (.) for decimal numbers")
        
        # Entry field
        self.vol_var = tk.StringVar()
        vol_entry = ttk.Entry(input_frame, textvariable=self.vol_var, width=15)
        vol_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Volume unit dropdown (default to µL as per your requirement)
        self.vol_unit_var = tk.StringVar(value="µL")  # Changed default from "mL" to "µL"
        vol_units = ttk.Combobox(
            input_frame,
            textvariable=self.vol_unit_var,
            values=["L", "mL", "µL"],
            state="readonly",
            width=8
        )
        vol_units.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # ========== ROW 4: Solvent (no tooltip needed) ==========
        ttk.Label(input_frame, text="Solvent:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.solvent_var = tk.StringVar()
        solvent_combo = ttk.Combobox(
            input_frame,
            textvariable=self.solvent_var,
            values=["DMSO", "Water", "Ethanol", "PBS", "Media", "Other"],
            width=27
        )
        solvent_combo.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Button frame
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Calculate", command=self.calculate_stock).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self.clear_inputs).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(btn_frame, text="Back to Menu", command=self.show_welcome_screen).grid(
            row=0, column=2, padx=5
        )
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        self.results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            height=10,
            width=60,
            font=('Courier', 10)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.main_frame.rowconfigure(4, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
    
    def show_dilution_calculator(self):
        """Display working solution dilution calculator interface."""
        self.clear_frame()
        self.current_mode = "dilution"
        
        # Title
        title = ttk.Label(
            self.main_frame,
            text="Working Solution Calculator",
            font=('Arial', 16, 'bold')
        )
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        subtitle = ttk.Label(
            self.main_frame,
            text="Dilute stock solution to working concentration",
            font=('Arial', 10)
        )
        subtitle.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Input frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Input Parameters", padding="10")
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
       # ========== ROW 0: Drug name (no tooltip) ==========
        ttk.Label(input_frame, text="Drug Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.drug_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.drug_name_var, width=30).grid(
            row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        
        # ========== ROW 1: Stock Concentration (with tooltip + unit) ==========
        stock_conc_fields = self.create_labeled_input(
            parent=input_frame,
            row=1,
            label_text="Stock Concentration:",
            tooltip_text="Use period (.) for decimal numbers",
            has_unit=True,
            unit_options=["M", "mM", "µM", "nM"],
            default_unit="mM"
        )
        self.stock_conc_var = stock_conc_fields['value_var']
        self.stock_conc_unit_var = stock_conc_fields['unit_var']
        
        # ========== ROW 2: Target Concentration (with tooltip + unit) ==========
        target_conc_fields = self.create_labeled_input(
            parent=input_frame,
            row=2,
            label_text="Target Concentration:",
            tooltip_text="Use period (.) for decimal numbers",
            has_unit=True,
            unit_options=["M", "mM", "µM", "nM"],
            default_unit="µM"
        )
        self.target_conc_var = target_conc_fields['value_var']
        self.target_conc_unit_var = target_conc_fields['unit_var']
        
        # ========== ROW 3: Target Volume (with tooltip + unit) ==========
        target_vol_fields = self.create_labeled_input(
            parent=input_frame,
            row=3,
            label_text="Target Volume:",
            tooltip_text="Use period (.) for decimal numbers",
            has_unit=True,
            unit_options=["L", "mL", "µL"],
            default_unit="µL"
        )
        self.target_vol_var = target_vol_fields['value_var']
        self.vol_unit_var = target_vol_fields['unit_var']
        
        # ========== ROW 4: Solvent (no tooltip) ==========
        ttk.Label(input_frame, text="Solvent:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.solvent_var = tk.StringVar()
        solvent_combo = ttk.Combobox(
            input_frame,
            textvariable=self.solvent_var,
            values=["Media", "PBS", "Water", "DMSO", "Ethanol", "Other"],
            width=27
        )
        solvent_combo.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
   
        
        # Button frame
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Calculate", command=self.calculate_dilution).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self.clear_inputs).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(btn_frame, text="Back to Menu", command=self.show_welcome_screen).grid(
            row=0, column=2, padx=5
        )
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        self.results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            height=10,
            width=60,
            font=('Courier', 10)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.main_frame.rowconfigure(4, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
    
    def calculate_stock(self):
        """Perform stock solution calculation with input validation and formatted results."""
        try:
            # ========== STEP 1: Get raw input values ==========
            drug_name = self.drug_name_var.get().strip()
            mw_input = self.mw_var.get().strip()
            conc_input = self.conc_var.get().strip()
            vol_input = self.vol_var.get().strip()
            
            # ========== STEP 2: Validate drug name ==========
            if not drug_name:
                messagebox.showerror("Input Error", "Please enter a drug name")
                return
            
            # ========== STEP 3: Validate molecular weight ==========
            is_valid, _, error_msg = validate_decimal_input(mw_input)
            if not is_valid:
                messagebox.showerror("Input Error", f"Molecular Weight: {error_msg}")
                return
            mw = float(mw_input)
            
            if mw <= 0:
                messagebox.showerror("Input Error", "Molecular weight must be positive")
                return
            
            # ========== STEP 4: Validate concentration ==========
            is_valid, _, error_msg = validate_decimal_input(conc_input)
            if not is_valid:
                messagebox.showerror("Input Error", f"Target Concentration: {error_msg}")
                return
            conc = float(conc_input)
            
            if conc <= 0:
                messagebox.showerror("Input Error", "Concentration must be positive")
                return
            
            # ========== STEP 5: Validate volume ==========
            is_valid, _, error_msg = validate_decimal_input(vol_input)
            if not is_valid:
                messagebox.showerror("Input Error", f"Target Volume: {error_msg}")
                return
            vol = float(vol_input)
            
            if vol <= 0:
                messagebox.showerror("Input Error", "Volume must be positive")
                return
            
            # ========== STEP 6: Get unit selections ==========
            conc_unit = self.conc_unit_var.get()
            vol_unit = self.vol_unit_var.get()
            solvent = self.solvent_var.get().strip()
            
            # ========== STEP 7: Perform calculation ==========
            result = calculate_stock_from_powder(mw, conc, vol, conc_unit, vol_unit)
            
            # ========== STEP 8: Display results - SIMPLIFIED ==========
            content = f"""{'═'*60}
STOCK SOLUTION
{'═'*60}

Drug:                {drug_name}
Molecular Weight:    {format_number(mw)} g/mol
Target:              {format_number(conc)} {conc_unit} in {format_number(vol)} {vol_unit}
Solvent:             {solvent if solvent else 'Not specified'}

{'─'*60}
WEIGH:  {format_result_with_unit(result['mass_mg'], 'mg')}
DISSOLVE IN:  {format_number(vol)} {vol_unit} {solvent if solvent else 'solvent'}
{'─'*60}"""
            
            self.show_results_window(
                title="Stock Solution Preparation",
                drug_name=drug_name,
                content=content
            )
            
            # ========== STEP 9: Save to history ==========
            inputs = {
                'molecular_weight': mw,
                'target_concentration': conc,
                'target_volume': vol,
                'concentration_unit': conc_unit,
                'volume_unit': vol_unit
            }
            
            self.history.add_calculation(
                calculation_type="Stock from Powder",
                drug_name=drug_name,
                inputs=inputs,
                results=result,
                solvent=solvent
            )
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred: {str(e)}")
    
    def calculate_dilution(self):
        """Perform dilution calculation and display results."""
        try:
            # Get inputs
            drug_name = self.drug_name_var.get().strip()
            stock_conc = float(self.stock_conc_var.get())
            target_conc = float(self.target_conc_var.get())
            target_vol = float(self.target_vol_var.get())
            stock_conc_unit = self.stock_conc_unit_var.get()
            target_conc_unit = self.target_conc_unit_var.get()
            vol_unit = self.vol_unit_var.get()
            solvent = self.solvent_var.get().strip()
            
            # Convert target concentration to stock concentration units
            conversion_factors = {
                ('M', 'M'): 1,
                ('M', 'mM'): 1000,
                ('M', 'µM'): 1000000,
                ('M', 'nM'): 1000000000,
                ('mM', 'M'): 0.001,
                ('mM', 'mM'): 1,
                ('mM', 'µM'): 1000,
                ('mM', 'nM'): 1000000,
                ('µM', 'M'): 0.000001,
                ('µM', 'mM'): 0.001,
                ('µM', 'µM'): 1,
                ('µM', 'nM'): 1000,
                ('nM', 'M'): 0.000000001,
                ('nM', 'mM'): 0.000001,
                ('nM', 'µM'): 0.001,
                ('nM', 'nM'): 1
            }
            
            # Convert target to stock units
            conversion_key = (stock_conc_unit, target_conc_unit)
            if conversion_key in conversion_factors:
                target_conc_in_stock_units = target_conc / conversion_factors[conversion_key]
            else:
                messagebox.showerror("Unit Error", "Unsupported unit combination")
                return
            
            # Validate inputs
            is_valid, error_msg = validate_inputs(
                concentration=stock_conc,
                volume=target_vol
            )
            
            if not is_valid:
                messagebox.showerror("Input Error", error_msg)
                return
            
            if target_conc <= 0:
                messagebox.showerror("Input Error", "Target concentration must be positive")
                return
            
            if not drug_name:
                messagebox.showwarning("Missing Input", "Please enter a drug name")
                return
            
            # Calculate using converted target concentration
            result = calculate_dilution(
                stock_conc, target_conc_in_stock_units, target_vol,
                stock_conc_unit, vol_unit
            )
            
            # Check for errors
            if result.get('error'):
                messagebox.showerror("Calculation Error", result.get('message'))
                return
            
            # Convert volumes to readable units
            stock_vol_raw = result['stock_volume']
            solvent_vol_raw = result['solvent_volume']
            stock_vol_converted, stock_vol_unit = convert_to_readable_unit(stock_vol_raw, vol_unit)
            solvent_vol_converted, solvent_vol_unit = convert_to_readable_unit(solvent_vol_raw, vol_unit)
            
            # ========== Display results - SIMPLIFIED ==========
            content = f"""{'═'*60}
WORKING SOLUTION
{'═'*60}

Drug:                {drug_name}
From Stock:          {format_number(stock_conc)} {stock_conc_unit}
Target:              {format_number(target_conc)} {target_conc_unit} in {format_number(target_vol)} {vol_unit}
Dilution Factor:     {format_number(result['dilution_factor'])}x
Solvent:             {solvent if solvent else 'Not specified'}

{'─'*60}
TAKE:  {format_number(stock_vol_converted)} {stock_vol_unit} of stock
ADD:   {format_number(solvent_vol_converted)} {solvent_vol_unit} of {solvent if solvent else 'solvent'}
{'─'*60}"""
            
            self.show_results_window(
                title="Working Solution Preparation",
                drug_name=drug_name,
                content=content
            )
            
            # Save to history with BOTH concentration units
            inputs = {
                'stock_concentration': stock_conc,
                'target_concentration': target_conc,
                'target_volume': target_vol,
                'stock_concentration_unit': stock_conc_unit,
                'target_concentration_unit': target_conc_unit,
                'volume_unit': vol_unit
            }
            
            self.history.add_calculation(
                calculation_type="Working from Stock",
                drug_name=drug_name,
                inputs=inputs,
                results=result,
                solvent=solvent
            )
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred: {str(e)}")
    
    def clear_inputs(self):
        """Clear all input fields."""
        if self.current_mode == "stock":
            self.drug_name_var.set("")
            self.mw_var.set("")
            self.conc_var.set("")
            self.vol_var.set("")
            self.solvent_var.set("")
        elif self.current_mode == "dilution":
            self.drug_name_var.set("")
            self.stock_conc_var.set("")
            self.target_conc_var.set("")
            self.target_vol_var.set("")
            self.solvent_var.set("")
    
    def show_results_window(self, title: str, drug_name: str, content: str):
        """
        Display calculation results in a popup window.
        
        Parameters
        ----------
        title : str
            Window title
        drug_name : str
            Name of the drug
        content : str
            Formatted result text to display
        """
        # Create popup window
        results_window = tk.Toplevel(self.root)
        results_window.title(f"{title} - {drug_name}")
        results_window.geometry("650x400")
        
        # Make it modal (stay on top)
        results_window.transient(self.root)
        results_window.grab_set()
        
        # Main frame
        frame = ttk.Frame(results_window, padding="15")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        results_window.columnconfigure(0, weight=1)
        results_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            frame,
            text=title,
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Results text (scrollable)
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        results_text = scrolledtext.ScrolledText(
            text_frame,
            height=15,
            width=70,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_text.insert(1.0, content)
        results_text.configure(state='disabled')  # Make read-only
        
        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        # Copy to clipboard button
        def copy_to_clipboard():
            results_window.clipboard_clear()
            results_window.clipboard_append(content)
            messagebox.showinfo("Copied", "Protocol copied to clipboard!", parent=results_window)
        
        ttk.Button(
            btn_frame,
            text="Copy Protocol",
            command=copy_to_clipboard
        ).grid(row=0, column=0, padx=5)
        
        # Close button
        ttk.Button(
            btn_frame,
            text="Close",
            command=results_window.destroy
        ).grid(row=0, column=1, padx=5)
        
        # Center the window
        results_window.update_idletasks()
        width = results_window.winfo_width()
        height = results_window.winfo_height()
        x = (results_window.winfo_screenwidth() // 2) - (width // 2)
        y = (results_window.winfo_screenheight() // 2) - (height // 2)
        results_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_history(self):
        """Display calculation history with search and filtering."""
        self.clear_frame()
        self.current_mode = "history"
        
        # Title
        title = ttk.Label(
            self.main_frame,
            text="Calculation History",
            font=('Arial', 16, 'bold')
        )
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Control frame (search + filter + sort)
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Search bar
        ttk.Label(control_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.update_history_display())
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=5)
        
        # Filter by type
        ttk.Label(control_frame, text="Show:").grid(row=0, column=2, padx=(20, 5))
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            control_frame,
            textvariable=self.filter_var,
            values=["All", "Stock Solutions", "Working Solutions"],
            state="readonly",
            width=18
        )
        filter_combo.grid(row=0, column=3, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.update_history_display())
        
        # Sort options
        ttk.Label(control_frame, text="Sort by:").grid(row=0, column=4, padx=(20, 5))
        self.sort_var = tk.StringVar(value="Date (newest first)")
        sort_combo = ttk.Combobox(
            control_frame,
            textvariable=self.sort_var,
            values=["Date (newest first)", "Date (oldest first)", "Drug name (A-Z)", "Drug name (Z-A)"],
            state="readonly",
            width=20
        )
        sort_combo.grid(row=0, column=5, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.update_history_display())
        
        # History display frame
        history_frame = ttk.Frame(self.main_frame)
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create Treeview with scrollbar
        tree_scroll = ttk.Scrollbar(history_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("#", "Date", "Drug", "Type", "Value", "Solvent")
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show='headings',
            yscrollcommand=tree_scroll.set,
            selectmode='browse'
        )
        tree_scroll.config(command=self.history_tree.yview)
        
        # Configure columns
        self.history_tree.heading("#", text="#")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Drug", text="Drug Name")
        self.history_tree.heading("Type", text="Type")
        self.history_tree.heading("Value", text="Concentration & Volume")
        self.history_tree.heading("Solvent", text="Solvent")
        
        self.history_tree.column("#", width=40, anchor=tk.CENTER)
        self.history_tree.column("Date", width=100, anchor=tk.W)
        self.history_tree.column("Drug", width=150, anchor=tk.W)
        self.history_tree.column("Type", width=80, anchor=tk.CENTER)
        self.history_tree.column("Value", width=200, anchor=tk.W)
        self.history_tree.column("Solvent", width=100, anchor=tk.W)
        
        # Add alternating row colors
        self.history_tree.tag_configure('oddrow', background='white')
        self.history_tree.tag_configure('evenrow', background='#f0f0f0')
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to show details
        self.history_tree.bind('<Double-1>', self.show_calculation_details)
        
        # Button frame
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="View Details", command=lambda: self.show_calculation_details(None)).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(btn_frame, text="Back to Menu", command=self.show_welcome_screen).grid(
            row=0, column=2, padx=5
        )
        
        # Configure grid weights
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # Initial display
        self.update_history_display()
    
    def update_history_display(self):
        """Update history display based on search and filter criteria."""
        # Clear current display
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get all calculations
        all_calculations = self.history.get_all_calculations()
        
        # Apply search filter
        search_term = self.search_var.get().lower()
        if search_term:
            all_calculations = [
                calc for calc in all_calculations
                if search_term in calc['drug_name'].lower() or
                   search_term in calc.get('solvent', '').lower()
            ]
        
        # Apply type filter
        filter_type = self.filter_var.get()
        if filter_type == "Stock Solutions":
            all_calculations = [calc for calc in all_calculations if calc['calculation_type'] == "Stock from Powder"]
        elif filter_type == "Working Solutions":
            all_calculations = [calc for calc in all_calculations if calc['calculation_type'] == "Working from Stock"]
        
        # Store for access in details view
        self.current_calculations = all_calculations
        
        # Apply sorting
        sorted_calcs = all_calculations.copy()
        sort_by = self.sort_var.get()
        
        if sort_by == "Date (newest first)":
            sorted_calcs.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == "Date (oldest first)":
            sorted_calcs.sort(key=lambda x: x['timestamp'])
        elif sort_by == "Drug name (A-Z)":
            sorted_calcs.sort(key=lambda x: x['drug_name'].lower())
        elif sort_by == "Drug name (Z-A)":
            sorted_calcs.sort(key=lambda x: x['drug_name'].lower(), reverse=True)
        
        # Populate list with alternating colors
        for i, calc in enumerate(sorted_calcs, 1):
            date = calc['timestamp'].split('T')[0]
            drug = calc['drug_name']
            calc_type = "Stock" if calc['calculation_type'] == "Stock from Powder" else "Working"
            solvent = calc.get('solvent', 'N/A')
            
            # Format the value column based on type - WITH BACKWARD COMPATIBILITY
            inputs = calc['inputs']
            if calc['calculation_type'] == "Stock from Powder":
                conc = format_number(inputs.get('target_concentration', 0))
                vol = format_number(inputs.get('target_volume', 0))
                conc_unit = inputs.get('concentration_unit', '?')
                vol_unit = inputs.get('volume_unit', '?')
                value = f"{conc} {conc_unit} in {vol} {vol_unit}"
            else:  # Working from Stock
                stock_conc = format_number(inputs.get('stock_concentration', 0))
                target_conc = format_number(inputs.get('target_concentration', 0))
                target_vol = format_number(inputs.get('target_volume', 0))
                
                # Get units with backward compatibility
                stock_unit = inputs.get('stock_concentration_unit', inputs.get('concentration_unit', '?'))
                target_unit = inputs.get('target_concentration_unit', inputs.get('concentration_unit', '?'))
                vol_unit = inputs.get('volume_unit', '?')
                
                # Display format to match stock solution: "5 µM in 1000 µL"
                value = f"{target_conc} {target_unit} in {target_vol} {vol_unit}"
            
            # Alternate row colors
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Insert into tree with tag
            self.history_tree.insert('', tk.END, values=(i, date, drug, calc_type, value, solvent), tags=(tag,))
    
    def show_calculation_details(self, event):
        """Show detailed view of selected calculation in popup window."""
        # Get selected item
        selection = self.history_tree.selection()
        if not selection:
            return
        
        # Get the index
        item = self.history_tree.item(selection[0])
        values = item['values']
        display_num = values[0]
        
        # Find the actual calculation
        sorted_calcs = self.current_calculations.copy()
        sort_by = self.sort_var.get()
        
        if sort_by == "Date (newest first)":
            sorted_calcs.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == "Date (oldest first)":
            sorted_calcs.sort(key=lambda x: x['timestamp'])
        elif sort_by == "Drug name (A-Z)":
            sorted_calcs.sort(key=lambda x: x['drug_name'].lower())
        elif sort_by == "Drug name (Z-A)":
            sorted_calcs.sort(key=lambda x: x['drug_name'].lower(), reverse=True)
        
        calc = sorted_calcs[display_num - 1]
        
        # Create popup window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"{calc['calculation_type']} - {calc['drug_name']}")
        details_window.geometry("700x450")
        
        # Make it modal but don't grab yet (causes issues)
        details_window.transient(self.root)
        details_window.focus_set()  # Give it focus
        
        # Main frame
        frame = ttk.Frame(details_window, padding="15")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        details_window.columnconfigure(0, weight=1)
        details_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            frame,
            text=f"Calculation #{display_num}: {calc['drug_name']}",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Details text
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        details_text = scrolledtext.ScrolledText(
            text_frame,
            height=18,
            width=80,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Format the content - SIMPLIFIED VERSION WITH BACKWARD COMPATIBILITY
        timestamp = calc['timestamp'].split('T')[0]
        drug_name = calc['drug_name']
        calc_type = calc['calculation_type']
        solvent = calc.get('solvent', 'Not specified')
        inputs = calc['inputs']
        results = calc['results']
        
        content = f"""{'═'*70}
#{display_num} │ {timestamp} │ {drug_name}
{'═'*70}

"""
        
        if calc_type == "Stock from Powder":
            mw = format_number(inputs.get('molecular_weight', 0))
            conc = format_number(inputs.get('target_concentration', 0))
            vol = format_number(inputs.get('target_volume', 0))
            conc_unit = inputs.get('concentration_unit', '?')
            vol_unit = inputs.get('volume_unit', '?')
            mass_mg = format_number(results.get('mass_mg', 0))
            
            content += f"""STOCK SOLUTION

Drug:                {drug_name}
Molecular Weight:    {mw} g/mol
Target:              {conc} {conc_unit} in {vol} {vol_unit}
Solvent:             {solvent}

{'─'*70}
WEIGH:  {mass_mg} mg
DISSOLVE IN:  {vol} {vol_unit} of {solvent}
{'─'*70}
"""
        else:  # Working from Stock
            stock_conc = format_number(inputs.get('stock_concentration', 0))
            target_conc = format_number(inputs.get('target_concentration', 0))
            target_vol = format_number(inputs.get('target_volume', 0))
            
            # Get units with backward compatibility
            stock_conc_unit = inputs.get('stock_concentration_unit', inputs.get('concentration_unit', '?'))
            target_conc_unit = inputs.get('target_concentration_unit', inputs.get('concentration_unit', '?'))
            vol_unit = inputs.get('volume_unit', '?')
            
            # Smart unit conversion for volumes
            stock_vol_raw = results.get('stock_volume', 0)
            solvent_vol_raw = results.get('solvent_volume', 0)
            
            # Convert to readable units
            stock_vol_converted, stock_vol_unit = convert_to_readable_unit(stock_vol_raw, vol_unit)
            solvent_vol_converted, solvent_vol_unit = convert_to_readable_unit(solvent_vol_raw, vol_unit)
            
            stock_vol = format_number(stock_vol_converted)
            solvent_vol = format_number(solvent_vol_converted)
            dilution = format_number(results.get('dilution_factor', 0))
            
            content += f"""WORKING SOLUTION

Drug:                {drug_name}
From Stock:          {stock_conc} {stock_conc_unit}
Target:              {target_conc} {target_conc_unit} in {target_vol} {vol_unit}
Dilution Factor:     {dilution}x
Solvent:             {solvent}

{'─'*70}
TAKE:  {stock_vol} {stock_vol_unit} of stock
ADD:   {solvent_vol} {solvent_vol_unit} of {solvent}
{'─'*70}
"""
        
        details_text.insert(1.0, content)
        details_text.configure(state='disabled')
        
        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, pady=(10, 0))
        
        # Copy to clipboard button
        def copy_to_clipboard():
            details_window.clipboard_clear()
            details_window.clipboard_append(content)
            messagebox.showinfo("Copied", "Protocol copied to clipboard!", parent=details_window)
        
        ttk.Button(
            btn_frame,
            text="Copy Protocol",
            command=copy_to_clipboard
        ).grid(row=0, column=0, padx=5)
        
        # Close button
        ttk.Button(
            btn_frame,
            text="Close",
            command=details_window.destroy
        ).grid(row=0, column=1, padx=5)
        
        # Center the window
        details_window.update_idletasks()
        width = details_window.winfo_width()
        height = details_window.winfo_height()
        x = (details_window.winfo_screenwidth() // 2) - (width // 2)
        y = (details_window.winfo_screenheight() // 2) - (height // 2)
        details_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def clear_history(self):
        """Clear all calculation history after confirmation."""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete all calculation history?"):
            self.history.clear_all()
            self.update_history_display()
            messagebox.showinfo("History Cleared", "All calculations have been deleted")


def main():
    """Launch the Drug Dosage Calculator application."""
    root = tk.Tk()
    app = DrugCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
