"""
Ventana Principal de la Aplicación de Escritorio de Teoría de Inventarios (POO).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Dict, Optional

from .theme import Theme
from .views.vista_eoq import VistaEOQ
from .views.vista_quiebre import VistaQuiebre
from .views.vista_restricciones import VistaRestricciones
from .views.vista_probabilistico import VistaProbabilistico
from .views.vista_ejercicios import VistaEjercicios
from .views.vista_teoria import VistaTeoria
from services.banco_ejercicios import EjercicioCatedra
from services.exportador import ExportadorServicio


class AplicacionInventarios(ctk.CTk):
    """
    Clase principal que orquesta la interfaz gráfica de usuario (GUI),
    la navegación entre vistas y la exportación de resultados.
    """

    def __init__(self):
        super().__init__()

        # Configuración de Ventana
        self.title("Sistema POO de Teoría de Inventarios — Métodos Cuantitativos (UJAP)")
        self.geometry("1300x820")
        self.minsize(1100, 700)
        self.configure(fg_color=Theme.BG_DARK)

        # Estado de navegación
        self.vista_actual_nombre = "eoq"
        self.vistas: Dict[str, ctk.CTkFrame] = {}

        # Construir Interfaz
        self._construir_layout()
        self._inicializar_vistas()
        self.mostrar_vista("eoq")

    def _construir_layout(self):
        """Construye el sidebar lateral y el contenedor principal."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA LATERAL (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=Theme.BG_SIDEBAR, border_width=1, border_color=Theme.BORDER_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Título del Software
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(20, 20))

        ctk.CTkLabel(
            logo_frame,
            text="📦 INVENTORY PRO",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.PRIMARY,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            logo_frame,
            text="Métodos Cuantitativos • UJAP",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x")

        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color=Theme.BORDER_COLOR).pack(fill="x", padx=15, pady=(0, 15))

        # Botones de Navegación
        self.nav_buttons = {}
        items_menu = [
            ("eoq", "📦 EOQ Clásico (Wilson)"),
            ("quiebre", "🏷️ Quiebre de Precios"),
            ("restricciones", "🏭 Multi-Artículos (Lagrange)"),
            ("probabilistico", "🎲 Modelo Probabilístico"),
            ("ejercicios", "📚 Banco de Ejercicios UJAP"),
            ("teoria", "📖 Formulario y Teoría"),
        ]

        ctk.CTkLabel(self.sidebar, text="MODELOS Y HERRAMIENTAS", font=Theme.font_small(), text_color=Theme.TEXT_SUBTLE, anchor="w").pack(fill="x", padx=20, pady=(0, 6))

        for clave, texto in items_menu:
            btn = ctk.CTkButton(
                self.sidebar,
                text=texto,
                font=Theme.font_body(),
                fg_color="transparent",
                text_color=Theme.TEXT_MAIN,
                hover_color=Theme.BG_INPUT,
                anchor="w",
                height=38,
                command=lambda c=clave: self.mostrar_vista(c)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[clave] = btn

        # Espacio expandible
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Pie del Sidebar: Exportación global y créditos
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.pack(fill="x", padx=15, pady=20)

        btn_export_all = ctk.CTkButton(
            footer_frame,
            text="📑 Exportar Todo a (.txt)",
            font=Theme.font_body_bold(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.PRIMARY,
            text_color=Theme.PRIMARY,
            hover_color=Theme.BG_INPUT_HOVER,
            command=self.exportar_todo_a_txt
        )
        btn_export_all.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            footer_frame,
            text="Sistema POO v1.0 • Python & Tkinter\nUniversidad José Antonio Páez",
            font=Theme.font_small(),
            text_color=Theme.TEXT_SUBTLE,
            justify="center"
        ).pack(fill="x")

        # --- CONTENEDOR PRINCIPAL DE VISTAS ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

    def _inicializar_vistas(self):
        """Instancia todas las vistas de la aplicación."""
        self.vistas["eoq"] = VistaEOQ(self.main_container)
        self.vistas["quiebre"] = VistaQuiebre(self.main_container)
        self.vistas["restricciones"] = VistaRestricciones(self.main_container)
        self.vistas["probabilistico"] = VistaProbabilistico(self.main_container)
        self.vistas["ejercicios"] = VistaEjercicios(self.main_container, on_cargar_ejercicio_callback=self._cargar_ejercicio_en_vista)
        self.vistas["teoria"] = VistaTeoria(self.main_container)

    def mostrar_vista(self, clave_vista: str):
        """Muestra la vista seleccionada y resalta el botón activo en el sidebar."""
        if clave_vista not in self.vistas:
            return

        self.vista_actual_nombre = clave_vista

        # Ocultar todas las vistas para evitar bloqueos de eventos
        for v in self.vistas.values():
            v.grid_remove()

        # Mostrar únicamente la vista activa
        self.vistas[clave_vista].grid(row=0, column=0, sticky="nsew")

        # Actualizar colores de botones del menú
        for k, btn in self.nav_buttons.items():
            if k == clave_vista:
                btn.configure(fg_color=Theme.PRIMARY, text_color="#FFFFFF", font=Theme.font_body_bold())
            else:
                btn.configure(fg_color="transparent", text_color=Theme.TEXT_MAIN, font=Theme.font_body())

    def _cargar_ejercicio_en_vista(self, ejercicio: EjercicioCatedra):
        """Precarga un ejercicio de la cátedra en su vista correspondiente y la abre."""
        tipo = ejercicio.tipo_modelo
        mod = ejercicio.modelo_instanciado

        if tipo == "eoq":
            self.mostrar_vista("eoq")
            vista_eoq: VistaEOQ = self.vistas["eoq"]
            vista_eoq.cargar_parametros(
                D=mod.D,
                S=mod.S,
                C=mod.C,
                H=mod.H_input,
                i=mod.i,
                LT=mod.LT,
                dias=mod.dias_ano
            )
            messagebox.showinfo("Ejercicio Cargado", f"Se han cargado los datos del ejercicio '{ejercicio.titulo}' en el Modelo EOQ.")

        elif tipo == "quiebre":
            self.mostrar_vista("quiebre")
            vista_quiebre: VistaQuiebre = self.vistas["quiebre"]
            vista_quiebre.cargar_datos_completos(
                D=mod.D,
                S=mod.S,
                i=mod.i,
                tramos=mod.tramos
            )
            messagebox.showinfo("Ejercicio Cargado", f"Se han cargado los datos del ejercicio '{ejercicio.titulo}' en el Modelo de Quiebre de Precios.")

        elif tipo == "restricciones":
            self.mostrar_vista("restricciones")
            vista_rest: VistaRestricciones = self.vistas["restricciones"]
            vista_rest.cargar_datos_completos(
                limite=mod.limite_recurso,
                tipo=mod.tipo_restriccion,
                es_promedio=mod.es_promedio,
                articulos=mod.articulos
            )
            messagebox.showinfo("Ejercicio Cargado", f"Se han cargado los datos del ejercicio '{ejercicio.titulo}' en el Modelo con Restricciones.")

        elif tipo == "probabilistico":
            self.mostrar_vista("probabilistico")
            vista_prob: VistaProbabilistico = self.vistas["probabilistico"]
            vista_prob.cargar_datos_completos(
                d_media=mod.d_media,
                sigma_d=mod.sigma_d,
                LT=mod.LT,
                SL=mod.SL_pct,
                S=mod.S,
                C=mod.C,
                i=mod.i or 0.20,
                dias=mod.dias_ano
            )
            messagebox.showinfo("Ejercicio Cargado", f"Se han cargado los datos del ejercicio '{ejercicio.titulo}' en el Modelo Probabilístico.")

    def exportar_todo_a_txt(self):
        """Calcula todos los modelos activos y genera un informe consolidado en archivo plano .txt."""
        # Asegurar que los modelos estén calculados
        modelos_a_exportar = []
        
        # 1. EOQ
        if self.vistas["eoq"].modelo_actual is None:
            self.vistas["eoq"].calcular()
        if self.vistas["eoq"].modelo_actual:
            modelos_a_exportar.append(self.vistas["eoq"].modelo_actual)

        # 2. Quiebre
        if self.vistas["quiebre"].modelo_actual is None:
            self.vistas["quiebre"].calcular()
        if self.vistas["quiebre"].modelo_actual:
            modelos_a_exportar.append(self.vistas["quiebre"].modelo_actual)

        # 3. Restricciones
        if self.vistas["restricciones"].modelo_actual is None:
            self.vistas["restricciones"].calcular()
        if self.vistas["restricciones"].modelo_actual:
            modelos_a_exportar.append(self.vistas["restricciones"].modelo_actual)

        # 4. Probabilístico
        if self.vistas["probabilistico"].modelo_actual is None:
            self.vistas["probabilistico"].calcular()
        if self.vistas["probabilistico"].modelo_actual:
            modelos_a_exportar.append(self.vistas["probabilistico"].modelo_actual)

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="Informe_Consolidado_Teoria_Inventarios_UJAP.txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")],
            title="Guardar Informe Consolidado de Inventarios"
        )
        if ruta:
            try:
                ExportadorServicio.exportar_consolidados(modelos_a_exportar, ruta)
                messagebox.showinfo("Informe Exportado", f"Informe consolidado guardado exitosamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al Exportar", f"No se pudo guardar el informe:\n{str(e)}")
