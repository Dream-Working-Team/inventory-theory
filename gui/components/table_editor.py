"""
Componente de Tabla Dinámica interactiva para agregar, editar y eliminar filas.
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
from ..theme import Theme


class TableEditor(ctk.CTkFrame):
    """
    Componente POO que encapsula un ttk.Treeview estilizado con botones de acción
    para agregar, eliminar y gestionar filas de datos tabulares (tramos, productos).
    """

    def __init__(
        self,
        master,
        columnas: List[str],
        titulos: List[str],
        anchos: Optional[List[int]] = None,
        on_change_callback: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=8, border_width=1, border_color=Theme.BORDER_COLOR, **kwargs)
        
        self.columnas = columnas
        self.titulos = titulos
        self.anchos = anchos if anchos is not None else [100] * len(columnas)
        self.on_change = on_change_callback

        # Configuración del estilo TTK para modo oscuro
        self._configurar_estilos_ttk()

        # Contenedor de la tabla con scrollbar
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.tree = ttk.Treeview(
            table_container,
            columns=self.columnas,
            show="headings",
            style="Dark.Treeview",
            selectmode="browse",
            height=6
        )

        for col, tit, w in zip(self.columnas, self.titulos, self.anchos):
            self.tree.heading(col, text=tit)
            self.tree.column(col, width=w, anchor="center")

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

    def _configurar_estilos_ttk(self):
        """Aplica colores oscuros al widget ttk.Treeview."""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Dark.Treeview",
            background=Theme.BG_INPUT,
            foreground=Theme.TEXT_MAIN,
            fieldbackground=Theme.BG_INPUT,
            bordercolor=Theme.BORDER_COLOR,
            darkcolor=Theme.BORDER_COLOR,
            lightcolor=Theme.BORDER_COLOR,
            font=(Theme.FONT_FAMILY, 9),
            rowheight=26
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=Theme.BG_SIDEBAR,
            foreground=Theme.TEXT_MAIN,
            relief="flat",
            font=(Theme.FONT_FAMILY, 9, "bold"),
            padding=5
        )
        style.map("Dark.Treeview", background=[("selected", Theme.PRIMARY)], foreground=[("selected", "#FFFFFF")])
        style.map("Dark.Treeview.Heading", background=[("active", Theme.BG_INPUT)])

    def insertar_fila(self, valores: List[Any]) -> str:
        """Inserta una nueva fila al final de la tabla."""
        item_id = self.tree.insert("", "end", values=valores)
        if self.on_change:
            self.on_change()
        return item_id

    def eliminar_seleccionada(self):
        """Elimina la fila seleccionada por el usuario."""
        selected = self.tree.selection()
        if selected:
            for item in selected:
                self.tree.delete(item)
            if self.on_change:
                self.on_change()

    def limpiar_todo(self):
        """Elimina todas las filas de la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.on_change:
            self.on_change()

    def obtener_todas_las_filas(self) -> List[List[Any]]:
        """Retorna una lista con las filas actuales y sus valores."""
        filas = []
        for item in self.tree.get_children():
            filas.append(self.tree.item(item)["values"])
        return filas
