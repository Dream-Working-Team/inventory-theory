"""
Vista interactiva para el Modelo Probabilístico de Inventarios (Demanda Normal y Lead Time).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional

from models.probabilistico import ModeloProbabilistico
from services.exportador import ExportadorServicio
from ..theme import Theme
from ..components.plot_frame import PlotFrame
from ..components.metric_card import MetricCard


class VistaProbabilistico(ctk.CTkScrollableFrame):
    """
    Vista POO para cálculo del Stock de Seguridad (SS), Punto de Reorden (ROP),
    evaluación del Nivel de Servicio Z y Simulación Estocástica Monte Carlo.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.modelo_actual: Optional[ModeloProbabilistico] = None
        self._construir_interfaz()
        self.calcular()

    def _construir_interfaz(self):
        # 1. Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))

        ctk.CTkLabel(
            header_frame,
            text="🎲 Modelo Probabilístico de Inventarios (Sistema Q, ROP)",
            font=Theme.font_title(),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            header_frame,
            text="Modela la incertidumbre en la demanda con distribución normal, dimensiona el Stock de Seguridad según el nivel de servicio y simula el riesgo de rotura de stock.",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # 2. Contenedor Principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # --- PANEL IZQUIERDO: Formulario de Parámetros Probabilísticos ---
        left_panel = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)

        ctk.CTkLabel(left_panel, text="⚙️ Parámetros Estocásticos", font=Theme.font_subtitle(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(15, 8))

        self.entry_d_media = self._crear_campo(left_panel, "Demanda Promedio Diaria (d̄) [u/día]:", "200.0")
        self.entry_sigma_d = self._crear_campo(left_panel, "Desviación Estándar Diaria (σ_d) [u/día]:", "150.0")
        self.entry_LT = self._crear_campo(left_panel, "Tiempo de Entrega (Lead Time) [días]:", "4.0")
        
        # Nivel de Servicio Deseado (%) con presets
        ctk.CTkLabel(left_panel, text="Nivel de Servicio Deseado (SL):", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(6, 2))
        
        sl_slider_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        sl_slider_frame.pack(fill="x", padx=15, pady=(0, 2))
        
        self.lbl_sl_val = ctk.CTkLabel(sl_slider_frame, text="95.0%", font=Theme.font_body_bold(), text_color=Theme.SECONDARY)
        self.lbl_sl_val.pack(side="right")

        self.slider_sl = ctk.CTkSlider(
            sl_slider_frame,
            from_=80.0,
            to=99.9,
            number_of_steps=199,
            command=self._on_slider_sl_change
        )
        self.slider_sl.set(95.0)
        self.slider_sl.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Botones de presets rápidos
        preset_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        preset_frame.pack(fill="x", padx=15, pady=(0, 6))
        for p in [90.0, 95.0, 98.0, 99.0]:
            ctk.CTkButton(
                preset_frame,
                text=f"{p:g}%",
                font=Theme.font_small(),
                width=45,
                height=22,
                fg_color=Theme.BG_INPUT,
                hover_color=Theme.BG_INPUT_HOVER,
                command=lambda val=p: self._set_sl_preset(val)
            ).pack(side="left", padx=2)

        # Parámetros de Costo
        self.entry_S = self._crear_campo(left_panel, "Costo por Pedido (S) [$]:", "20.0")
        self.entry_C = self._crear_campo(left_panel, "Costo Unitario de Compra (C) [$]:", "10.0")
        self.entry_i = self._crear_campo(left_panel, "Tasa Almacenamiento (i) [%]:", "20.0")
        self.entry_dias = self._crear_campo(left_panel, "Días Laborales al Año:", "250")

        # Botones de Acción
        btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(15, 10))

        btn_calc = ctk.CTkButton(
            btn_frame,
            text="⚡ Calcular Sistema Probabilístico",
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.calcular
        )
        btn_calc.pack(fill="x", pady=(0, 6))

        btn_sim = ctk.CTkButton(
            btn_frame,
            text="🎲 Re-Simular Monte Carlo",
            font=Theme.font_body(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.SECONDARY,
            hover_color=Theme.BG_INPUT_HOVER,
            text_color=Theme.SECONDARY,
            command=self._ejecutar_nueva_simulacion
        )
        btn_sim.pack(fill="x", pady=(0, 6))

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

        # --- PANEL DERECHO: Tarjetas Métricas, Gráficos y Texto ---
        right_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)

        # Tarjetas Métricas
        metrics_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 10))

        self.card_ss = MetricCard(metrics_frame, titulo="STOCK DE SEGURIDAD (SS)", valor_inicial="-", subtitulo="amortiguador de protección", color_acento=Theme.SECONDARY)
        self.card_ss.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.card_rop = MetricCard(metrics_frame, titulo="PUNTO DE REORDEN (ROP)", valor_inicial="-", subtitulo="disparador de pedidos", color_acento=Theme.ACCENT_YELLOW)
        self.card_rop.pack(side="left", fill="both", expand=True, padx=6)

        self.card_z = MetricCard(metrics_frame, titulo="FACTOR DE SEGURIDAD (Z)", valor_inicial="-", subtitulo="desviaciones estándar", color_acento=Theme.PRIMARY)
        self.card_z.pack(side="left", fill="both", expand=True, padx=6)

        self.card_q = MetricCard(metrics_frame, titulo="LOTE ECONÓMICO (EOQ / Q*)", valor_inicial="-", subtitulo="unidades por reabastecimiento", color_acento=Theme.SUCCESS)
        self.card_q.pack(side="left", fill="both", expand=True, padx=(6, 0))

        # Canvas de Gráficos (Campana de Gauss + Monte Carlo)
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
        self.txt_resultados.insert("1.0", "Presione '⚡ Calcular Sistema Probabilístico' para dimensionar el stock de seguridad y ver la simulación.")

    def _crear_campo(self, parent, label_text: str, valor_default: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label_text, font=Theme.font_body(), text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=15, pady=(4, 2))
        entry = ctk.CTkEntry(parent, font=Theme.font_body(), fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR)
        entry.insert(0, valor_default)
        entry.pack(fill="x", padx=15, pady=(0, 2))
        return entry

    def _on_slider_sl_change(self, value):
        self.lbl_sl_val.configure(text=f"{value:.1f}%")

    def _set_sl_preset(self, val: float):
        self.slider_sl.set(val)
        self.lbl_sl_val.configure(text=f"{val:.1f}%")

    def cargar_datos_completos(self, d_media: float, sigma_d: float, LT: float, SL: float, S: float, C: float, i: float, dias: int = 250):
        """Carga datos programáticamente desde el banco de ejercicios."""
        self.entry_d_media.delete(0, "end")
        self.entry_d_media.insert(0, str(d_media))
        self.entry_sigma_d.delete(0, "end")
        self.entry_sigma_d.insert(0, str(sigma_d))
        self.entry_LT.delete(0, "end")
        self.entry_LT.insert(0, str(LT))
        self._set_sl_preset(SL)
        self.entry_S.delete(0, "end")
        self.entry_S.insert(0, str(S))
        self.entry_C.delete(0, "end")
        self.entry_C.insert(0, str(C))
        self.entry_i.delete(0, "end")
        self.entry_i.insert(0, str(i * 100 if i <= 1.0 else i))
        self.entry_dias.delete(0, "end")
        self.entry_dias.insert(0, str(dias))

        self.calcular()

    def calcular(self):
        """Lee datos, instancia ModeloProbabilistico y genera los resultados."""
        try:
            d_m = float(self.entry_d_media.get())
            s_d = float(self.entry_sigma_d.get())
            lt = float(self.entry_LT.get())
            sl = float(self.slider_sl.get())
            s = float(self.entry_S.get())
            c = float(self.entry_C.get())
            i = float(self.entry_i.get()) / 100.0
            dias = int(self.entry_dias.get())

            # Instanciación POO
            self.modelo_actual = ModeloProbabilistico(
                demanda_promedio_diaria=d_m,
                desviacion_diaria=s_d,
                lead_time_dias=lt,
                nivel_servicio_pct=sl,
                costo_pedido=s,
                costo_unitario=c,
                tasa_almacenamiento=i,
                dias_laborales_anuales=dias
            )

            res = self.modelo_actual.calcular()

            # Actualizar tarjetas
            self.card_ss.actualizar(f"{res['stock_seguridad_SS']:,.2f} u.", f"Aprox. {round(res['stock_seguridad_SS'])} unidades")
            self.card_rop.actualizar(f"{res['punto_reorden_ROP']:,.2f} u.", f"μ_LT ({res['mu_LT']:.0f}) + SS ({res['stock_seguridad_SS']:.0f})")
            self.card_z.actualizar(f"Z = {res['factor_Z']:.3f}", f"Riesgo α = {res['riesgo_agotamiento_alpha']*100:.1f}%")
            self.card_q.actualizar(f"{res['Q_optimo_EOQ']:,.2f} u.", f"Aprox. {round(res['Q_optimo_EOQ'])} u/orden")

            # Actualizar Texto
            reporte = self.modelo_actual.generar_reporte_txt()
            self.txt_resultados.delete("1.0", "end")
            self.txt_resultados.insert("1.0", reporte)

            # Actualizar Gráficos
            fig = self.modelo_actual.generar_figura()
            self.plot_frame.mostrar_figura(fig)

        except ValueError as e:
            messagebox.showerror("Error en Parámetros", f"Verifique los números ingresados:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Ocurrió un error inesperado:\n{str(e)}")

    def _ejecutar_nueva_simulacion(self):
        """Ejecuta una nueva corrida de Monte Carlo con semilla aleatoria y actualiza el gráfico."""
        if self.modelo_actual is None or not self.modelo_actual.calculado:
            self.calcular()
            return
        
        # Volver a calcular con figura actualizada
        fig = self.modelo_actual.generar_figura()
        self.plot_frame.mostrar_figura(fig)

    def exportar_txt(self):
        """Exporta el reporte probabilístico a texto plano (.txt)."""
        if self.modelo_actual is None or not self.modelo_actual.calculado:
            messagebox.showwarning("Atención", "Primero debe calcular el modelo para exportar los resultados.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")],
            title="Guardar Reporte Probabilístico en Texto Plano"
        )
        if ruta:
            try:
                ExportadorServicio.exportar_modelo_a_txt(self.modelo_actual, ruta)
                messagebox.showinfo("Exportación Exitosa", f"El archivo fue guardado exitosamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo:\n{str(e)}")
