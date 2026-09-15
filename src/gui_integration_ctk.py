"""
GUI Integration Module for PubChem API Lookup (CustomTkinter migration).

MIGRATION STATUS (increment 1 of 4):
    [x] AboutDialog
    [ ] MolecularWeightLookupWidget -> still tkinter/ttk, migrated in increment 2

Until increment 2, keep the original ``gui_integration.py`` alongside this
file - ``main_ctk.py`` only imports ``AboutDialog`` from here so far.

Author: Stefanie Strasser
GitHub: https://github.com/steffiAI/drug-dosage-calculator
License: MIT
"""

import sys
from pathlib import Path

import customtkinter as ctk

# Color tokens, matching main_ctk.py's palette.
BG = "#1E1E1E"
CARD = "#262626"
BORDER = "#2A2A2A"
ACCENT = "#5CB8EC"
TEXT = "#FFFFFF"
MUTED = "#9AA0A6"


class AboutDialog:
    """
    About dialog window shown from the "About" button.

    Parameters
    ----------
    parent : customtkinter.CTk or customtkinter.CTkToplevel
        Parent window this dialog is opened from.
    """

    def __init__(self, parent) -> None:
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("About")
        self.dialog.geometry("480x560")
        self.dialog.resizable(False, False)
        self.dialog.configure(fg_color=BG)

        try:
            if getattr(sys, "frozen", False):
                icon_path = Path(sys._MEIPASS) / "assets" / "icon.ico"
            else:
                icon_path = Path(__file__).parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.dialog.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.dialog.transient(parent)
        self.dialog.focus_set()

        info_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # Title
        ctk.CTkLabel(
            info_frame,
            text="Drug Concentration Calculator",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=16, weight="bold"),
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
            font=ctk.CTkFont(family="Segoe UI", size=12),
            justify="center",
            text_color=MUTED,
        ).pack(pady=10)

        self._separator(info_frame)

        # Author info
        ctk.CTkLabel(
            info_frame,
            text="Developed by",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=MUTED,
        ).pack()

        ctk.CTkLabel(
            info_frame,
            text="Stefanie Strasser",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=14, weight="bold"),
            text_color=ACCENT,
        ).pack(pady=(5, 3))

        ctk.CTkLabel(
            info_frame,
            text="s.strasser387@gmail.com",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=MUTED,
        ).pack(pady=(0, 15))

        # GitHub link (text only, same as original - no webbrowser call)
        ctk.CTkLabel(
            info_frame,
            text="GitHub Repository:",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=MUTED,
        ).pack(pady=(10, 3))

        ctk.CTkLabel(
            info_frame,
            text="github.com/steffiAI/drug-dosage-calculator",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=ACCENT,
        ).pack()

        self._separator(info_frame)

        # License
        ctk.CTkLabel(
            info_frame,
            text="Licensed under MIT License",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=MUTED,
        ).pack(pady=(5, 0))

        ctk.CTkLabel(
            info_frame,
            text="Open-source software for the research community",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=MUTED,
        ).pack()

        # Close button
        ctk.CTkButton(
            info_frame,
            text="Close",
            command=self.dialog.destroy,
            width=140,
            height=36,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12, weight="bold"),
            fg_color=CARD,
            hover_color="#2E2E2E",
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
        ).pack(pady=20)

        # Center on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (480 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (560 // 2)
        self.dialog.geometry(f"+{x}+{y}")

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
