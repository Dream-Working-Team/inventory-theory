"""
Vista interactiva para el Modelo Determinístico EOQ Clásico (Modelo de Wilson).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional

from models.eoq import ModeloEOQ
from services.exportador import ExportadorServicio
from ..theme import Theme
from ..components.plot_frame import PlotFrame
from ..components.metric_card import MetricCard


class VistaEOQ(ctk.CTkScrollableFrame):
    """
    Vista POO para parametrización, cálculo, visualización y exportación
    del Modelo de Cantidad Económica de Pedido (EOQ Clásico).
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.modelo_actual: Optional[ModeloEOQ] = None
        self._construir_interfaz()
        self.calcular()

    def _construir_interfaz(self):
        # 1. Encabezado de la Vista
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="📦 Modelo Determinístico Clásico (EOQ / Wilson)",
            font=Theme.font_title(),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        )
        title_lbl.pack(fill="x")

        desc_lbl = ctk.CTkLabel(
            header_frame,
            text="Determina el tamaño óptimo de lote que minimiza la suma de costos de ordenar y almacenar bajo demanda y lead time conocidos.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        desc_lbl.pack(fill="x", pady=(2, 0))

        # 2. Contenedor Principal (Panel Izquierdo: Parámetros | Panel Derecho: Métricas y Gráficos)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # --- PANEL IZQUIERDO: Formulario de Parámetros ---
        left_panel = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR, width=340)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)

        ctk.CTkLabel(left_panel, text="⚙️ Parámetros de Entrada", font=Theme.font_subtitle(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(15, 10))

        # Campos de entrada
        self.entry_D = self._crear_campo(left_panel, "Demanda Anual (D) [unidades/año]:", "5000")
        self.entry_S = self._crear_campo(left_panel, "Costo por Pedir / Ordenar (S o K) [$]:", "49.0")
        self.entry_C = self._crear_campo(left_panel, "Costo Unitario de Compra (C) [$]:", "5.0")
        
        # Selector de H: Porcentaje i vs Valor directo H
        ctk.CTkLabel(left_panel, text="Modo Costo de Almacenamiento (H):", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(8, 2))
        self.var_modo_h = ctk.StringVar(value="porcentaje")
        radio_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        radio_frame.pack(fill="x", padx=15, pady=2)
        ctk.CTkRadioButton(radio_frame, text="Tasa i (%)", variable=self.var_modo_h, value="porcentaje", command=self._actualizar_modo_h, font=Theme.font_body()).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(radio_frame, text="H Directo ($)", variable=self.var_modo_h, value="directo", command=self._actualizar_modo_h, font=Theme.font_body()).pack(side="left")

        self.entry_i = self._crear_campo(left_panel, "Tasa Anual de Almacenamiento (i) [%]:", "20.0")
        self.entry_H = self._crear_campo(left_panel, "Costo Almacenamiento Fijo (H) [$/u/año]:", "1.0")
        self.entry_H.pack_forget()  # Oculto por defecto

        self.entry_LT = self._crear_campo(left_panel, "Tiempo de Entrega (Lead Time) [días]:", "5.0")
        self.entry_dias = self._crear_campo(left_panel, "Días Laborales al Año:", "250")

        # Botones de Acción
        btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(20, 15))

        btn_calc = ctk.CTkButton(
            btn_frame,
            text="⚡ Calcular Modelo",
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.calcular
        )
        btn_calc.pack(fill="x", pady=(0, 8))

        btn_export = ctk.CTkButton(
            btn_frame,
            text="📥 Exportar Reporte (.txt)",
            font=Theme.font_body(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            hover_color=Theme.BG_INPUT_HOVER,
            command=self.exportar_txt
        )
        btn_export.pack(fill="x")

        # --- PANEL DERECHO: Tarjetas de Resultados, Gráficos y Texto ---
        right_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)

        # Tarjetas Métricas Superiores
        metrics_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 10))

        self.card_q = MetricCard(metrics_frame, titulo="LOTE ÓPTIMO (EOQ / Q*)", valor_inicial="-", subtitulo="unidades por orden", color_acento=Theme.SECONDARY)
        self.card_q.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.card_rop = MetricCard(metrics_frame, titulo="PUNTO DE REORDEN (ROP)", valor_inicial="-", subtitulo="unidades en existencia", color_acento=Theme.ACCENT_YELLOW)
        self.card_rop.pack(side="left", fill="both", expand=True, padx=6)

        self.card_n = MetricCard(metrics_frame, titulo="NÚMERO DE PEDIDOS (N)", valor_inicial="-", subtitulo="pedidos al año", color_acento=Theme.PRIMARY)
        self.card_n.pack(side="left", fill="both", expand=True, padx=6)

        self.card_ct = MetricCard(metrics_frame, titulo="COSTO TOTAL ANUAL (CT)", valor_inicial="-", subtitulo="costo global anual", color_acento=Theme.SUCCESS)
        self.card_ct.pack(side="left", fill="both", expand=True, padx=(6, 0))

        # Canvas de Gráficos Embebidos
        self.plot_frame = PlotFrame(right_panel, height=320)
        self.plot_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Cuadro de Resumen Detallado y Fórmulas
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
        self.txt_resultados.insert("1.0", "Presione '⚡ Calcular Modelo' para visualizar el análisis detallado y los gráficos.")

    def _crear_campo(self, parent, label_text: str, valor_default: str) -> ctk.CTkEntry:
        """Crea un label con su entry correspondiente."""
        ctk.CTkLabel(parent, text=label_text, font=Theme.font_body(), text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=15, pady=(6, 2))
        entry = ctk.CTkEntry(parent, font=Theme.font_body(), fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR)
        entry.insert(0, valor_default)
        entry.pack(fill="x", padx=15, pady=(0, 2))
        return entry

    def _actualizar_modo_h(self):
        """Alterna entre mostrar tasa i (%) o costo fijo H ($)."""
        if self.var_modo_h.get() == "porcentaje":
            self.entry_H.pack_forget()
            self.entry_i.pack(fill="x", padx=15, pady=(0, 2), after=self.entry_C)
        else:
            self.entry_i.pack_forget()
            self.entry_H.pack(fill="x", padx=15, pady=(0, 2), after=self.entry_C)

    def cargar_parametros(self, D: float, S: float, C: float, H: Optional[float] = None, i: Optional[float] = None, LT: float = 0.0, dias: int = 250):
        """Carga parámetros programáticamente (usado por el banco de ejercicios)."""
        self.entry_D.delete(0, "end")
        self.entry_D.insert(0, str(D))
        self.entry_S.delete(0, "end")
        self.entry_S.insert(0, str(S))
        self.entry_C.delete(0, "end")
        self.entry_C.insert(0, str(C))
        self.entry_LT.delete(0, "end")
        self.entry_LT.insert(0, str(LT))
        self.entry_dias.delete(0, "end")
        self.entry_dias.insert(0, str(dias))

        if H is not None:
            self.var_modo_h.set("directo")
            self._actualizar_modo_h()
            self.entry_H.delete(0, "end")
            self.entry_H.insert(0, str(H))
        elif i is not None:
            self.var_modo_h.set("porcentaje")
            self._actualizar_modo_h()
            self.entry_i.delete(0, "end")
            self.entry_i.insert(0, str(i * 100 if i <= 1.0 else i))

        self.calcular()

    def calcular(self):
        """Lee los campos, instancia ModeloEOQ, calcula y actualiza la vista."""
        try:
            D = float(self.entry_D.get())
            S = float(self.entry_S.get())
            C = float(self.entry_C.get())
            LT = float(self.entry_LT.get())
            dias = int(self.entry_dias.get())

            if self.var_modo_h.get() == "porcentaje":
                i_val = float(self.entry_i.get()) / 100.0
                H_val = None
            else:
                i_val = None
                H_val = float(self.entry_H.get())

            # Instanciación POO
            self.modelo_actual = ModeloEOQ(
                demanda_anual=D,
                costo_pedido=S,
                costo_unitario=C,
                tasa_almacenamiento=i_val,
                costo_almacenamiento=H_val,
                lead_time_dias=LT,
                dias_laborales_anuales=dias
            )

            res = self.modelo_actual.calcular()

            # Actualizar Métricas Visuales
            self.card_q.actualizar(f"{res['Q_optimo']:,.2f} u.", f"Aprox. {round(res['Q_optimo'])} u/pedido")
            self.card_rop.actualizar(f"{res['punto_reorden_ROP']:,.2f} u.", f"d={res['demanda_diaria']:.1f} u/día × LT={LT:.0f}d")
            self.card_n.actualizar(f"{res['N_pedidos_anuales']:,.2f}", f"Cada {res['T_dias_entre_pedidos']:.1f} días laborables")
            self.card_ct.actualizar(f"${res['costo_total_anual']:,.2f}", f"Inv: ${res['costo_total_inventario']:,.2f}")

            # Actualizar Texto Detallado
            reporte = self.modelo_actual.generar_reporte_txt()
            self.txt_resultados.delete("1.0", "end")
            self.txt_resultados.insert("1.0", reporte)

            # Actualizar Gráficos
            fig = self.modelo_actual.generar_figura()
            self.plot_frame.mostrar_figura(fig)

        except ValueError as e:
            messagebox.showerror("Error en Parámetros", f"Por favor verifica los valores ingresados:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Ocurrió un error inesperado al calcular:\n{str(e)}")

    def exportar_txt(self):
        """Exporta el reporte del modelo actual a un archivo .txt."""
        if self.modelo_actual is None or not self.modelo_actual.calculado:
            messagebox.showwarning("Atención", "Primero debe calcular el modelo para poder exportar los resultados.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")],
            title="Guardar Reporte EOQ en Texto Plano"
        )
        if ruta:
            try:
                ExportadorServicio.exportar_modelo_a_txt(self.modelo_actual, ruta)
                messagebox.showinfo("Exportación Exitosa", f"El reporte fue guardado correctamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo:\n{str(e)}")
