"""
Drug Dosage Calculator - Main GUI Application (CustomTkinter migration).

Version: v3.1.0.

"""

import sys
import ctypes
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk, StringVar, filedialog
from typing import Optional
from datetime import datetime

import customtkinter as ctk
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui_integration_ctk import AboutDialog, MolecularWeightLookupWidget  # noqa: E402
from calculators import calculate_stock_from_powder, calculate_dilution, validate_inputs  # noqa: E402
from data_storage import CalculationHistory, UserPreferences  # noqa: E402
from formatters import (  # noqa: E402
    format_number, validate_decimal_input, format_result_with_unit, convert_to_readable_unit,
)
from font_manager import FontManager  # noqa: E402
from pdf_export import PDFExporter  # noqa: E402

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
SUCCESS = "#6FCF6F"

APP_VERSION = "v3.1.0"
COLUMN_WIDTH = 640

HISTORY_COLUMN_LABELS = {
    "#": "#", "Date": "Date", "Drug": "Drug Name", "Type": "Type",
    "Value": "Concentration & Volume", "Solvent": "Solvent",
}


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
    font_manager : FontManager
        Font manager for scaled tooltip font.
    """

    def __init__(self, widget, text: str, font_manager) -> None:
        self.widget = widget
        self.text = text
        self.font_manager = font_manager
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
        tooltip_font = self.font_manager.get_font('tooltip')
        tk.Label(
            self.tip, text=self.text, bg=CARD, fg=TEXT, font=(tooltip_font.cget("family"), tooltip_font.cget("size")),
            relief="solid", borderwidth=1, highlightbackground=BORDER, padx=6, pady=3,
        ).pack()

    def hide(self, _event=None) -> None:
        """Destroy the tooltip."""
        if self.tip:
            self.tip.destroy()
            self.tip = None


def apply_dark_titlebar(window) -> None:
    """
    Force an immersive dark Windows title bar on a Tk/CTk window.

    Parameters
    ----------
    window : tkinter.Tk, tkinter.Toplevel, or customtkinter equivalent
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
        self.root.geometry("880x640")
        self.root.minsize(560, 540)
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
        apply_dark_titlebar(self.root)
        center_window(self.root)

        self.current_mode: Optional[str] = None
        self.history = CalculationHistory()
        self.preferences = UserPreferences()
        self.pdf_exporter = PDFExporter()

        self.font_manager = FontManager(self.preferences.get_font_scale())
        self._setup_fonts()

        self.main_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        self.show_welcome_screen()

    def _setup_fonts(self) -> None:
        """Initialize all font objects using FontManager."""
        fm = self.font_manager
        self.h1_font = fm.get_font('h1', weight='bold')
        self.about_font = fm.get_font('about')
        self.row_title_font = fm.get_font('row_title', weight='bold')
        self.row_subtitle_font = fm.get_font('small', family='Consolas')
        self.history_title_font = fm.get_font('history_title', weight='bold')
        self.inset_font = fm.get_font('body')
        self.footer_font = fm.get_font('small', family='Consolas')
        self.button_font = fm.get_font('button', weight='bold')
        self.form_label_font = fm.get_font('body')
        self.form_entry_font = fm.get_font('body')
        self.form_title_font = fm.get_font('form_title', weight='bold')
        self.form_subtitle_font = fm.get_font('body')

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

    def _on_font_scale_change(self, value) -> None:
        """Handle font scale slider changes, saving the preference and updating UI."""
        new_scale = float(value)
        self.preferences.set_font_scale(new_scale)
        self.font_manager.set_user_scale(new_scale)
        self._setup_fonts()

        # Update percentage label
        if hasattr(self, 'font_scale_label'):
            self.font_scale_label.configure(text=f"{int(new_scale * 100)}%")

        current_screen = self.current_mode
        if current_screen == "stock":
            self.show_stock_calculator()
        elif current_screen == "dilution":
            self.show_dilution_calculator()
        elif current_screen == "history":
            self.show_history_screen()
        else:
            self.show_welcome_screen()

    # ------------------------------------------------------------------
    # Welcome screen
    # ------------------------------------------------------------------
    def show_welcome_screen(self) -> None:
        """Display the welcome screen: About link, H1, hero, calculator rows, history card."""
        self.clear_frame()
        self.current_mode = None

        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(anchor="w", fill="x", padx=16, pady=(10, 0))

        ctk.CTkButton(
            top_bar,
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
        ).pack(side="left")

        ctk.CTkLabel(
            top_bar,
            text="Font size:",
            text_color=MUTED,
            font=self.about_font,
        ).pack(side="left", padx=(20, 8))

        self.font_scale_var = tk.DoubleVar(value=self.preferences.get_font_scale())
        ctk.CTkSlider(
            top_bar,
            from_=1.0,
            to=1.5,
            number_of_steps=5,
            variable=self.font_scale_var,
            command=self._on_font_scale_change,
            width=120,
            height=16,
            fg_color=ROW,
            progress_color=ACCENT,
            button_color=ACCENT,
            button_hover_color="#4A9FD6",
        ).pack(side="left", padx=(0, 8))

        self.font_scale_label = ctk.CTkLabel(
            top_bar,
            text=f"{int(self.font_scale_var.get() * 100)}%",
            text_color=MUTED,
            font=self.about_font,
            width=45,
        )
        self.font_scale_label.pack(side="left")

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(expand=True)

        ctk.CTkLabel(
            content,
            text="Drug Concentration Calculator",
            font=self.h1_font,
            text_color=TEXT,
        ).pack(pady=(6, 0))

        hero_img = Image.open(_asset_path("pill3.png"))
        hero = ctk.CTkImage(light_image=hero_img, dark_image=hero_img, size=(84, 84))
        self._icon_refs.append(hero)
        ctk.CTkLabel(content, image=hero, text="").pack(pady=(12, 20))

        col = ctk.CTkFrame(content, fg_color="transparent", width=COLUMN_WIDTH)
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
            content,
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
            text=f"Total calculations saved: {self.history.get_calculation_count()}",
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
        MolecularWeightLookupWidget(form, self.drug_name_var, self.mw_var, self.font_manager, row=1, column_start=2)

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
            CTkToolTip(info_icon, tooltip, self.font_manager)

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

        calc_data = {
            'type': "Stock from Powder",
            'inputs': {
                "molecular_weight": mw, "target_concentration": conc, "target_volume": vol,
                "concentration_unit": conc_unit, "volume_unit": vol_unit,
            },
            'results': result,
            'solvent': solvent,
        }

        self.show_results_window("Stock Solution Preparation", drug_name, content, calc_data)

        self.history.add_calculation(
            calculation_type="Stock from Powder",
            drug_name=drug_name,
            inputs=calc_data['inputs'],
            results=result,
            solvent=solvent,
        )

    def clear_inputs(self) -> None:
        """Clear the input fields for the current calculator screen."""
        if self.current_mode == "stock":
            for var in (self.drug_name_var, self.mw_var, self.conc_var, self.vol_var, self.solvent_var):
                var.set("")
        elif self.current_mode == "dilution":
            for var in (self.drug_name_var, self.stock_conc_var, self.target_conc_var, self.target_vol_var, self.solvent_var):
                var.set("")

    def show_results_window(self, title: str, drug_name: str, content: str, calc_data: dict = None) -> None:
        """
        Show calculation results in a professional popup window with export options.

        Parameters
        ----------
        title : str
            Popup title.
        drug_name : str
            Drug name, appended to the window title.
        content : str
            Formatted result text.
        calc_data : dict, optional
            Calculation data for PDF export (type, inputs, results, solvent).
        """
        win = ctk.CTkToplevel(self.root)
        win.title(f"{title} - {drug_name}")
        win.geometry("650x550")
        win.configure(fg_color=BG)
        win.transient(self.root)

        try:
            icon_path = _asset_path("icon.ico")
            if icon_path.exists():
                win.iconbitmap(str(icon_path))
        except Exception:
            pass
        apply_dark_titlebar(win)

        # Header with icon
        header = ctk.CTkFrame(win, fg_color=CARD, height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        icon_name = "tube" if "Stock" in title else "pipette"
        icon_img = self._load_icon(icon_name, 32)
        ctk.CTkLabel(header, image=icon_img, text="").pack(side="left", padx=(20, 10), pady=14)

        header_text = ctk.CTkFrame(header, fg_color="transparent")
        header_text.pack(side="left", fill="both", expand=True, pady=14)
        ctk.CTkLabel(
            header_text, text=title, font=self.form_title_font, text_color=TEXT, anchor="w"
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_text, text=drug_name, font=self.form_subtitle_font, text_color=ACCENT, anchor="w"
        ).pack(anchor="w")

        # Content area with better formatting
        content_frame = ctk.CTkFrame(win, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        text = ctk.CTkTextbox(
            content_frame,
            fg_color=ROW,
            text_color=TEXT,
            font=self.font_manager.get_font('monospace', family='Consolas'),
            wrap="word",
            border_width=1,
            border_color=BORDER,
        )
        text.pack(fill="both", expand=True)
        text.insert("1.0", content)
        text.configure(state="disabled")

        def copy_to_clipboard() -> None:
            win.clipboard_clear()
            win.clipboard_append(content)
            self._show_toast(win, "Protocol copied to clipboard!", SUCCESS)

        def export_to_pdf() -> None:
            if not calc_data:
                messagebox.showerror("Export Error", "No calculation data available for export")
                return

            try:
                # Generate default filename
                date_str = datetime.now().strftime("%Y-%m-%d")
                safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in drug_name)
                default_filename = f"{date_str}_{safe_name}_{calc_data['type'].replace(' ', '_')}.pdf"

                # Show save file dialog
                filepath = filedialog.asksaveasfilename(
                    parent=win,
                    title="Save PDF Protocol",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=default_filename,
                )

                if not filepath:  # User cancelled
                    return

                # Export PDF
                filepath = Path(filepath)
                self.pdf_exporter.export_calculation(
                    calculation_type=calc_data['type'],
                    drug_name=drug_name,
                    inputs=calc_data['inputs'],
                    results=calc_data['results'],
                    solvent=calc_data.get('solvent', ''),
                    filepath=filepath,
                )

                # Auto-open PDF
                self.pdf_exporter.open_pdf(filepath)

                self._show_toast(win, f"PDF saved and opened:\n{filepath.name}", SUCCESS, width=400)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export PDF:\n{str(e)}")

        # Button bar with professional styling
        btn_bar = ctk.CTkFrame(win, fg_color=CARD, height=70)
        btn_bar.pack(fill="x", padx=0, pady=0)
        btn_bar.pack_propagate(False)

        btn_frame = ctk.CTkFrame(btn_bar, fg_color="transparent")
        btn_frame.pack(expand=True)

        ctk.CTkButton(
            btn_frame,
            text="Export to PDF",
            command=export_to_pdf,
            fg_color=ACCENT,
            hover_color="#4A9FD6",
            text_color="#0F1C24",
            font=self.button_font,
            width=140,
            height=36,
        ).grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            btn_frame,
            text="Copy to Clipboard",
            command=copy_to_clipboard,
            fg_color=ROW,
            hover_color=ROW_HOVER,
            text_color=TEXT,
            font=self.button_font,
            width=150,
            height=36,
        ).grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            btn_frame,
            text="Close",
            command=win.destroy,
            fg_color=ROW,
            hover_color=ROW_HOVER,
            text_color=MUTED,
            font=self.button_font,
            width=100,
            height=36,
        ).grid(row=0, column=2, padx=6)

        win.update_idletasks()
        center_window(win, self.root)

    def _show_toast(self, parent, message: str, color: str, width: int = 350) -> None:
        """Show a brief toast notification."""
        toast = ctk.CTkToplevel(parent)
        toast.title("")
        toast.configure(fg_color=BG)
        toast.transient(parent)
        toast.overrideredirect(True)

        frame = ctk.CTkFrame(toast, fg_color=CARD, border_width=2, border_color=color, corner_radius=8)
        frame.pack(padx=2, pady=2)

        ctk.CTkLabel(
            frame,
            text=message,
            font=self.font_manager.get_font('body'),
            text_color=color,
            wraplength=width-40,
        ).pack(padx=20, pady=15)

        toast.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (toast.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (toast.winfo_height() // 2)
        toast.geometry(f"+{x}+{y}")

        toast.after(2500, toast.destroy)

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

        calc_data = {
            'type': "Working from Stock",
            'inputs': {
                "stock_concentration": stock_conc, "target_concentration": target_conc,
                "target_volume": target_vol, "stock_concentration_unit": stock_conc_unit,
                "target_concentration_unit": target_conc_unit, "volume_unit": vol_unit,
            },
            'results': result,
            'solvent': solvent,
        }

        self.show_results_window("Working Solution Preparation", drug_name, content, calc_data)

        self.history.add_calculation(
            calculation_type="Working from Stock",
            drug_name=drug_name,
            inputs=calc_data['inputs'],
            results=result,
            solvent=solvent,
        )

    # ------------------------------------------------------------------
    # Calculation History
    # ------------------------------------------------------------------
    def _configure_treeview_style(self) -> None:
        """Configure a dark ttk style for the history Treeview and scrollbar."""
        style = ttk.Style()
        style.theme_use("clam")

        # CTkFont sizes are auto-scaled by CustomTkinter to match the
        # display's DPI scaling; a plain ttk.Style font is not. Without
        # this, "11" on a CTkLabel and "11" here render at visibly
        # different physical sizes on a scaled display.
        try:
            scale = ctk.ScalingTracker.get_widget_scaling(self.root)
        except Exception:
            scale = 1.0
        base_size = self.font_manager.get_size('history_table')
        row_font_size = round(base_size * scale)
        heading_font_size = round(base_size * scale)
        row_height = round(34 * scale)

        style.configure(
            "Dark.Treeview", background=ROW, fieldbackground=ROW, foreground=TEXT,
            borderwidth=0, rowheight=row_height, font=("Segoe UI", row_font_size),
        )
        style.map("Dark.Treeview", background=[("selected", ACCENT)], foreground=[("selected", BG)])
        style.configure(
            "Dark.Treeview.Heading", background=CARD, foreground=MUTED,
            borderwidth=0, font=("Segoe UI", heading_font_size, "bold"),
        )
        style.map("Dark.Treeview.Heading", background=[("active", CARD)])

        style.configure(
            "Dark.Vertical.TScrollbar", background=ROW, troughcolor=CARD,
            bordercolor=BORDER, arrowcolor=MUTED,
        )

    def show_history(self) -> None:
        """Display the Calculation History screen with search, filter, and sort."""
        self.clear_frame()
        self.current_mode = "history"
        self._configure_treeview_style()

        ctk.CTkLabel(
            self.main_frame, text="Calculation History", font=self.form_title_font, text_color=TEXT
        ).pack(pady=(16, 10))

        controls = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        controls.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(controls, text="Search:", font=self.form_label_font, text_color=MUTED).grid(
            row=0, column=0, padx=(0, 6)
        )
        self.search_var = StringVar()
        self.search_var.trace_add("write", lambda *_a: self.update_history_display())
        ctk.CTkEntry(
            controls, textvariable=self.search_var, width=200, fg_color=ROW, border_color=BORDER,
            text_color=TEXT, font=self.form_entry_font,
        ).grid(row=0, column=1, padx=(0, 20))

        ctk.CTkLabel(controls, text="Show:", font=self.form_label_font, text_color=MUTED).grid(
            row=0, column=2, padx=(0, 6)
        )
        self.filter_var = StringVar(value="All")
        ctk.CTkComboBox(
            controls, variable=self.filter_var, values=["All", "Stock Solutions", "Working Solutions"],
            width=170, fg_color=ROW, border_color=BORDER, button_color=ROW, text_color=TEXT,
            dropdown_fg_color=ROW, font=self.form_entry_font,
            command=lambda _v: self.update_history_display(),
        ).grid(row=0, column=3, padx=(0, 20))

        ctk.CTkLabel(controls, text="Sort by:", font=self.form_label_font, text_color=MUTED).grid(
            row=0, column=4, padx=(0, 6)
        )
        self.sort_var = StringVar(value="Date (newest first)")
        ctk.CTkComboBox(
            controls, variable=self.sort_var,
            values=["Date (newest first)", "Date (oldest first)", "Drug name (A-Z)", "Drug name (Z-A)"],
            width=190, fg_color=ROW, border_color=BORDER, button_color=ROW, text_color=TEXT,
            dropdown_fg_color=ROW, font=self.form_entry_font,
            command=lambda _v: self._on_sort_dropdown_changed(),
        ).grid(row=0, column=5)

        tree_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        tree_scroll = ttk.Scrollbar(tree_frame, style="Dark.Vertical.TScrollbar")
        tree_scroll.pack(side="right", fill="y")

        columns = ("#", "Date", "Drug", "Type", "Value", "Solvent")
        self.history_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set,
            selectmode="extended", style="Dark.Treeview",
        )
        tree_scroll.config(command=self.history_tree.yview)

        headings = {
            "#": ("#", 40, "center"), "Date": ("Date", 100, "w"), "Drug": ("Drug Name", 150, "w"),
            "Type": ("Type", 80, "center"), "Value": ("Concentration & Volume", 220, "w"),
            "Solvent": ("Solvent", 100, "w"),
        }
        self._header_sort_col: Optional[str] = None
        self._header_sort_reverse = False
        for col, (text, width, anchor) in headings.items():
            self.history_tree.heading(col, text=text, command=lambda c=col: self._on_header_click(c))
            self.history_tree.column(col, width=width, anchor=anchor)

        self.history_tree.tag_configure("evenrow", background=CARD)
        self.history_tree.tag_configure("oddrow", background=ROW)
        self.history_tree.pack(fill="both", expand=True)
        self.history_tree.bind("<Double-1>", self.show_calculation_details)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(
            btn_frame, text="View Details", command=lambda: self.show_calculation_details(None),
            fg_color=ACCENT, hover_color="#4A9FD6", text_color="#0F1C24", font=self.button_font, width=120,
        ).grid(row=0, column=0, padx=6)
        ctk.CTkButton(
            btn_frame, text="Export Selected", command=self.export_selected_to_pdf,
            fg_color=ACCENT, hover_color="#4A9FD6", text_color="#0F1C24", font=self.button_font, width=140,
        ).grid(row=0, column=1, padx=6)
        ctk.CTkButton(
            btn_frame, text="Clear History", command=self.clear_history,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT, font=self.button_font, width=120,
        ).grid(row=0, column=2, padx=6)
        ctk.CTkButton(
            btn_frame, text="Back to Menu", command=self.show_welcome_screen,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT, font=self.button_font, width=120,
        ).grid(row=0, column=3, padx=6)

        ctk.CTkLabel(
            self.main_frame, text=f"{APP_VERSION} \u00b7 S. Strasser", font=self.footer_font, text_color=FOOTER_COLOR
        ).pack(pady=(0, 10))

        self.update_history_display()

    def _format_value_column(self, calc: dict) -> str:
        """
        Build the "Concentration & Volume" display string for one calculation.

        Parameters
        ----------
        calc : dict
            A calculation record.

        Returns
        -------
        str
        """
        inputs = calc["inputs"]
        if calc["calculation_type"] == "Stock from Powder":
            conc = format_number(inputs.get("target_concentration", 0))
            vol = format_number(inputs.get("target_volume", 0))
            conc_unit = inputs.get("concentration_unit", "?")
            vol_unit = inputs.get("volume_unit", "?")
            return f"{conc} {conc_unit} in {vol} {vol_unit}"
        target_conc = format_number(inputs.get("target_concentration", 0))
        target_vol = format_number(inputs.get("target_volume", 0))
        target_unit = inputs.get("target_concentration_unit", inputs.get("concentration_unit", "?"))
        vol_unit = inputs.get("volume_unit", "?")
        return f"{target_conc} {target_unit} in {target_vol} {vol_unit}"

    def _get_sorted_filtered_calculations(self) -> list:
        """
        Apply the current search, filter, and sort settings to the history.

        A column header click (``self._header_sort_col``) takes priority
        over the "Sort by" dropdown; picking from the dropdown clears it.

        Returns
        -------
        list of dict
            Calculations after filtering and sorting.
        """
        calculations = self.history.get_all_calculations()

        search_term = self.search_var.get().lower()
        if search_term:
            calculations = [
                c for c in calculations
                if search_term in c["drug_name"].lower() or search_term in c.get("solvent", "").lower()
            ]

        filter_type = self.filter_var.get()
        if filter_type == "Stock Solutions":
            calculations = [c for c in calculations if c["calculation_type"] == "Stock from Powder"]
        elif filter_type == "Working Solutions":
            calculations = [c for c in calculations if c["calculation_type"] == "Working from Stock"]

        self.current_calculations = calculations
        sorted_calcs = calculations.copy()

        if self._header_sort_col:
            column_keys = {
                "Date": lambda c: c["timestamp"],
                "Drug": lambda c: c["drug_name"].lower(),
                "Type": lambda c: c["calculation_type"],
                "Solvent": lambda c: c.get("solvent", "").lower(),
                "Value": lambda c: self._format_value_column(c).lower(),
            }
            key = column_keys.get(self._header_sort_col, lambda c: c["timestamp"])
            sorted_calcs.sort(key=key, reverse=self._header_sort_reverse)
            return sorted_calcs

        sort_by = self.sort_var.get()
        if sort_by == "Date (newest first)":
            sorted_calcs.sort(key=lambda x: x["timestamp"], reverse=True)
        elif sort_by == "Date (oldest first)":
            sorted_calcs.sort(key=lambda x: x["timestamp"])
        elif sort_by == "Drug name (A-Z)":
            sorted_calcs.sort(key=lambda x: x["drug_name"].lower())
        elif sort_by == "Drug name (Z-A)":
            sorted_calcs.sort(key=lambda x: x["drug_name"].lower(), reverse=True)
        return sorted_calcs

    def _on_sort_dropdown_changed(self) -> None:
        """Reset any column header sort and apply the "Sort by" dropdown instead."""
        self._header_sort_col = None
        for c, label in HISTORY_COLUMN_LABELS.items():
            self.history_tree.heading(c, text=label)
        self.update_history_display()

    def _on_header_click(self, col: str) -> None:
        """
        Sort the history by the clicked column, toggling direction on repeat clicks.

        Parameters
        ----------
        col : str
            Column id that was clicked.
        """
        if self._header_sort_col == col:
            self._header_sort_reverse = not self._header_sort_reverse
        else:
            self._header_sort_col = col
            self._header_sort_reverse = False

        arrow = " \u25bc" if self._header_sort_reverse else " \u25b2"
        for c, label in HISTORY_COLUMN_LABELS.items():
            self.history_tree.heading(c, text=label + (arrow if c == col else ""))

        self.update_history_display()

    def update_history_display(self) -> None:
        """Refresh the Treeview based on the current search, filter, and sort settings."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for i, calc in enumerate(self._get_sorted_filtered_calculations(), 1):
            date = calc["timestamp"].split("T")[0]
            calc_type = "Stock" if calc["calculation_type"] == "Stock from Powder" else "Working"
            solvent = calc.get("solvent", "N/A")
            value = self._format_value_column(calc)

            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.history_tree.insert(
                "", "end", values=(i, date, calc["drug_name"], calc_type, value, solvent), tags=(tag,)
            )

    def show_calculation_details(self, _event) -> None:
        """Show the selected calculation's full details in a popup."""
        selection = self.history_tree.selection()
        if not selection:
            return

        display_num = int(self.history_tree.item(selection[0])["values"][0])
        calc = self._get_sorted_filtered_calculations()[display_num - 1]

        timestamp = calc["timestamp"].split("T")[0]
        drug_name = calc["drug_name"]
        solvent = calc.get("solvent", "Not specified")
        inputs = calc["inputs"]
        results = calc["results"]

        header = f"#{display_num} \u00b7 {timestamp} \u00b7 {drug_name}\n\n"

        if calc["calculation_type"] == "Stock from Powder":
            content = header + (
                f"STOCK SOLUTION\n\n"
                f"Drug:                {drug_name}\n"
                f"Molecular Weight:    {format_number(inputs.get('molecular_weight', 0))} g/mol\n"
                f"Target:              {format_number(inputs.get('target_concentration', 0))} "
                f"{inputs.get('concentration_unit', '?')} in {format_number(inputs.get('target_volume', 0))} "
                f"{inputs.get('volume_unit', '?')}\n"
                f"Solvent:             {solvent}\n\n"
                f"WEIGH:  {format_result_with_unit(results.get('mass_mg', 0), 'mg')}\n"
                f"DISSOLVE IN:  {format_number(inputs.get('target_volume', 0))} "
                f"{inputs.get('volume_unit', '?')} of {solvent}\n"
            )
        else:
            vol_unit = inputs.get("volume_unit", "?")
            stock_vol, stock_vol_unit = convert_to_readable_unit(results.get("stock_volume", 0), vol_unit)
            solvent_vol, solvent_vol_unit = convert_to_readable_unit(results.get("solvent_volume", 0), vol_unit)
            stock_unit = inputs.get("stock_concentration_unit", inputs.get("concentration_unit", "?"))
            target_unit = inputs.get("target_concentration_unit", inputs.get("concentration_unit", "?"))
            content = header + (
                f"WORKING SOLUTION\n\n"
                f"Drug:                {drug_name}\n"
                f"From Stock:          {format_number(inputs.get('stock_concentration', 0))} {stock_unit}\n"
                f"Target:              {format_number(inputs.get('target_concentration', 0))} {target_unit} in "
                f"{format_number(inputs.get('target_volume', 0))} {vol_unit}\n"
                f"Dilution Factor:     {format_number(results.get('dilution_factor', 0))}x\n"
                f"Solvent:             {solvent}\n\n"
                f"TAKE:  {format_result_with_unit(stock_vol, stock_vol_unit)} of stock\n"
                f"ADD:   {format_result_with_unit(solvent_vol, solvent_vol_unit)} of {solvent}\n"
            )

        calc_data = {
            'type': calc["calculation_type"],
            'inputs': inputs,
            'results': results,
            'solvent': solvent,
        }

        self.show_results_window(f"Calculation #{display_num}", drug_name, content, calc_data)

    def _confirm_dialog(self, title: str, message: str) -> bool:
        """
        Show a dark-styled Yes/No confirmation window and block until answered.

        Parameters
        ----------
        title : str
            Window title.
        message : str
            Question to display.

        Returns
        -------
        bool
            True if the user confirmed, False otherwise.
        """
        win = ctk.CTkToplevel(self.root)
        win.title(title)
        win.geometry("380x160")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.transient(self.root)
        win.grab_set()

        try:
            icon_path = _asset_path("icon.ico")
            if icon_path.exists():
                win.iconbitmap(str(icon_path))
        except Exception:
            pass
        apply_dark_titlebar(win)

        result = {"confirmed": False}

        ctk.CTkLabel(
            win, text=message, font=self.form_label_font, text_color=TEXT, wraplength=320, justify="center"
        ).pack(expand=True, padx=20, pady=(20, 10))

        def on_yes() -> None:
            result["confirmed"] = True
            win.destroy()

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        ctk.CTkButton(
            btn_frame, text="Yes", command=on_yes,
            fg_color=ACCENT, hover_color="#4A9FD6", text_color="#0F1C24", font=self.button_font, width=90,
        ).grid(row=0, column=0, padx=6)
        ctk.CTkButton(
            btn_frame, text="Cancel", command=win.destroy,
            fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT, font=self.button_font, width=90,
        ).grid(row=0, column=1, padx=6)

        center_window(win, self.root)

        win.wait_window()
        return result["confirmed"]

    def export_selected_to_pdf(self) -> None:
        """Export selected calculations to a single PDF."""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select one or more calculations to export.\n\nTip: Hold Ctrl to select multiple, or Shift to select a range.")
            return

        try:
            # Get selected calculations
            selected_calcs = []
            for item in selection:
                display_num = int(self.history_tree.item(item)["values"][0])
                calc = self._get_sorted_filtered_calculations()[display_num - 1]
                selected_calcs.append(calc)

            # Generate default filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            if len(selected_calcs) == 1:
                safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in selected_calcs[0]["drug_name"])
                default_filename = f"{date_str}_{safe_name}_{selected_calcs[0]['calculation_type'].replace(' ', '_')}.pdf"
            else:
                default_filename = f"{date_str}_Multiple_Calculations_{len(selected_calcs)}_protocols.pdf"

            # Show save file dialog
            filepath = filedialog.asksaveasfilename(
                parent=self.root,
                title="Save PDF Protocol",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=default_filename,
            )

            if not filepath:  # User cancelled
                return

            # Export PDF
            filepath = Path(filepath)
            self.pdf_exporter.export_multiple_calculations(selected_calcs, filepath)

            # Auto-open PDF
            self.pdf_exporter.open_pdf(filepath)

            count_text = "calculation" if len(selected_calcs) == 1 else f"{len(selected_calcs)} calculations"
            messagebox.showinfo(
                "PDF Exported",
                f"Successfully exported {count_text} to:\n{filepath.name}\n\nThe PDF has been opened."
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF:\n{str(e)}")

    def clear_history(self) -> None:
        """Delete all calculation history, after confirmation."""
        if self._confirm_dialog("Confirm Clear", "Are you sure you want to delete all calculation history?"):
            self.history.clear_history()
            self.update_history_display()
            messagebox.showinfo("History Cleared", "All calculations have been deleted")

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------
    def show_about_dialog(self) -> None:
        """Open the About dialog window."""
        AboutDialog(self.root, self.font_manager)


def main() -> None:
    """Launch the Drug Dosage Calculator application (CTk version)."""
    root = ctk.CTk()
    DrugCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
