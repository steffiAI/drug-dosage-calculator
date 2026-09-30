"""
GUI Integration Module for PubChem API Lookup (CustomTkinter migration).

MIGRATION STATUS (increment 2 of 4):
    [x] AboutDialog
    [x] MolecularWeightLookupWidget

Author: Stefanie Strasser
GitHub: https://github.com/steffiAI/drug-dosage-calculator
License: MIT
"""

import sys
import ctypes
import threading
from pathlib import Path
from tkinter import messagebox, simpledialog
from typing import Optional

import customtkinter as ctk

from pubchem_api import PubChemAPI
from font_manager import FontManager

# Color tokens, matching main_ctk.py's palette.
BG = "#1E1E1E"
ROW = "#2F2F2F"
ROW_HOVER = "#3A3A3A"
CARD = "#262626"
BORDER = "#2A2A2A"
ACCENT = "#5CB8EC"
TEXT = "#FFFFFF"
MUTED = "#9AA0A6"
SUCCESS = "#6FCF6F"
ERROR = "#FF6B6B"
WARNING = "#F2C94C"


def apply_dark_titlebar(window) -> None:
    """
    Force an immersive dark Windows title bar on a Tk/CTk window.

    Parameters
    ----------
    window : tkinter.Toplevel or customtkinter equivalent
        Window to apply the dark title bar to.

    Notes
    -----
    Windows only; no-ops on other platforms or unsupported Windows builds.
    """
    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
        )
    except Exception:
        pass


def center_window(window, parent=None) -> None:
    """
    Center a window on screen or over a parent window.

    Parameters
    ----------
    window : tkinter window
        Window to center.
    parent : tkinter window, optional
        Parent window to center over. If None, centers on screen.
    """
    window.update_idletasks()

    if parent is None:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (window.winfo_width() // 2)
        y = (screen_height // 2) - (window.winfo_height() // 2)
    else:
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (window.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (window.winfo_height() // 2)

    window.geometry(f"+{x}+{y}")


class AboutDialog:
    """
    About dialog window shown from the "About" button.

    Parameters
    ----------
    parent : customtkinter.CTk or customtkinter.CTkToplevel
        Parent window this dialog is opened from.
    font_manager : FontManager
        Font manager instance for consistent font sizing.
    """

    def __init__(self, parent, font_manager: FontManager) -> None:
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("About")
        self.dialog.geometry("500x580")
        self.dialog.configure(fg_color=BG)
        self.dialog.resizable(False, False)

        try:
            if getattr(sys, "frozen", False):
                icon_path = Path(sys._MEIPASS) / "assets" / "icon.ico"
            else:
                icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.dialog.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.dialog.transient(parent)
        apply_dark_titlebar(self.dialog)
        self.dialog.focus_set()

        info_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # Title
        ctk.CTkLabel(
            info_frame,
            text="Drug Concentration Calculator",
            font=font_manager.get_font('button', weight='bold'),
            text_color=TEXT,
        ).pack(pady=(0, 15))

        # Description
        description = (
            "A professional tool for calculating stock and working\n"
            "solution concentrations.\n\n"
            "Features automated molecular weight lookup via\n"
            "PubChem database integration and calculation history."
        )
        ctk.CTkLabel(
            info_frame,
            text=description,
            font=font_manager.get_font('small'),
            justify="center",
            text_color=MUTED,
        ).pack(pady=10)

        self._separator(info_frame)

        # Author info
        ctk.CTkLabel(
            info_frame,
            text="Developed by",
            font=font_manager.get_font('small'),
            text_color=MUTED,
        ).pack()

        ctk.CTkLabel(
            info_frame,
            text="Stefanie Strasser",
            font=font_manager.get_font('body', weight='bold'),
            text_color=ACCENT,
        ).pack(pady=(5, 15))

        # GitHub and feedback
        ctk.CTkLabel(
            info_frame,
            text="GitHub Repository:",
            font=font_manager.get_font('small'),
            text_color=MUTED,
        ).pack(pady=(0, 3))

        ctk.CTkLabel(
            info_frame,
            text="github.com/steffiAI/drug-dosage-calculator",
            font=font_manager.get_font('small', weight='bold'),
            text_color=ACCENT,
        ).pack()

        ctk.CTkLabel(
            info_frame,
            text="Report issues or suggest features via GitHub",
            font=font_manager.get_font('small'),
            text_color=MUTED,
        ).pack(pady=(8, 0))

        self._separator(info_frame)

        # License
        ctk.CTkLabel(
            info_frame,
            text="Licensed under MIT License",
            font=font_manager.get_font('small'),
            text_color=MUTED,
        ).pack(pady=(5, 0))

        ctk.CTkLabel(
            info_frame,
            text="Open-source software for the research community",
            font=font_manager.get_font('small'),
            text_color=MUTED,
        ).pack()

        # Close button
        ctk.CTkButton(
            info_frame,
            text="Close",
            command=self.dialog.destroy,
            width=140,
            height=36,
            font=font_manager.get_font('small', weight='bold'),
            fg_color=CARD,
            hover_color="#2E2E2E",
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
        ).pack(pady=20)

        # Center window after everything is laid out
        self.dialog.update_idletasks()
        self.dialog.after(10, lambda: center_window(self.dialog, parent))

    @staticmethod
    def _separator(parent: ctk.CTkFrame) -> None:
        """
        Add a thin horizontal divider line.

        Parameters
        ----------
        parent : customtkinter.CTkFrame
            Frame to place the divider in.
        """
        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", pady=15)


class MolecularWeightLookupWidget:
    """
    Lookup button + status label for PubChem molecular weight lookup.

    Parameters
    ----------
    parent_frame : customtkinter.CTkFrame
        Frame to place the widget in.
    drug_name_var : tkinter.StringVar
        Variable holding the drug name or CAS number to search.
    mw_var : tkinter.StringVar
        Variable to fill with the looked-up molecular weight.
    font_manager : FontManager
        Font manager instance for consistent font sizing.
    row : int, default=0
        Grid row for placement.
    column_start : int, default=3
        Starting grid column.
    """

    def __init__(
        self,
        parent_frame: ctk.CTkFrame,
        drug_name_var,
        mw_var,
        font_manager: FontManager,
        row: int = 0,
        column_start: int = 3,
    ) -> None:
        self.frame = parent_frame
        self.drug_name_var = drug_name_var
        self.mw_var = mw_var
        self.font_manager = font_manager
        self.api = PubChemAPI()
        self.current_result: Optional[dict] = None

        self.lookup_button = ctk.CTkButton(
            parent_frame,
            text="Lookup MW",
            command=self._on_lookup_clicked,
            fg_color=ROW,
            hover_color=ROW_HOVER,
            text_color=ACCENT,
            font=font_manager.get_font('small', weight='bold'),
            width=120,
            height=28,
        )
        self.lookup_button.grid(row=row, column=column_start, padx=(8, 16), pady=2, sticky="e")

        self.status_label = ctk.CTkLabel(
            parent_frame, text="", font=font_manager.get_font('small'), text_color=MUTED,
            justify="left", anchor="w",
        )
        self.status_label.grid(
            row=row, column=column_start + 1, columnspan=2, padx=5, sticky="w"
        )

    def _get_display_name(self, result: dict) -> str:
        """
        Get the preferred compound name from a PubChem result, Title Case.

        Parameters
        ----------
        result : dict
            PubChem lookup result.

        Returns
        -------
        str
        """
        if result.get("synonyms"):
            return result["synonyms"][0].title()
        return result.get("molecular_formula", "Unknown")

    def _on_lookup_clicked(self) -> None:
        """Handle the Lookup button click; runs the API call on a background thread."""
        user_input = self.drug_name_var.get().strip()
        if not user_input:
            messagebox.showwarning("Input Required", "Please enter a drug name or CAS number first.")
            return

        self.lookup_button.configure(text="Searching...", state="disabled")
        self.status_label.configure(text="Searching PubChem...", text_color=ACCENT)
        self.frame.update()

        threading.Thread(target=self._perform_lookup, args=(user_input,), daemon=True).start()

    def _perform_lookup(self, identifier: str) -> None:
        """
        Run the PubChem lookup off the main thread, then hand off to the GUI thread.

        Parameters
        ----------
        identifier : str
            Drug name or CAS number to search.
        """
        try:
            result, _ = self.api.robust_lookup(identifier)
            self.frame.after(0, self._handle_lookup_result, result, identifier)
        except Exception as e:
            self.frame.after(0, self._handle_lookup_error, str(e))

    def _handle_lookup_result(self, result: Optional[dict], identifier: str) -> None:
        """
        Apply a lookup result on the main thread.

        Parameters
        ----------
        result : dict or None
            Lookup result, or None if not found.
        identifier : str
            Original search identifier.
        """
        self.lookup_button.configure(text="Lookup MW", state="normal")

        if result:
            self.current_result = result
            display_name = self._get_display_name(result)
            self.mw_var.set(f"{result['molecular_weight']:.2f}")

            # The compound info popup (below) already shows name/formula,
            # so nothing needs repeating here - avoids widening the card.
            self.status_label.configure(text="", text_color=SUCCESS)
            self._show_compound_info(result, display_name)
        else:
            self.status_label.configure(text="Not found", text_color=ERROR)
            if messagebox.askyesno(
                "Compound Not Found",
                f"Could not find '{identifier}' in PubChem.\n\n"
                "Suggestions:\n\u2022 Check spelling\n\u2022 Try a CAS number\n"
                "\u2022 Use an alternative name\n\nEnter the molecular weight manually?",
            ):
                mw = simpledialog.askfloat(
                    "Manual Entry",
                    f"Enter molecular weight for '{identifier}' (g/mol):",
                    minvalue=0,
                    maxvalue=100000,
                )
                if mw:
                    self.mw_var.set(f"{mw:.2f}")
                    self.status_label.configure(text="Manually entered", text_color=WARNING)

    def _handle_lookup_error(self, error_msg: str) -> None:
        """
        Handle a lookup error on the main thread.

        Parameters
        ----------
        error_msg : str
            Error message to display.
        """
        self.lookup_button.configure(text="Lookup MW", state="normal")
        self.status_label.configure(text="Error", text_color=ERROR)
        messagebox.showerror(
            "Lookup Error",
            f"An error occurred during lookup:\n\n{error_msg}\n\n"
            "Please check your internet connection and try again.",
        )

    def _show_compound_info(self, result: dict, display_name: str) -> None:
        """
        Show a popup with full compound details.

        Parameters
        ----------
        result : dict
            PubChem lookup result.
        display_name : str
            Normalized compound name for the popup title.
        """
        win = ctk.CTkToplevel(self.frame)
        win.title(f"Compound Information - {display_name}")
        win.geometry("550x500")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.transient(self.frame.winfo_toplevel())

        try:
            icon_path = (
                Path(sys._MEIPASS) / "assets" / "icon.ico"
                if getattr(sys, "frozen", False)
                else Path(__file__).parent.parent / "assets" / "icon.ico"
            )
            if icon_path.exists():
                win.iconbitmap(str(icon_path))
        except Exception:
            pass
        apply_dark_titlebar(win)

        header = ctk.CTkFrame(win, fg_color=CARD, corner_radius=0, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text=display_name,
            font=self.font_manager.get_font('button', weight='bold'),
            text_color=TEXT,
        ).pack(pady=16)

        cache_status = "Cached data" if result.get("cached") else "Fresh from PubChem"
        pubchem_url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{result['cid']}"
        synonyms = "\n".join(f"  \u2022 {syn}" for syn in result["synonyms"][:10])
        info_text = (
            f"Compound Name: {display_name}\n"
            f"Molecular Formula: {result['molecular_formula']}\n"
            f"Molecular Weight: {result['molecular_weight']:.2f} g/mol\n"
            f"IUPAC Name: {result['iupac_name']}\n"
            f"PubChem CID: {result['cid']}\n\n"
            f"Common Names / Synonyms:\n{synonyms}\n\n"
            f"Data Source: {cache_status}\n"
            f"Lookup Date: {result.get('lookup_date', 'Unknown')[:10]}\n\n"
            f"PubChem Link:\n{pubchem_url}\n"
        )

        text = ctk.CTkTextbox(
            win, fg_color=BG, text_color=TEXT, font=self.font_manager.get_font('small'), wrap="word"
        )
        text.pack(fill="both", expand=True, padx=15, pady=15)
        text.insert("1.0", info_text)
        text.configure(state="disabled")

        ctk.CTkButton(
            win, text="Close", command=win.destroy, fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT
        ).pack(pady=(0, 15))

        parent_win = self.frame.winfo_toplevel()
        center_window(win, parent_win)
