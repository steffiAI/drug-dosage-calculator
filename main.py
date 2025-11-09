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
    
    def show_welcome_screen(self):
        """Display welcome screen with calculator selection buttons."""
        self.clear_frame()
        self.current_mode = None
        
        # Title
        title = ttk.Label(
            self.main_frame,
            text="Drug Dosage Calculator",
            font=('Arial', 18, 'bold')
        )
        title.grid(row=0, column=0, pady=20)
        
        subtitle = ttk.Label(
            self.main_frame,
            text="Laboratory Solution Preparation Tool",
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
        """Display stock solution calculator interface."""
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
        
        # Drug name
        ttk.Label(input_frame, text="Drug Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.drug_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.drug_name_var, width=30).grid(
            row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        
        # Molecular weight
        ttk.Label(input_frame, text="Molecular Weight (g/mol):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.mw_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.mw_var, width=15).grid(
            row=1, column=1, sticky=tk.W, pady=5
        )
        
        # Target concentration
        ttk.Label(input_frame, text="Target Concentration:").grid(row=2, column=0, sticky=tk.W, pady=5)
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
        
        # Target volume
        ttk.Label(input_frame, text="Target Volume:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.vol_var = tk.StringVar()
        vol_entry = ttk.Entry(input_frame, textvariable=self.vol_var, width=15)
        vol_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Volume unit dropdown
        self.vol_unit_var = tk.StringVar(value="mL")
        vol_units = ttk.Combobox(
            input_frame,
            textvariable=self.vol_unit_var,
            values=["L", "mL", "µL"],
            state="readonly",
            width=8
        )
        vol_units.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Solvent
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
        
        # Drug name
        ttk.Label(input_frame, text="Drug Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.drug_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.drug_name_var, width=30).grid(
            row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        
        # Stock concentration
        ttk.Label(input_frame, text="Stock Concentration:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.stock_conc_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.stock_conc_var, width=15).grid(
            row=1, column=1, sticky=tk.W, pady=5
        )
        
        # Stock concentration unit
        self.stock_conc_unit_var = tk.StringVar(value="mM")
        stock_conc_units = ttk.Combobox(
            input_frame,
            textvariable=self.stock_conc_unit_var,
            values=["M", "mM", "µM", "nM"],
            state="readonly",
            width=8
        )
        stock_conc_units.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Target concentration
        ttk.Label(input_frame, text="Target Concentration:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.target_conc_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.target_conc_var, width=15).grid(
            row=2, column=1, sticky=tk.W, pady=5
        )
        
        # Target concentration unit (same as stock)
        self.target_conc_unit_var = tk.StringVar(value="µM")
        target_conc_units = ttk.Combobox(
            input_frame,
            textvariable=self.target_conc_unit_var,
            values=["M", "mM", "µM", "nM"],
            state="readonly",
            width=8
        )
        target_conc_units.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Target volume
        ttk.Label(input_frame, text="Target Volume:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.target_vol_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.target_vol_var, width=15).grid(
            row=3, column=1, sticky=tk.W, pady=5
        )
        
        # Volume unit
        self.vol_unit_var = tk.StringVar(value="mL")
        vol_units = ttk.Combobox(
            input_frame,
            textvariable=self.vol_unit_var,
            values=["L", "mL", "µL"],
            state="readonly",
            width=8
        )
        vol_units.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Solvent
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
    
    def calculate_stock(self):
        """Perform stock solution calculation and display results."""
        try:
            # Get inputs
            drug_name = self.drug_name_var.get().strip()
            mw = float(self.mw_var.get())
            conc = float(self.conc_var.get())
            vol = float(self.vol_var.get())
            conc_unit = self.conc_unit_var.get()
            vol_unit = self.vol_unit_var.get()
            solvent = self.solvent_var.get().strip()
            
            # Validate inputs
            is_valid, error_msg = validate_inputs(
                molecular_weight=mw,
                concentration=conc,
                volume=vol
            )
            
            if not is_valid:
                messagebox.showerror("Input Error", error_msg)
                return
            
            if not drug_name:
                messagebox.showwarning("Missing Input", "Please enter a drug name")
                return
            
            # Calculate
            result = calculate_stock_from_powder(mw, conc, vol, conc_unit, vol_unit)
            
            # Create results in popup window
            self.show_results_window(
                title="Stock Solution Preparation",
                drug_name=drug_name,
                content=f"""Drug: {drug_name}
Molecular Weight: {mw} g/mol
Target: {conc} {conc_unit} in {vol} {vol_unit}
Solvent: {solvent if solvent else 'Not specified'}

═══════════════════════════════════════════════════════════
INSTRUCTIONS:
═══════════════════════════════════════════════════════════

1. Weigh {result['mass_mg']:.4f} mg of {drug_name}
   (or {result['mass_g']:.6f} g)

2. Add approximately 80% of final volume of {solvent if solvent else 'solvent'}
   (~{result['volume'] * 0.8:.2f} {vol_unit})

3. Dissolve completely (vortex/sonicate if needed)

4. Bring to final volume: {result['volume']} {vol_unit}

5. Label with:
   - Drug name: {drug_name}
   - Concentration: {conc} {conc_unit}
   - Date prepared
   - Your initials"""
            )
            
            # Save to history
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
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred: {str(e)}")
    
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
            
            # Create results in popup window
            self.show_results_window(
                title="Working Solution Preparation",
                drug_name=drug_name,
                content=f"""Drug: {drug_name}
Stock Concentration: {stock_conc} {stock_conc_unit}
Target: {target_conc} {target_conc_unit} in {target_vol} {vol_unit}
Dilution Factor: {result['dilution_factor']:.1f}x
Solvent: {solvent if solvent else 'Not specified'}

═══════════════════════════════════════════════════════════
INSTRUCTIONS:
═══════════════════════════════════════════════════════════

1. Pipette {result['stock_volume']:.4f} {vol_unit} of stock solution

2. Add {result['solvent_volume']:.4f} {vol_unit} of {solvent if solvent else 'solvent'}

3. Mix thoroughly (vortex or pipette up/down)

4. Final volume: {result['total_volume']} {vol_unit}

5. Label with:
   - Drug name: {drug_name}
   - Concentration: {target_conc} {target_conc_unit}
   - Date prepared
   - Your initials"""
            )
            
            # Save to history
            inputs = {
                'stock_concentration': stock_conc,
                'target_concentration': target_conc,
                'target_volume': target_vol,
                'concentration_unit': stock_conc_unit,
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
        results_window.geometry("650x500")
        
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
            height=20,
            width=75,
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
            messagebox.showinfo("Copied", "Results copied to clipboard!", parent=results_window)
        
        ttk.Button(
            btn_frame,
            text="Copy to Clipboard",
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
        """Display calculation history."""
        self.clear_frame()
        self.current_mode = "history"
        
        # Title
        title = ttk.Label(
            self.main_frame,
            text="Calculation History",
            font=('Arial', 16, 'bold')
        )
        title.grid(row=0, column=0, pady=10)
        
        # Button frame
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=1, column=0, pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.show_history).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frame, text="Back to Menu", command=self.show_welcome_screen).grid(
            row=0, column=1, padx=5
        )
        
        # History display
        history_frame = ttk.LabelFrame(self.main_frame, text="Saved Calculations", padding="10")
        history_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        history_text = scrolledtext.ScrolledText(
            history_frame,
            height=25,
            width=80,
            font=('Courier', 9)
        )
        history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load and display history
        calculations = self.history.get_all_calculations()
        
        if not calculations:
            history_text.insert(1.0, "No calculations saved yet.\n")
        else:
            for i, calc in enumerate(calculations, 1):
                timestamp = calc['timestamp'].split('T')[0]  # Just date
                entry = f"""
{'='*70}
Entry #{i} - {calc['calculation_type']}
{'='*70}
Date: {timestamp}
Drug: {calc['drug_name']}
Solvent: {calc.get('solvent', 'Not specified')}

"""
                if calc['calculation_type'] == "Stock from Powder":
                    inputs = calc['inputs']
                    results = calc['results']
                    entry += f"""Inputs:
  - Molecular Weight: {inputs['molecular_weight']} g/mol
  - Target Concentration: {inputs['target_concentration']} {inputs['concentration_unit']}
  - Target Volume: {inputs['target_volume']} {inputs['volume_unit']}

Results:
  - Weigh: {results['mass_mg']:.4f} mg ({results['mass_g']:.6f} g)
"""
                else:  # Working from Stock
                    inputs = calc['inputs']
                    results = calc['results']
                    entry += f"""Inputs:
  - Stock Concentration: {inputs['stock_concentration']} {inputs['concentration_unit']}
  - Target Concentration: {inputs['target_concentration']} {inputs['concentration_unit']}
  - Target Volume: {inputs['target_volume']} {inputs['volume_unit']}

Results:
  - Stock Volume: {results['stock_volume']:.4f} {results['volume_unit']}
  - Solvent Volume: {results['solvent_volume']:.4f} {results['volume_unit']}
  - Dilution Factor: {results['dilution_factor']:.1f}x
"""
                history_text.insert(tk.END, entry)
        
        # Configure grid weights
        self.main_frame.rowconfigure(2, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)


def main():
    """Launch the Drug Dosage Calculator application."""
    root = tk.Tk()
    app = DrugCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
