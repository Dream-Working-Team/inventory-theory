"""
Configuración visual y tema para la interfaz gráfica (CustomTkinter / Tkinter).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import customtkinter as ctk

# Configuración global de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Theme:
    """Paleta de colores y estilos tipográficos modernos."""
    
    # Fondos
    BG_DARK = "#12141C"
    BG_CARD = "#1A1D27"
    BG_SIDEBAR = "#151822"
    BG_INPUT = "#222736"
    BG_INPUT_HOVER = "#2A3042"
    
    # Bordes y Divisores
    BORDER_COLOR = "#2D3448"
    BORDER_LIGHT = "#3E4760"
    
    # Acentos y Acciones
    PRIMARY = "#3A86FF"
    PRIMARY_HOVER = "#2563EB"
    SECONDARY = "#00F5D4"
    ACCENT_YELLOW = "#FFBE0B"
    ACCENT_CORAL = "#FF758F"
    ACCENT_PURPLE = "#9D4EDD"
    SUCCESS = "#38B000"
    WARNING = "#FF9F1C"
    ERROR = "#EF233C"
    
    # Tipografía
    TEXT_MAIN = "#F1F5F9"
    TEXT_MUTED = "#94A3B8"
    TEXT_SUBTLE = "#64748B"
    
    # Fuentes (Familias y Tamaños)
    FONT_FAMILY = "Segoe UI"
    FONT_CODE = "Consolas"
    
    @classmethod
    def font_title(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=20, weight="bold")
    
    @classmethod
    def font_subtitle(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=15, weight="bold")
        
    @classmethod
    def font_section(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="bold")
        
    @classmethod
    def font_body(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12)
        
    @classmethod
    def font_body_bold(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12, weight="bold")
        
    @classmethod
    def font_small(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=10)
        
    @classmethod
    def font_code(cls):
        return ctk.CTkFont(family=cls.FONT_CODE, size=11)
        
    @classmethod
    def font_metric(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=18, weight="bold")
