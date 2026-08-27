"""
Vista interactiva para el Modelo de Varios Artículos con Restricciones (Lagrange).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional, List

from models.restricciones import ModeloRestricciones, ArticuloRestriccion
from services.exportador import ExportadorServicio
from ..theme import Theme
from ..components.plot_frame import PlotFrame
from ..components.metric_card import MetricCard
from ..components.table_editor import TableEditor


class VistaRestricciones(ctk.CTkScrollableFrame):
    """
    Vista POO para optimización conjunta de múltiples productos sujetos a
    restricciones de capacidad de almacenamiento físico o presupuesto de capital.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.modelo_actual: Optional[ModeloRestricciones] = None
        self._construir_interfaz()
        self.calcular()

    def _construir_interfaz(self):
        # 1. Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))

        ctk.CTkLabel(
            header_frame,
            text="🏭 Modelo de Varios Artículos con Restricciones (Lagrange)",
            font=Theme.font_title(),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            header_frame,
            text="Resuelve la asignación óptima de tamaños de lote para múltiples productos compartiendo un recurso limitado (espacio físico o presupuesto) mediante Multiplicadores de Lagrange.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # 2. Contenedor Principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # --- PANEL IZQUIERDO: Configuración de Recurso y Tabla de Productos ---
        left_panel = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR, width=440)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)

        ctk.CTkLabel(left_panel, text="⚙️ Configuración del Recurso Limitante", font=Theme.font_subtitle(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(15, 8))

        # Tipo de Restricción
        ctk.CTkLabel(left_panel, text="Tipo de Recurso:", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(4, 2))
        self.var_tipo = ctk.StringVar(value="espacio")
        radio_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        radio_frame.pack(fill="x", padx=15, pady=2)
        ctk.CTkRadioButton(radio_frame, text="Espacio Almacén (m²)", variable=self.var_tipo, value="espacio", font=Theme.font_body()).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(radio_frame, text="Presupuesto Capital ($)", variable=self.var_tipo, value="presupuesto", font=Theme.font_body()).pack(side="left")

        self.entry_limite = self._crear_campo(left_panel, "Capacidad Máxima Disponible (Límite):", "220.0")

        # Base de Medición
        self.var_promedio = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(left_panel, text="Aplicar restricción a Inventario Promedio (Q/2)", variable=self.var_promedio, font=Theme.font_small()).pack(anchor="w", padx=15, pady=(6, 10))

        # Tabla de Artículos
        ctk.CTkLabel(left_panel, text="📦 Catálogo de Productos a Gestionar", font=Theme.font_section(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(8, 4))

        self.table_articulos = TableEditor(
            left_panel,
            columnas=["nombre", "demanda", "costo_p", "costo_u", "costo_h", "espacio"],
            titulos=["Producto", "D (anual)", "S ($)", "C ($)", "H ($/u/año)", "Espacio (u)"],
            anchos=[110, 65, 55, 55, 70, 65]
        )
        self.table_articulos.pack(fill="x", padx=15, pady=(0, 8))

        # Botones de Tabla
        tbl_btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        tbl_btn_frame.pack(fill="x", padx=15, pady=(0, 12))

        btn_add = ctk.CTkButton(tbl_btn_frame, text="➕ Añadir Prod.", font=Theme.font_small(), width=110, fg_color=Theme.BG_INPUT, hover_color=Theme.BG_INPUT_HOVER, command=self._abrir_dialogo_agregar_articulo)
        btn_add.pack(side="left", padx=(0, 4))

        btn_del = ctk.CTkButton(tbl_btn_frame, text="🗑️ Eliminar", font=Theme.font_small(), width=90, fg_color=Theme.BG_INPUT, hover_color=Theme.BG_INPUT_HOVER, command=self.table_articulos.eliminar_seleccionada)
        btn_del.pack(side="left", padx=4)

        btn_demo = ctk.CTkButton(tbl_btn_frame, text="🔄 Cargar Ejemplo", font=Theme.font_small(), width=120, fg_color=Theme.BG_INPUT, hover_color=Theme.BG_INPUT_HOVER, command=self._cargar_ejemplo_defecto)
        btn_demo.pack(side="right")

        # Botones de Acción
        btn_calc = ctk.CTkButton(
            left_panel,
            text="⚡ Optimizar con Multiplicadores Lagrange",
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.calcular
        )
        btn_calc.pack(fill="x", padx=15, pady=(5, 6))

        btn_export = ctk.CTkButton(
            left_panel,
            text="📥 Exportar Reporte (.txt)",
            font=Theme.font_body(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            hover_color=Theme.BG_INPUT_HOVER,
            command=self.exportar_txt
        )
        btn_export.pack(fill="x", padx=15, pady=(0, 15))

        # --- PANEL DERECHO: Tarjetas, Gráficos y Texto ---
        right_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)

        # Tarjetas Métricas
        metrics_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 10))

        self.card_lambda = MetricCard(metrics_frame, titulo="MULTIPLICADOR LAGRANGE (λ*)", valor_inicial="-", subtitulo="precio sombra del recurso", color_acento=Theme.ACCENT_YELLOW)
        self.card_lambda.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.card_estado = MetricCard(metrics_frame, titulo="ESTADO RESTRICCIÓN", valor_inicial="-", subtitulo="condición de capacidad", color_acento=Theme.SECONDARY)
        self.card_estado.pack(side="left", fill="both", expand=True, padx=6)

        self.card_recurso = MetricCard(metrics_frame, titulo="USO TOTAL DE CAPACIDAD", valor_inicial="-", subtitulo="ocupación real calculada", color_acento=Theme.PRIMARY)
        self.card_recurso.pack(side="left", fill="both", expand=True, padx=6)

        self.card_ct = MetricCard(metrics_frame, titulo="COSTO TOTAL ANUAL", valor_inicial="-", subtitulo="sistema conjunto", color_acento=Theme.SUCCESS)
        self.card_ct.pack(side="left", fill="both", expand=True, padx=(6, 0))

        # Canvas de Gráficos
        self.plot_frame = PlotFrame(right_panel, height=320)
        self.plot_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Cuadro de Resumen Detallado
        self.txt_resultados = ctk.CTkTextbox(
            right_panel,
            font=Theme.font_code(),
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_MAIN,
            height=160
        )
        self.txt_resultados.pack(fill="both", expand=True)
        self.txt_resultados.insert("1.0", "Presione '⚡ Optimizar con Multiplicadores Lagrange' para resolver la asignación óptima.")

        # Cargar ejemplo inicial
        self._cargar_ejemplo_defecto()

    def _crear_campo(self, parent, label_text: str, valor_default: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label_text, font=Theme.font_body(), text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=15, pady=(4, 2))
        entry = ctk.CTkEntry(parent, font=Theme.font_body(), fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR)
        entry.insert(0, valor_default)
        entry.pack(fill="x", padx=15, pady=(0, 2))
        return entry

    def _cargar_ejemplo_defecto(self):
        """Carga el caso de 3 artículos con restricción de espacio de 220 m²."""
        self.table_articulos.limpiar_todo()
        self.table_articulos.insertar_fila(["Producto A (Básico)", "1000", "40", "20", "4.0", "1.0"])
        self.table_articulos.insertar_fila(["Producto B (Premium)", "1500", "50", "35", "7.0", "1.5"])
        self.table_articulos.insertar_fila(["Producto C (Industrial)", "800", "60", "50", "10.0", "2.0"])
        self.entry_limite.delete(0, "end")
        self.entry_limite.insert(0, "220.0")

    def _abrir_dialogo_agregar_articulo(self):
        """Modal para añadir un nuevo producto al catálogo."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Producto al Inventario")
        dialog.geometry("360x380")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Datos del Producto", font=Theme.font_subtitle()).pack(pady=(15, 8))

        e_nom = self._crear_campo(dialog, "Nombre / Código Producto:", f"Producto {chr(65 + len(self.table_articulos.obtener_todas_las_filas()))}")
        e_d = self._crear_campo(dialog, "Demanda Anual (D):", "1000")
        e_s = self._crear_campo(dialog, "Costo por Pedido (S) [$]:", "50")
        e_c = self._crear_campo(dialog, "Costo Unitario (C) [$]:", "25")
        e_h = self._crear_campo(dialog, "Costo Almacenamiento (H) [$/u/año]:", "5.0")
        e_esp = self._crear_campo(dialog, "Espacio Unitario (a) [m²/u]:", "1.0")

        def guardar():
            try:
                nom = e_nom.get().strip() or "Producto"
                d_val = float(e_d.get())
                s_val = float(e_s.get())
                c_val = float(e_c.get())
                h_val = float(e_h.get())
                esp_val = float(e_esp.get())

                self.table_articulos.insertar_fila([nom, f"{d_val:g}", f"{s_val:g}", f"{c_val:g}", f"{h_val:g}", f"{esp_val:g}"])
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos en todos los campos.")

        ctk.CTkButton(dialog, text="Guardar Producto", font=Theme.font_body_bold(), fg_color=Theme.PRIMARY, command=guardar).pack(fill="x", padx=15, pady=15)

    def cargar_datos_completos(self, limite: float, tipo: str, es_promedio: bool, articulos: List[ArticuloRestriccion]):
        """Carga datos programáticamente desde el banco de ejercicios."""
        self.entry_limite.delete(0, "end")
        self.entry_limite.insert(0, str(limite))
        self.var_tipo.set(tipo)
        self.var_promedio.set(es_promedio)

        self.table_articulos.limpiar_todo()
        for art in articulos:
            self.table_articulos.insertar_fila([
                art.nombre,
                f"{art.demanda_anual:g}",
                f"{art.costo_pedido:g}",
                f"{art.costo_unitario:g}",
                f"{art.costo_almacenamiento:g}",
                f"{art.espacio_unitario:g}"
            ])

        self.calcular()

    def calcular(self):
        """Lee la interfaz, instancia ModeloRestricciones y calcula la solución óptima."""
        try:
            limite = float(self.entry_limite.get())
            tipo = self.var_tipo.get()
            es_prom = self.var_promedio.get()

            filas = self.table_articulos.obtener_todas_las_filas()
            if not filas:
                messagebox.showwarning("Atención", "Debe agregar al menos un producto a la lista.")
                return

            articulos_objs = []
            for f in filas:
                nom = str(f[0])
                d_val = float(f[1])
                s_val = float(f[2])
                c_val = float(f[3])
                h_val = float(f[4])
                esp_val = float(f[5])

                articulos_objs.append(ArticuloRestriccion(
                    nombre=nom,
                    demanda_anual=d_val,
                    costo_pedido=s_val,
                    costo_unitario=c_val,
                    costo_almacenamiento=h_val,
                    espacio_unitario=esp_val
                ))

            # Instanciación POO
            self.modelo_actual = ModeloRestricciones(
                limite_recurso=limite,
                tipo_restriccion=tipo,
                es_inventario_promedio=es_prom,
                articulos=articulos_objs
            )

            res = self.modelo_actual.calcular()

            # Actualizar tarjetas
            self.card_lambda.actualizar(f"λ* = {res['lambda_optimo']:.4f}", "Sombra marginal")
            self.card_estado.actualizar("ACTIVA (100% uso)" if res['restriccion_activa'] else "INACTIVA (Holgura)", "Capacidad crítica" if res['restriccion_activa'] else "Capacidad suficiente")
            self.card_recurso.actualizar(f"{res['uso_total_recurso']:,.2f} / {limite:,.0f}", "Espacio ocupado" if tipo == "espacio" else "Capital utilizado")
            self.card_ct.actualizar(f"${res['costo_total_con_restriccion']:,.2f}", f"Sobrecosto: +${res['sobrecosto_restriccion']:,.2f}")

            # Actualizar Texto
            reporte = self.modelo_actual.generar_reporte_txt()
            self.txt_resultados.delete("1.0", "end")
            self.txt_resultados.insert("1.0", reporte)

            # Actualizar Gráficos
            fig = self.modelo_actual.generar_figura()
            self.plot_frame.mostrar_figura(fig)

        except ValueError as e:
            messagebox.showerror("Error en Datos", f"Verifique los campos numéricos:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Ocurrió un error inesperado:\n{str(e)}")

    def exportar_txt(self):
        """Exporta el reporte del modelo a un archivo .txt."""
        if self.modelo_actual is None or not self.modelo_actual.calculado:
            messagebox.showwarning("Atención", "Primero debe calcular el modelo para exportar los resultados.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")],
            title="Guardar Reporte Multi-Artículo con Restricciones"
        )
        if ruta:
            try:
                ExportadorServicio.exportar_modelo_a_txt(self.modelo_actual, ruta)
                messagebox.showinfo("Exportación Exitosa", f"El archivo fue guardado exitosamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo:\n{str(e)}")
