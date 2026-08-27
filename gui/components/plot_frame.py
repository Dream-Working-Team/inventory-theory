"""
Componente reutilizable para embeber gráficos de Matplotlib en la interfaz CustomTkinter.
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import customtkinter as ctk
import matplotlib.figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from ..theme import Theme


class PlotFrame(ctk.CTkFrame):
    """
    Contenedor POO para figuras de Matplotlib con toolbar de navegación opcional
    y redimensionamiento automático.
    """

    def __init__(self, master, figsize=(10, 4.5), dpi=100, **kwargs):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR, **kwargs)
        
        self.canvas: FigureCanvasTkAgg = None
        self.toolbar = None
        self.fig: matplotlib.figure.Figure = None
        
        # Etiqueta de placeholder inicial
        self.placeholder_label = ctk.CTkLabel(
            self,
            text="📉 Los gráficos se generarán automáticamente al calcular el modelo.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        self.placeholder_label.pack(expand=True, fill="both", padx=20, pady=40)

    def mostrar_figura(self, fig: matplotlib.figure.Figure):
        """Reemplaza el contenido del frame con una nueva figura de Matplotlib."""
        self.limpiar()

        self.fig = fig
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        
        widget = self.canvas.get_tk_widget()
        widget.pack(expand=True, fill="both", padx=6, pady=6)

    def limpiar(self):
        """Limpia el canvas y destruye widgets de gráficos anteriores."""
        if self.placeholder_label and self.placeholder_label.winfo_exists():
            self.placeholder_label.pack_forget()

        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        if self.toolbar is not None:
            self.toolbar.destroy()
            self.toolbar = None

        self.fig = None
