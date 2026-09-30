"""
Font Manager for centralized font scaling and accessibility.

Provides a single source of truth for all font sizes in the application,
with support for user-controlled scaling while preserving the calculation
history table at its base size.
"""

import customtkinter as ctk
from typing import Dict, Literal


class FontManager:
    """
    Centralized font management with user-configurable scaling.

    Parameters
    ----------
    user_scale : float, default=1.0
        User preference scale factor (1.0 = default, 1.15 = larger fonts).
    """

    BASE_SIZES: Dict[str, int] = {
        'h1': 36,
        'form_title': 24,
        'row_title': 18,
        'history_title': 17,
        'tooltip': 16,
        'button': 16,
        'about': 15,
        'body': 14,
        'small': 12,
        'monospace': 14,
        'history_table': 11,
    }

    def __init__(self, user_scale: float = 1.0) -> None:
        self.user_scale = user_scale
        self._fonts: Dict[str, ctk.CTkFont] = {}

    def _get_scaled_size(self, base_name: str) -> int:
        """
        Get the scaled font size for a given base name.

        Parameters
        ----------
        base_name : str
            Font name from BASE_SIZES.

        Returns
        -------
        int
            Scaled font size (history_table is never scaled by user preference).
        """
        base_size = self.BASE_SIZES[base_name]
        if base_name == 'history_table':
            return base_size
        return round(base_size * self.user_scale)

    def get_font(
        self,
        name: str,
        family: str = "Segoe UI",
        weight: Literal["normal", "bold"] = "normal"
    ) -> ctk.CTkFont:
        """
        Get a CTkFont object with the specified parameters.

        Parameters
        ----------
        name : str
            Font size name from BASE_SIZES.
        family : str, default="Segoe UI"
            Font family.
        weight : "normal" or "bold", default="normal"
            Font weight.

        Returns
        -------
        ctk.CTkFont
        """
        size = self._get_scaled_size(name)
        cache_key = f"{name}_{family}_{weight}_{self.user_scale}"

        if cache_key not in self._fonts:
            self._fonts[cache_key] = ctk.CTkFont(family=family, size=size, weight=weight)

        return self._fonts[cache_key]

    def get_size(self, name: str) -> int:
        """
        Get the scaled size for a font name (for use with ttk or plain tuples).

        Parameters
        ----------
        name : str
            Font size name from BASE_SIZES.

        Returns
        -------
        int
            Scaled font size.
        """
        return self._get_scaled_size(name)

    def set_user_scale(self, scale: float) -> None:
        """
        Update the user scale factor and clear the font cache.

        Parameters
        ----------
        scale : float
            New user scale factor.
        """
        self.user_scale = scale
        self._fonts.clear()
