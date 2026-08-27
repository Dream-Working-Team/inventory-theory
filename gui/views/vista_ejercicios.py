"""
Vista para el Banco de Ejercicios Guiados de la Cátedra de Métodos Cuantitativos.
Universidad José Antonio Páez.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import List, Callable, Optional

from services.banco_ejercicios import BancoEjerciciosService, EjercicioCatedra
from services.exportador import ExportadorServicio
from ..theme import Theme


class VistaEjercicios(ctk.CTkScrollableFrame):
    """
    Vista POO para explorar los ejercicios resueltos de la guía de la UJAP
    con visualización paso a paso y precarga interactiva en las calculadoras.
    """

    def __init__(self, master, on_cargar_ejercicio_callback: Optional[Callable] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_cargar_ejercicio = on_cargar_ejercicio_callback
        self.ejercicios: List[EjercicioCatedra] = BancoEjerciciosService.obtener_todos_los_ejercicios()
        self.ejercicio_seleccionado: Optional[EjercicioCatedra] = self.ejercicios[0] if self.ejercicios else None
        
        self._construir_interfaz()

    def _construir_interfaz(self):
        # 1. Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))

        ctk.CTkLabel(
            header_frame,
            text="📚 Banco de Ejercicios Guiados (Guía Oficial UJAP)",
            font=Theme.font_title(),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            header_frame,
            text="Colección completa de problemas resueltos de las guías y tareas de la cátedra de Métodos Cuantitativos.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # 2. Contenedor Principal (Panel Izquierdo: Lista de Ejercicios | Panel Derecho: Detalle y Resolución)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # --- PANEL IZQUIERDO: Selector de Ejercicios ---
        left_panel = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR, width=320)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)

        ctk.CTkLabel(left_panel, text="📋 Lista de Problemas", font=Theme.font_subtitle(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(15, 10))

        # Lista de Botones para cada ejercicio
        self.btn_ejercicios = []
        for idx, ej in enumerate(self.ejercicios):
            btn = ctk.CTkButton(
                left_panel,
                text=f"{ej.id_ejercicio}: {ej.titulo[:32]}...",
                font=Theme.font_body(),
                fg_color=Theme.PRIMARY if idx == 0 else Theme.BG_INPUT,
                hover_color=Theme.PRIMARY_HOVER,
                anchor="w",
                command=lambda e=ej, b_idx=idx: self._seleccionar_ejercicio(e, b_idx)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.btn_ejercicios.append(btn)

        # --- PANEL DERECHO: Detalle del Problema y Resolución Paso a Paso ---
        right_panel = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        right_panel.pack(side="right", fill="both", expand=True)

        # Título y Fuente del ejercicio
        self.lbl_det_titulo = ctk.CTkLabel(right_panel, text="", font=Theme.font_subtitle(), text_color=Theme.TEXT_MAIN, anchor="w")
        self.lbl_det_titulo.pack(fill="x", padx=20, pady=(15, 2))

        self.lbl_det_fuente = ctk.CTkLabel(right_panel, text="", font=Theme.font_small(), text_color=Theme.SECONDARY, anchor="w")
        self.lbl_det_fuente.pack(fill="x", padx=20, pady=(0, 10))

        # Barra de Acciones (Cargar en Calculadora y Exportar)
        action_bar = ctk.CTkFrame(right_panel, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(0, 10))

        self.btn_cargar = ctk.CTkButton(
            action_bar,
            text="🚀 Cargar Parámetros en la Calculadora Interactiva",
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._cargar_en_calculadora
        )
        self.btn_cargar.pack(side="left", padx=(0, 10))

        btn_export = ctk.CTkButton(
            action_bar,
            text="📥 Exportar Ejercicio (.txt)",
            font=Theme.font_body(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            hover_color=Theme.BG_INPUT_HOVER,
            command=self._exportar_ejercicio_txt
        )
        btn_export.pack(side="left")

        # Texto del Enunciado y Resolución Paso a Paso
        self.txt_detalle = ctk.CTkTextbox(
            right_panel,
            font=Theme.font_code(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_MAIN,
            height=440
        )
        self.txt_detalle.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Mostrar primer ejercicio por defecto
        if self.ejercicio_seleccionado:
            self._mostrar_detalle_ejercicio(self.ejercicio_seleccionado)

    def _seleccionar_ejercicio(self, ej: EjercicioCatedra, btn_idx: int):
        """Maneja la selección de un ejercicio de la lista."""
        self.ejercicio_seleccionado = ej
        for i, b in enumerate(self.btn_ejercicios):
            b.configure(fg_color=Theme.PRIMARY if i == btn_idx else Theme.BG_INPUT)
        self._mostrar_detalle_ejercicio(ej)

    def _mostrar_detalle_ejercicio(self, ej: EjercicioCatedra):
        """Muestra el contenido estructurado del ejercicio seleccionado."""
        self.lbl_det_titulo.configure(text=f"📌 {ej.titulo}")
        self.lbl_det_fuente.configure(text=f"Cátedra Métodos Cuantitativos UJAP | {ej.fuente}")

        contenido = [
            "=" * 78,
            "1. ENUNCIADO DEL PROBLEMA:",
            "=" * 78,
            ej.enunciado,
            "",
            "=" * 78,
            "2. DATOS EXTRAÍDOS DEL PROBLEMA:",
            "=" * 78,
        ]
        for k, v in ej.datos_resumen.items():
            contenido.append(f"   • {k:<30}: {v}")

        contenido.extend([
            "",
            "=" * 78,
            "3. RESOLUCIÓN MATEMÁTICA PASO A PASO:",
            "=" * 78,
            ej.solucion_explicada,
            "",
            "=" * 78,
            "4. RESULTADOS FORMALES DEL MODELO POO:",
            "=" * 78,
            ej.modelo_instanciado.generar_reporte_txt()
        ])

        self.txt_detalle.delete("1.0", "end")
        self.txt_detalle.insert("1.0", "\n".join(contenido))

    def _cargar_en_calculadora(self):
        """Envía el ejercicio al callback para precargarlo en la pestaña correspondiente."""
        if self.ejercicio_seleccionado and self.on_cargar_ejercicio:
            self.on_cargar_ejercicio(self.ejercicio_seleccionado)

    def _exportar_ejercicio_txt(self):
        """Exporta el ejercicio resuelto a un archivo .txt."""
        if self.ejercicio_seleccionado is None:
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{self.ejercicio_seleccionado.id_ejercicio}_solucion.txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")],
            title="Guardar Ejercicio Resuelto en Texto Plano"
        )
        if ruta:
            try:
                ExportadorServicio.exportar_modelo_a_txt(self.ejercicio_seleccionado.modelo_instanciado, ruta)
                messagebox.showinfo("Exportación Exitosa", f"Ejercicio guardado correctamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
