"""
Vista interactiva para el Modelo de Quiebre de Precios / Descuentos por Cantidad.
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
from typing import Optional, List

from models.quiebre_precios import ModeloQuiebrePrecios, TramoDescuento
from services.exportador import ExportadorServicio
from ..theme import Theme
from ..components.plot_frame import PlotFrame
from ..components.metric_card import MetricCard
from ..components.table_editor import TableEditor


class VistaQuiebre(ctk.CTkScrollableFrame):
    """
    Vista POO para evaluación de descuentos por volumen, análisis de factibilidad
    y selección del lote óptimo global.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.modelo_actual: Optional[ModeloQuiebrePrecios] = None
        self._construir_interfaz()
        self.calcular()

    def _construir_interfaz(self):
        # 1. Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))

        ctk.CTkLabel(
            header_frame,
            text="🏷️ Modelo con Quiebre de Precios (Descuentos por Cantidad)",
            font=Theme.font_title(),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            header_frame,
            text="Evalúa múltiples tramos de descuento por volumen, ajusta cantidades a puntos de quiebre y determina el mínimo global de costo total.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # 2. Contenedor Principal (Panel Izquierdo: Parámetros + Tabla | Panel Derecho: Métricas + Gráficos)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # --- PANEL IZQUIERDO: Parámetros y Editor de Tramos ---
        left_panel = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR, width=420)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)

        ctk.CTkLabel(left_panel, text="⚙️ Parámetros Generales", font=Theme.font_subtitle(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(15, 8))

        self.entry_D = self._crear_campo(left_panel, "Demanda Anual (D) [unidades/año]:", "5000")
        self.entry_S = self._crear_campo(left_panel, "Costo por Pedir / Ordenar (S) [$]:", "49.0")
        self.entry_i = self._crear_campo(left_panel, "Tasa Anual de Almacenamiento (i) [%]:", "20.0")

        # Sección de Tramos
        ctk.CTkLabel(left_panel, text="📊 Tramos de Descuento Configurados", font=Theme.font_section(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(12, 4))

        self.table_tramos = TableEditor(
            left_panel,
            columnas=["tramo", "q_min", "q_max", "precio", "desc"],
            titulos=["Tr.", "Q Mín", "Q Máx", "Precio ($)", "Desc. (%)"],
            anchos=[35, 75, 75, 75, 65]
        )
        self.table_tramos.pack(fill="x", padx=15, pady=(0, 8))

        # Botones de gestión de tabla
        tbl_btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        tbl_btn_frame.pack(fill="x", padx=15, pady=(0, 12))

        btn_add = ctk.CTkButton(tbl_btn_frame, text="➕ Agregar Tramo", font=Theme.font_small(), width=110, fg_color=Theme.BG_INPUT, hover_color=Theme.BG_INPUT_HOVER, command=self._abrir_dialogo_agregar_tramo)
        btn_add.pack(side="left", padx=(0, 4))

        btn_del = ctk.CTkButton(tbl_btn_frame, text="🗑️ Eliminar Fila", font=Theme.font_small(), width=100, fg_color=Theme.BG_INPUT, hover_color=Theme.BG_INPUT_HOVER, command=self.table_tramos.eliminar_seleccionada)
        btn_del.pack(side="left", padx=4)

        btn_demo = ctk.CTkButton(tbl_btn_frame, text="🔄 Cargar Ejemplo", font=Theme.font_small(), width=110, fg_color=Theme.BG_INPUT, hover_color=Theme.BG_INPUT_HOVER, command=self._cargar_ejemplo_defecto)
        btn_demo.pack(side="right")

        # Botones de Ejecución
        btn_calc = ctk.CTkButton(
            left_panel,
            text="⚡ Optimizar Quiebre de Precios",
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

        # --- PANEL DERECHO: Tarjetas, Gráficos y Reporte ---
        right_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)

        # Tarjetas Métricas
        metrics_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 10))

        self.card_q = MetricCard(metrics_frame, titulo="LOTE ÓPTIMO GLOBAL (Q*)", valor_inicial="-", subtitulo="unidades recomendadas", color_acento=Theme.ACCENT_YELLOW)
        self.card_q.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.card_precio = MetricCard(metrics_frame, titulo="PRECIO UNITARIO ÓPTIMO", valor_inicial="-", subtitulo="por unidad en el tramo", color_acento=Theme.SECONDARY)
        self.card_precio.pack(side="left", fill="both", expand=True, padx=6)

        self.card_ct = MetricCard(metrics_frame, titulo="COSTO TOTAL ANUAL MÍNIMO", valor_inicial="-", subtitulo="suma global de costos", color_acento=Theme.SUCCESS)
        self.card_ct.pack(side="left", fill="both", expand=True, padx=6)

        self.card_ahorro = MetricCard(metrics_frame, titulo="AHORRO ANUAL TOTAL", valor_inicial="-", subtitulo="vs tramo sin descuento", color_acento=Theme.PRIMARY)
        self.card_ahorro.pack(side="left", fill="both", expand=True, padx=(6, 0))

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
        self.txt_resultados.insert("1.0", "Configure los tramos de descuento y presione '⚡ Optimizar Quiebre de Precios'.")

        # Cargar ejemplo inicial de la cátedra
        self._cargar_ejemplo_defecto()

    def _crear_campo(self, parent, label_text: str, valor_default: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label_text, font=Theme.font_body(), text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=15, pady=(4, 2))
        entry = ctk.CTkEntry(parent, font=Theme.font_body(), fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR)
        entry.insert(0, valor_default)
        entry.pack(fill="x", padx=15, pady=(0, 2))
        return entry

    def _cargar_ejemplo_defecto(self):
        """Carga el problema clásico de 3 tramos de la guía de la UJAP."""
        self.table_tramos.limpiar_todo()
        self.table_tramos.insertar_fila(["1", "0", "999", "5.00", "0%"])
        self.table_tramos.insertar_fila(["2", "1000", "1999", "4.80", "4%"])
        self.table_tramos.insertar_fila(["3", "2000", "Inf", "4.75", "5%"])

    def _abrir_dialogo_agregar_tramo(self):
        """Abre ventana modal para ingresar un nuevo tramo con botones de acción visibles."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Nuevo Tramo de Descuento")
        dialog.geometry("380x430")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="➕ Ingrese Datos del Tramo", font=Theme.font_subtitle(), text_color=Theme.TEXT_MAIN).pack(pady=(15, 8))

        e_min = self._crear_campo(dialog, "Cantidad Mínima (Q Mín):", "0")
        e_max = self._crear_campo(dialog, "Cantidad Máxima (Q Máx / 'Inf'):", "999")
        e_precio = self._crear_campo(dialog, "Precio Unitario ($):", "5.0")
        e_desc = self._crear_campo(dialog, "Porcentaje Descuento (%):", "0.0")

        def guardar():
            try:
                q_min = float(e_min.get())
                max_str = e_max.get().strip().lower()
                q_max = "Inf" if max_str in ["inf", "infinito", "mas", "+"] else str(float(max_str))
                precio = float(e_precio.get())
                desc = float(e_desc.get())

                idx = len(self.table_tramos.obtener_todas_las_filas()) + 1
                self.table_tramos.insertar_fila([str(idx), f"{q_min:g}", q_max, f"{precio:.2f}", f"{desc:g}%"])
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos en los campos.")

        # Contenedor de Botones de Acción
        btn_box = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_box.pack(fill="x", padx=15, pady=(15, 15))

        btn_guardar = ctk.CTkButton(
            btn_box,
            text="💾 Guardar Tramo",
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=guardar
        )
        btn_guardar.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_cancelar = ctk.CTkButton(
            btn_box,
            text="❌ Cancelar",
            font=Theme.font_body(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            hover_color=Theme.BG_INPUT_HOVER,
            command=dialog.destroy
        )
        btn_cancelar.pack(side="right", fill="x", expand=True, padx=(6, 0))

    def cargar_datos_completos(self, D: float, S: float, i: float, tramos: List[TramoDescuento]):
        """Carga datos programáticamente desde el banco de ejercicios."""
        self.entry_D.delete(0, "end")
        self.entry_D.insert(0, str(D))
        self.entry_S.delete(0, "end")
        self.entry_S.insert(0, str(S))
        self.entry_i.delete(0, "end")
        self.entry_i.insert(0, str(i * 100 if i <= 1.0 else i))

        self.table_tramos.limpiar_todo()
        for idx, t in enumerate(tramos, start=1):
            q_max_str = "Inf" if t.q_max == float('inf') else f"{t.q_max:g}"
            self.table_tramos.insertar_fila([str(idx), f"{t.q_min:g}", q_max_str, f"{t.precio_unitario:.2f}", f"{t.descuento_porcentaje:g}%"])

        self.calcular()

    def calcular(self):
        """Lee datos de interfaz, instancia ModeloQuiebrePrecios y resuelve."""
        try:
            D = float(self.entry_D.get())
            S = float(self.entry_S.get())
            i = float(self.entry_i.get()) / 100.0

            filas = self.table_tramos.obtener_todas_las_filas()
            if not filas:
                messagebox.showwarning("Atención", "Debe agregar al menos un tramo de descuento.")
                return

            tramos_objs = []
            for f in filas:
                q_min = float(f[1])
                q_max_str = str(f[2]).strip().lower()
                q_max = float('inf') if q_max_str in ["inf", "infinito", "mas", "+"] else float(q_max_str)
                precio = float(f[3])
                desc_str = str(f[4]).replace("%", "").strip()
                desc = float(desc_str) if desc_str else 0.0

                tramos_objs.append(TramoDescuento(
                    q_min=q_min,
                    q_max=q_max,
                    precio_unitario=precio,
                    descuento_porcentaje=desc
                ))

            # Instanciación POO
            self.modelo_actual = ModeloQuiebrePrecios(
                demanda_anual=D,
                costo_pedido=S,
                tasa_almacenamiento=i,
                tramos=tramos_objs
            )

            res = self.modelo_actual.calcular()

            # Actualizar tarjetas
            self.card_q.actualizar(f"{res['Q_optimo_global']:,.2f} u.", f"Tramo #{res['mejor_tramo_index']}")
            self.card_precio.actualizar(f"${res['precio_unitario_optimo']:,.2f}", "por unidad")
            self.card_ct.actualizar(f"${res['costo_total_minimo']:,.2f}", "Costo anual óptimo")
            self.card_ahorro.actualizar(f"${res['ahorro_anual_respecto_base']:,.2f}", "Ahorro vs precio base")

            # Actualizar Texto
            reporte = self.modelo_actual.generar_reporte_txt()
            self.txt_resultados.delete("1.0", "end")
            self.txt_resultados.insert("1.0", reporte)

            # Actualizar Gráficos
            fig = self.modelo_actual.generar_figura()
            self.plot_frame.mostrar_figura(fig)

        except ValueError as e:
            messagebox.showerror("Error en Datos", f"Verifique los números ingresados:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Ocurrió un error inesperado:\n{str(e)}")

    def exportar_txt(self):
        """Exporta el reporte del modelo actual a un archivo .txt."""
        if self.modelo_actual is None or not self.modelo_actual.calculado:
            messagebox.showwarning("Atención", "Primero debe calcular el modelo para poder exportar.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")],
            title="Guardar Reporte Quiebre de Precios en Texto Plano"
        )
        if ruta:
            try:
                ExportadorServicio.exportar_modelo_a_txt(self.modelo_actual, ruta)
                messagebox.showinfo("Exportación Exitosa", f"Reporte guardado exitosamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo:\n{str(e)}")
