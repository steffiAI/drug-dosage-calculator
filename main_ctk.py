"""
Drug Dosage Calculator - Main GUI Application (CustomTkinter migration).

Version: v2.2.0.

MIGRATION STATUS (increment 1 of 4):
    [x] App shell, dark appearance, title bar
    [x] Welcome screen
    [x] About dialog (see gui_integration_ctk.py)
    [ ] Stock Solution Calculator screen  -> placeholder
    [ ] Working Solution Calculator screen -> placeholder
    [ ] History screen (keeps ttk.Treeview embedded)

Run this file directly to test in isolation.
"""

import sys
import ctypes
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, StringVar
from typing import Optional

import customtkinter as ctk
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui_integration_ctk import AboutDialog, MolecularWeightLookupWidget  # noqa: E402
from calculators import calculate_stock_from_powder, calculate_dilution, validate_inputs  # noqa: E402
from data_storage import CalculationHistory  # noqa: E402
from formatters import (  # noqa: E402
    format_number, validate_decimal_input, format_result_with_unit, convert_to_readable_unit,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color tokens (HANDOFF.md section 2)
BG = "#1E1E1E"
ROW = "#2F2F2F"
ROW_HOVER = "#3A3A3A"
CARD = "#262626"
INSET = "#333333"
BORDER = "#2A2A2A"
ACCENT = "#5CB8EC"
TEXT = "#FFFFFF"
MUTED = "#9AA0A6"
INSET_TEXT = "#B9BEC3"
FOOTER_COLOR = "#7D8287"

APP_VERSION = "v2.2.0"
COLUMN_WIDTH = 640


def _asset_path(*parts: str) -> Path:
    """
    Resolve a path under ``assets/``, from source or a frozen executable.

    Parameters
    ----------
    *parts : str
        Path segments under ``assets/``.

    Returns
    -------
    pathlib.Path
    """
    base = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).parent
    return base / "assets" / Path(*parts)


class CTkToolTip:
    """
    Hover tooltip for a widget, styled to match the app's dark palette.

    Parameters
    ----------
    widget : tkinter widget
        Widget to attach the tooltip to (e.g. an info-icon label).
    text : str
        Text to display on hover.
    """

    def __init__(self, widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None) -> None:
        """Display the tooltip below the widget."""
        if self.tip:
            return
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip, text=self.text, bg=CARD, fg=TEXT, font=("Segoe UI", 18),
            relief="solid", borderwidth=1, highlightbackground=BORDER, padx=6, pady=3,
        ).pack()

    def hide(self, _event=None) -> None:
        """Destroy the tooltip."""
        if self.tip:
            self.tip.destroy()
            self.tip = None


class DrugCalculatorApp:
    """
    Main application window for the drug dosage calculator (CTk version).

    Parameters
    ----------
    root : customtkinter.CTk
        Root CustomTkinter window.
    """

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Drug Concentration Calculator")
        self.root.geometry("880x580")
        self.root.minsize(560, 480)
        self.root.configure(fg_color=BG)

        # CTkImage needs a live reference or it gets garbage-collected.
        self._icon_refs: list = []

        try:
            icon_path = _asset_path("icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

        # Immersive dark title bar (Windows only; no-ops elsewhere).
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

        self._calculation_count: int = 0
        self.current_mode: Optional[str] = None
        self.history = CalculationHistory()

        # Keep family and weight separate - "Segoe UI Semibold" + bold doesn't resolve.
        self.h1_font = ctk.CTkFont(family="Segoe UI", size=34, weight="bold")
        self.about_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.row_title_font = ctk.CTkFont(family="Segoe UI", size=17, weight="bold")
        self.row_subtitle_font = ctk.CTkFont(family="Consolas", size=13)
        self.history_title_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.inset_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.footer_font = ctk.CTkFont(family="Consolas", size=13)
        self.placeholder_font = ctk.CTkFont(family="Segoe UI", size=16)
        self.button_font = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        self.form_label_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.form_entry_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.form_title_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        self.form_subtitle_font = ctk.CTkFont(family="Segoe UI", size=13)

        self.main_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        self.show_welcome_screen()

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def clear_frame(self) -> None:
        """Remove all widgets from the main frame before drawing a new screen."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self._icon_refs.clear()

    def _load_icon(self, name: str, size: int = 34) -> ctk.CTkImage:
        """
        Load an icon from ``assets/icons/`` as a CTkImage.

        Parameters
        ----------
        name : str
            Icon base name, e.g. ``"powder"`` (loads ``powder-2x.png``).
        size : int, default=34
            Display size in pixels.

        Returns
        -------
        customtkinter.CTkImage
        """
        img = Image.open(_asset_path("icons", f"{name}-2x.png"))
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        self._icon_refs.append(ctk_img)
        return ctk_img

    # ------------------------------------------------------------------
    # Welcome screen
    # ------------------------------------------------------------------
    def show_welcome_screen(self) -> None:
        """Display the welcome screen: About link, H1, hero, calculator rows, history card."""
        self.clear_frame()
        self.current_mode = None

        ctk.CTkButton(
            self.main_frame,
            text=" About",
            image=self._load_icon("info", 17),
            compound="left",
            fg_color="transparent",
            hover_color="#262626",
            text_color=MUTED,
            font=self.about_font,
            width=90,
            height=30,
            anchor="w",
            command=self.show_about_dialog,
        ).pack(anchor="w", padx=16, pady=(10, 0))

        ctk.CTkLabel(
            self.main_frame,
            text="Drug Concentration Calculator",
            font=self.h1_font,
            text_color=TEXT,
        ).pack(pady=(6, 0))

        hero_img = Image.open(_asset_path("pill3.png"))
        hero = ctk.CTkImage(light_image=hero_img, dark_image=hero_img, size=(84, 84))
        self._icon_refs.append(hero)
        ctk.CTkLabel(self.main_frame, image=hero, text="").pack(pady=(12, 20))

        col = ctk.CTkFrame(self.main_frame, fg_color="transparent", width=COLUMN_WIDTH)
        col.pack()

        self._calculator_row(
            col,
            title="Stock Solution Calculator",
            subtitle="powder -> stock",
            icons=("powder", "arrow", "tube"),
            command=self.show_stock_calculator,
        )
        self._calculator_row(
            col,
            title="Working Solution Calculator",
            subtitle="stock -> working",
            icons=("tube", "arrow", "pipette"),
            command=self.show_dilution_calculator,
        )
        self._history_card(col)

        ctk.CTkLabel(
            self.main_frame,
            text=f"{APP_VERSION} \u00b7 S. Strasser",
            font=self.footer_font,
            text_color=FOOTER_COLOR,
        ).pack(pady=(20, 0))

    def _calculator_row(self, parent, title: str, subtitle: str, icons: tuple, command) -> None:
        """
        Build one clickable calculator row: icon pair + arrow, title, mono subtitle.

        Parameters
        ----------
        parent : customtkinter.CTkFrame
            Container to place the row in.
        title : str
            Row title.
        subtitle : str
            Mono, lowercase subtitle, e.g. "powder -> stock".
        icons : tuple of str
            Icon names in sequence, e.g. ("powder", "arrow", "tube").
        command : callable
            Called when any part of the row is clicked.
        """
        frame = ctk.CTkFrame(
            parent,
            fg_color=ROW,
            corner_radius=11,
            border_width=1,
            border_color=BORDER,
            width=COLUMN_WIDTH,
        )
        frame.pack(fill="x", pady=6)
        frame.grid_columnconfigure(1, weight=1)

        icons_box = ctk.CTkFrame(frame, fg_color="transparent")
        icons_box.grid(row=0, column=0, rowspan=2, padx=(18, 18), pady=14)
        for i, name in enumerate(icons):
            size = 15 if name == "arrow" else 34
            ctk.CTkLabel(icons_box, image=self._load_icon(name, size), text="").grid(
                row=0, column=i, padx=4
            )

        ctk.CTkLabel(
            frame, text=title, font=self.row_title_font, text_color=TEXT, anchor="w"
        ).grid(row=0, column=1, sticky="sw", padx=(0, 18), pady=(14, 0))
        ctk.CTkLabel(
            frame, text=subtitle, font=self.row_subtitle_font, text_color=MUTED, anchor="w"
        ).grid(row=1, column=1, sticky="nw", padx=(0, 18), pady=(2, 14))

        def enter(_event) -> None:
            frame.configure(fg_color=ROW_HOVER)

        def leave(_event) -> None:
            frame.configure(fg_color=ROW)

        for widget in (frame, icons_box, *icons_box.winfo_children(), *frame.winfo_children()):
            widget.bind("<Button-1>", lambda _e=None: command())
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            widget.configure(cursor="hand2")

    def _history_card(self, parent) -> None:
        """
        Build the Calculation History card: history icon + title, saved-count inset.

        Parameters
        ----------
        parent : customtkinter.CTkFrame
            Container to place the card in.
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=11,
            border_width=1,
            border_color=BORDER,
            width=COLUMN_WIDTH,
        )
        card.pack(fill="x", pady=6)

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=18, pady=(13, 0))
        ctk.CTkLabel(head, image=self._load_icon("history", 24), text="").pack(side="left")
        ctk.CTkLabel(
            head, text="  Calculation History", font=self.history_title_font, text_color=TEXT
        ).pack(side="left")

        ctk.CTkLabel(
            card,
            text=f"Total calculations saved: {self._calculation_count}",
            font=self.inset_font,
            text_color=INSET_TEXT,
            fg_color=INSET,
            corner_radius=8,
            height=32,
        ).pack(fill="x", padx=18, pady=(11, 14))

        def enter(_event) -> None:
            card.configure(fg_color="#2E2E2E")

        def leave(_event) -> None:
            card.configure(fg_color=CARD)

        for widget in (card, head, *head.winfo_children()):
            widget.bind("<Button-1>", lambda _e=None: self.show_history())
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            widget.configure(cursor="hand2")

    # ------------------------------------------------------------------
    # Stock Solution Calculator
    # ------------------------------------------------------------------
    def show_stock_calculator(self) -> None:
        """Display the Stock Solution Calculator screen (powder -> stock)."""
        self.clear_frame()
        self.current_mode = "stock"

        # Wrapped in its own frame with pack(expand=True) so the block is
        # vertically centered in the window, instead of packed from the
        # top with all the leftover space collecting below the footer.
        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(expand=True)

        ctk.CTkLabel(
            content, text="Stock Solution Calculator", font=self.form_title_font, text_color=TEXT
        ).pack(pady=(20, 4))
        ctk.CTkLabel(
            content,
            text="Calculate mass of powder needed for stock solution",
            font=self.form_subtitle_font,
            text_color=MUTED,
        ).pack(pady=(0, 16))

        form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=11, border_width=1, border_color=BORDER)
        form.pack(padx=40, pady=4)
        form.grid_columnconfigure(1, weight=1)

        self.drug_name_var = StringVar()
        self._form_row(form, 0, "Drug Name:", self.drug_name_var, width=260, full_width=True)

        self.mw_var = StringVar()
        self._form_row(
            form, 1, "Molecular Weight (g/mol):", self.mw_var, width=120,
            tooltip="Use period (.) for decimal numbers",
        )
        MolecularWeightLookupWidget(form, self.drug_name_var, self.mw_var, row=1, column_start=2)

        self.conc_var = StringVar()
        self.conc_unit_var = StringVar(value="mM")
        self._form_row(
            form, 2, "Target Concentration:", self.conc_var, width=120,
            unit_var=self.conc_unit_var, unit_options=["M", "mM", "\u00b5M", "nM"],
            tooltip="Use period (.) for decimal numbers",
        )

        self.vol_var = StringVar()
        self.vol_unit_var = StringVar(value="\u00b5L")
        self._form_row(
            form, 3, "Target Volume:", self.vol_var, width=120,
            unit_var=self.vol_unit_var, unit_options=["L", "mL", "\u00b5L"],
            tooltip="Use period (.) for decimal numbers",
        )

        self.solvent_var = StringVar()
        self._form_row(
            form, 4, "Solvent:", self.solvent_var, width=260,
            unit_options=["DMSO", "Water", "Ethanol", "PBS", "Media", "Other"], is_solvent=True,
        )

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=18)
        ctk.CTkButton(
            btn_frame, text="Calculate", command=self.calculate_stock,
            fg_color=ACCENT, hover_color="#4A9FD6", text_color="#0F1C24", font=self.button_font, width=110,
        ).grid(row=0, column=0, padx=6)
        ctk.CTkButton(
            btn_frame, text="Clear", command=self.clear_inputs,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT, font=self.button_font, width=90,
        ).grid(row=0, column=1, padx=6)
        ctk.CTkButton(
            btn_frame, text="Back to Menu", command=self.show_welcome_screen,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT, font=self.button_font, width=120,
        ).grid(row=0, column=2, padx=6)

        ctk.CTkLabel(
            content, text=f"{APP_VERSION} \u00b7 S. Strasser", font=self.footer_font, text_color=FOOTER_COLOR
        ).pack(pady=(10, 0))

    def _form_row(
        self, parent, row: int, label: str, value_var, width: int = 150,
        unit_var=None, unit_options=None, is_solvent: bool = False, full_width: bool = False,
        tooltip: str = None,
    ) -> None:
        """
        Build one labeled form row: label, entry, and optional unit/solvent dropdown.

        Parameters
        ----------
        parent : customtkinter.CTkFrame
            Form frame to place the row in.
        row : int
            Grid row.
        label : str
            Field label text.
        value_var : tkinter.StringVar
            Variable bound to the entry field.
        width : int, default=150
            Entry field width in pixels.
        unit_var : tkinter.StringVar, optional
            Variable bound to a unit dropdown, if any.
        unit_options : list of str, optional
            Options for the unit dropdown, or for a solvent dropdown when
            ``is_solvent`` is True (in which case the entry becomes the dropdown).
        is_solvent : bool, default=False
            If True, ``value_var`` binds to an editable dropdown instead of a plain entry.
        full_width : bool, default=False
            If True, the entry spans into column 2 and stretches to fill it,
            so its right edge lines up with whatever ends up in column 2 on
            other rows (e.g. the MW lookup button). Only valid when the row
            has nothing else placed in column 2.
        tooltip : str, optional
            If given, an info icon is shown next to the label with this
            text on hover.
        """
        label_frame = ctk.CTkFrame(parent, fg_color="transparent")
        label_frame.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=8)
        ctk.CTkLabel(
            label_frame, text=label, font=self.form_label_font, text_color=MUTED, anchor="w"
        ).pack(side="left")
        if tooltip:
            info_icon = ctk.CTkLabel(
                label_frame, text=" \u24d8", font=self.form_label_font, text_color=ACCENT, cursor="hand2"
            )
            info_icon.pack(side="left")
            CTkToolTip(info_icon, tooltip)

        if is_solvent:
            ctk.CTkComboBox(
                parent, variable=value_var, values=unit_options or [], width=width,
                fg_color=ROW, border_color=BORDER, button_color=ROW, text_color=TEXT,
                dropdown_fg_color=ROW, font=self.form_entry_font,
            ).grid(row=row, column=1, columnspan=2, sticky="ew", padx=(0, 16), pady=8)
            return

        if full_width:
            ctk.CTkEntry(
                parent, textvariable=value_var, width=width, fg_color=ROW, border_color=BORDER,
                text_color=TEXT, font=self.form_entry_font,
            ).grid(row=row, column=1, columnspan=2, sticky="ew", padx=(0, 16), pady=8)
            return

        ctk.CTkEntry(
            parent, textvariable=value_var, width=width, fg_color=ROW, border_color=BORDER,
            text_color=TEXT, font=self.form_entry_font,
        ).grid(row=row, column=1, sticky="w", pady=8)

        if unit_var is not None:
            ctk.CTkComboBox(
                parent, variable=unit_var, values=unit_options or [], width=120,
                fg_color=ROW, border_color=BORDER, button_color=ROW, text_color=TEXT,
                dropdown_fg_color=ROW, font=self.form_entry_font,
            ).grid(row=row, column=2, sticky="e", padx=(8, 16), pady=8)
        else:
            parent.grid_columnconfigure(2, minsize=16)

    def calculate_stock(self) -> None:
        """Validate inputs, run the stock calculation, show results, and save to history."""
        drug_name = self.drug_name_var.get().strip()
        if not drug_name:
            messagebox.showerror("Input Error", "Please enter a drug name")
            return

        for label, var in (("Molecular Weight", self.mw_var), ("Target Concentration", self.conc_var), ("Target Volume", self.vol_var)):
            is_valid, _, error_msg = validate_decimal_input(var.get().strip())
            if not is_valid:
                messagebox.showerror("Input Error", f"{label}: {error_msg}")
                return

        mw, conc, vol = float(self.mw_var.get()), float(self.conc_var.get()), float(self.vol_var.get())
        is_valid, error_msg = validate_inputs(molecular_weight=mw, concentration=conc, volume=vol)
        if not is_valid:
            messagebox.showerror("Input Error", error_msg)
            return

        conc_unit, vol_unit = self.conc_unit_var.get(), self.vol_unit_var.get()
        solvent = self.solvent_var.get().strip()
        result = calculate_stock_from_powder(mw, conc, vol, conc_unit, vol_unit)

        content = (
            f"STOCK SOLUTION\n\n"
            f"Drug:                {drug_name}\n"
            f"Molecular Weight:    {format_number(mw)} g/mol\n"
            f"Target:              {format_number(conc)} {conc_unit} in {format_number(vol)} {vol_unit}\n"
            f"Solvent:             {solvent or 'Not specified'}\n\n"
            f"WEIGH:  {format_result_with_unit(result['mass_mg'], 'mg')}\n"
            f"DISSOLVE IN:  {format_number(vol)} {vol_unit} {solvent or 'solvent'}\n"
        )
        self.show_results_window("Stock Solution Preparation", drug_name, content)

        self.history.add_calculation(
            calculation_type="Stock from Powder",
            drug_name=drug_name,
            inputs={
                "molecular_weight": mw, "target_concentration": conc, "target_volume": vol,
                "concentration_unit": conc_unit, "volume_unit": vol_unit,
            },
            results=result,
            solvent=solvent,
        )
        self._calculation_count = self.history.get_calculation_count()

    def clear_inputs(self) -> None:
        """Clear the input fields for the current calculator screen."""
        if self.current_mode == "stock":
            for var in (self.drug_name_var, self.mw_var, self.conc_var, self.vol_var, self.solvent_var):
                var.set("")
        elif self.current_mode == "dilution":
            for var in (self.drug_name_var, self.stock_conc_var, self.target_conc_var, self.target_vol_var, self.solvent_var):
                var.set("")

    def show_results_window(self, title: str, drug_name: str, content: str) -> None:
        """
        Show calculation results in a popup window with a copy-to-clipboard option.

        Parameters
        ----------
        title : str
            Popup title.
        drug_name : str
            Drug name, appended to the window title.
        content : str
            Formatted result text.
        """
        win = ctk.CTkToplevel(self.root)
        win.title(f"{title} - {drug_name}")
        win.geometry("600x400")
        win.configure(fg_color=BG)
        win.transient(self.root)

        try:
            icon_path = _asset_path("icon.ico")
            if icon_path.exists():
                win.iconbitmap(str(icon_path))
        except Exception:
            pass

        ctk.CTkLabel(win, text=title, font=self.form_title_font, text_color=TEXT).pack(pady=(15, 10))

        text = ctk.CTkTextbox(
            win, fg_color=ROW, text_color=TEXT, font=ctk.CTkFont(family="Consolas", size=12), wrap="word"
        )
        text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        text.insert("1.0", content)
        text.configure(state="disabled")

        def copy_to_clipboard() -> None:
            win.clipboard_clear()
            win.clipboard_append(content)
            messagebox.showinfo("Copied", "Protocol copied to clipboard!", parent=win)

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        ctk.CTkButton(
            btn_frame, text="Copy Protocol", command=copy_to_clipboard,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT,
        ).grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            btn_frame, text="Close", command=win.destroy, fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT
        ).grid(row=0, column=1, padx=5)

    # ------------------------------------------------------------------
    # Working Solution Calculator
    # ------------------------------------------------------------------
    def show_dilution_calculator(self) -> None:
        """Display the Working Solution Calculator screen (stock -> working)."""
        self.clear_frame()
        self.current_mode = "dilution"

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(expand=True)

        ctk.CTkLabel(
            content, text="Working Solution Calculator", font=self.form_title_font, text_color=TEXT
        ).pack(pady=(20, 4))
        ctk.CTkLabel(
            content,
            text="Dilute stock solution to working concentration",
            font=self.form_subtitle_font,
            text_color=MUTED,
        ).pack(pady=(0, 16))

        form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=11, border_width=1, border_color=BORDER)
        form.pack(padx=40, pady=4)
        form.grid_columnconfigure(1, weight=1)

        self.drug_name_var = StringVar()
        self._form_row(form, 0, "Drug Name:", self.drug_name_var, width=260, full_width=True)

        self.stock_conc_var = StringVar()
        self.stock_conc_unit_var = StringVar(value="mM")
        self._form_row(
            form, 1, "Stock Concentration:", self.stock_conc_var, width=120,
            unit_var=self.stock_conc_unit_var, unit_options=["M", "mM", "\u00b5M", "nM"],
            tooltip="Use period (.) for decimal numbers",
        )

        self.target_conc_var = StringVar()
        self.target_conc_unit_var = StringVar(value="\u00b5M")
        self._form_row(
            form, 2, "Target Concentration:", self.target_conc_var, width=120,
            unit_var=self.target_conc_unit_var, unit_options=["M", "mM", "\u00b5M", "nM"],
            tooltip="Use period (.) for decimal numbers",
        )

        self.target_vol_var = StringVar()
        self.vol_unit_var = StringVar(value="\u00b5L")
        self._form_row(
            form, 3, "Target Volume:", self.target_vol_var, width=120,
            unit_var=self.vol_unit_var, unit_options=["L", "mL", "\u00b5L"],
            tooltip="Use period (.) for decimal numbers",
        )

        self.solvent_var = StringVar()
        self._form_row(
            form, 4, "Solvent:", self.solvent_var, width=260,
            unit_options=["Media", "PBS", "Water", "DMSO", "Ethanol", "Other"], is_solvent=True,
        )

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=18)
        ctk.CTkButton(
            btn_frame, text="Calculate", command=self.calculate_dilution,
            fg_color=ACCENT, hover_color="#4A9FD6", text_color="#0F1C24", font=self.button_font, width=110,
        ).grid(row=0, column=0, padx=6)
        ctk.CTkButton(
            btn_frame, text="Clear", command=self.clear_inputs,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT, font=self.button_font, width=90,
        ).grid(row=0, column=1, padx=6)
        ctk.CTkButton(
            btn_frame, text="Back to Menu", command=self.show_welcome_screen,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT, font=self.button_font, width=120,
        ).grid(row=0, column=2, padx=6)

        ctk.CTkLabel(
            content, text=f"{APP_VERSION} \u00b7 S. Strasser", font=self.footer_font, text_color=FOOTER_COLOR
        ).pack(pady=(10, 0))

    def calculate_dilution(self) -> None:
        """Validate inputs, run the dilution calculation, show results, and save to history."""
        drug_name = self.drug_name_var.get().strip()
        if not drug_name:
            messagebox.showwarning("Missing Input", "Please enter a drug name")
            return

        for label, var in (
            ("Stock Concentration", self.stock_conc_var),
            ("Target Concentration", self.target_conc_var),
            ("Target Volume", self.target_vol_var),
        ):
            is_valid, _, error_msg = validate_decimal_input(var.get().strip())
            if not is_valid:
                messagebox.showerror("Input Error", f"{label}: {error_msg}")
                return

        stock_conc = float(self.stock_conc_var.get())
        target_conc = float(self.target_conc_var.get())
        target_vol = float(self.target_vol_var.get())
        stock_conc_unit = self.stock_conc_unit_var.get()
        target_conc_unit = self.target_conc_unit_var.get()
        vol_unit = self.vol_unit_var.get()
        solvent = self.solvent_var.get().strip()

        if target_conc <= 0:
            messagebox.showerror("Input Error", "Target concentration must be positive")
            return

        is_valid, error_msg = validate_inputs(concentration=stock_conc, volume=target_vol)
        if not is_valid:
            messagebox.showerror("Input Error", error_msg)
            return

        conversion_factors = {
            ("M", "M"): 1, ("M", "mM"): 1000, ("M", "\u00b5M"): 1000000, ("M", "nM"): 1000000000,
            ("mM", "M"): 0.001, ("mM", "mM"): 1, ("mM", "\u00b5M"): 1000, ("mM", "nM"): 1000000,
            ("\u00b5M", "M"): 0.000001, ("\u00b5M", "mM"): 0.001, ("\u00b5M", "\u00b5M"): 1, ("\u00b5M", "nM"): 1000,
            ("nM", "M"): 0.000000001, ("nM", "mM"): 0.000001, ("nM", "\u00b5M"): 0.001, ("nM", "nM"): 1,
        }
        conversion_key = (stock_conc_unit, target_conc_unit)
        if conversion_key not in conversion_factors:
            messagebox.showerror("Unit Error", "Unsupported unit combination")
            return
        target_conc_in_stock_units = target_conc / conversion_factors[conversion_key]

        result = calculate_dilution(stock_conc, target_conc_in_stock_units, target_vol, stock_conc_unit, vol_unit)
        if result.get("error"):
            messagebox.showerror("Calculation Error", result.get("message"))
            return

        stock_vol, stock_vol_unit = convert_to_readable_unit(result["stock_volume"], vol_unit)
        solvent_vol, solvent_vol_unit = convert_to_readable_unit(result["solvent_volume"], vol_unit)

        content = (
            f"WORKING SOLUTION\n\n"
            f"Drug:                {drug_name}\n"
            f"From Stock:          {format_number(stock_conc)} {stock_conc_unit}\n"
            f"Target:              {format_number(target_conc)} {target_conc_unit} in {format_number(target_vol)} {vol_unit}\n"
            f"Dilution Factor:     {format_number(result['dilution_factor'])}x\n"
            f"Solvent:             {solvent or 'Not specified'}\n\n"
            f"TAKE:  {format_result_with_unit(stock_vol, stock_vol_unit)} of stock\n"
            f"ADD:   {format_result_with_unit(solvent_vol, solvent_vol_unit)} of {solvent or 'solvent'}\n"
        )
        self.show_results_window("Working Solution Preparation", drug_name, content)

        self.history.add_calculation(
            calculation_type="Working from Stock",
            drug_name=drug_name,
            inputs={
                "stock_concentration": stock_conc, "target_concentration": target_conc,
                "target_volume": target_vol, "stock_concentration_unit": stock_conc_unit,
                "target_concentration_unit": target_conc_unit, "volume_unit": vol_unit,
            },
            results=result,
            solvent=solvent,
        )
        self._calculation_count = self.history.get_calculation_count()

    # ------------------------------------------------------------------
    # Placeholder for the last migration increment
    # ------------------------------------------------------------------
    def show_history(self) -> None:
        """Placeholder - migrated in increment 4."""
        self._show_placeholder("Calculation History")

    def _show_placeholder(self, screen_name: str) -> None:
        """
        Show a placeholder screen for not-yet-migrated screens.

        Parameters
        ----------
        screen_name : str
            Name of the screen to display.
        """
        self.clear_frame()
        self.current_mode = None

        ctk.CTkLabel(
            self.main_frame,
            text=f"{screen_name}\n\n(coming in the next migration step)",
            font=self.placeholder_font,
            text_color=MUTED,
            justify="center",
        ).pack(pady=(100, 20))

        ctk.CTkButton(
            self.main_frame,
            text="Back to Menu",
            command=self.show_welcome_screen,
            width=140,
            fg_color=ROW,
            hover_color=ROW_HOVER,
            text_color=TEXT,
            font=self.button_font,
        ).pack()

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------
    def show_about_dialog(self) -> None:
        """Open the About dialog window."""
        AboutDialog(self.root)


def main() -> None:
    """Launch the Drug Dosage Calculator application (CTk version)."""
    root = ctk.CTk()
    DrugCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
