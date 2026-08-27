"""
Modelo Determinístico de un Solo Artículo con Demanda Constante (EOQ / Modelo de Wilson).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import math
from typing import Dict, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
from .base import ModeloInventario


class ModeloEOQ(ModeloInventario):
    """
    Implementación en POO del Modelo Clásico de Cantidad Económica de Pedido (EOQ).
    """

    def __init__(
        self,
        demanda_anual: float,
        costo_pedido: float,
        costo_unitario: float = 0.0,
        tasa_almacenamiento: Optional[float] = None,
        costo_almacenamiento: Optional[float] = None,
        lead_time_dias: float = 0.0,
        dias_laborales_anuales: int = 250,
        nombre: str = "Modelo EOQ Clásico"
    ):
        super().__init__(nombre=nombre, descripcion="Modelo determinístico de un solo producto con demanda y tiempo de entrega constantes.")
        
        if demanda_anual <= 0:
            raise ValueError("La demanda anual (D) debe ser un valor positivo mayor a 0.")
        if costo_pedido <= 0:
            raise ValueError("El costo por pedido (S o K) debe ser mayor a 0.")
        
        self.D = float(demanda_anual)
        self.S = float(costo_pedido)
        self.C = float(costo_unitario)
        self.i = float(tasa_almacenamiento) if tasa_almacenamiento is not None else None
        self.H_input = float(costo_almacenamiento) if costo_almacenamiento is not None else None
        self.LT = float(lead_time_dias)
        self.dias_ano = int(dias_laborales_anuales)

        # Determinar H
        if self.H_input is not None and self.H_input > 0:
            self.H = self.H_input
        elif self.i is not None and self.C > 0:
            self.H = self.i * self.C
        else:
            raise ValueError("Debe especificarse el costo de almacenamiento directo (H) o la tasa (i) junto con el costo unitario (C).")

    def calcular(self) -> Dict[str, Any]:
        """Calcula todas las métricas del modelo EOQ."""
        # 1. Cantidad Óptima de Pedido (EOQ)
        self.Q_opt = math.sqrt((2.0 * self.D * self.S) / self.H)
        
        # 2. Número de pedidos por año
        self.N_pedidos = self.D / self.Q_opt
        
        # 3. Demanda diaria
        self.d_diaria = self.D / self.dias_ano if self.dias_ano > 0 else self.D / 365.0
        
        # 4. Tiempo entre pedidos
        self.T_anos = self.Q_opt / self.D
        self.T_dias = self.T_anos * self.dias_ano
        
        # 5. Punto de Reorden (ROP)
        demanda_en_lead_time = self.d_diaria * self.LT
        if demanda_en_lead_time > self.Q_opt:
            self.ROP = demanda_en_lead_time % self.Q_opt
            self.pedidos_en_transito = int(demanda_en_lead_time // self.Q_opt)
        else:
            self.ROP = demanda_en_lead_time
            self.pedidos_en_transito = 0
            
        # 6. Costos Anuales
        self.costo_compra_anual = self.D * self.C
        self.costo_pedir_anual = (self.D / self.Q_opt) * self.S
        self.costo_mantener_anual = (self.Q_opt / 2.0) * self.H
        self.costo_total_inventario = self.costo_pedir_anual + self.costo_mantener_anual
        self.costo_total_anual = self.costo_compra_anual + self.costo_total_inventario

        self.resultados = {
            "Q_optimo": self.Q_opt,
            "N_pedidos_anuales": self.N_pedidos,
            "T_dias_entre_pedidos": self.T_dias,
            "T_anos_entre_pedidos": self.T_anos,
            "demanda_diaria": self.d_diaria,
            "punto_reorden_ROP": self.ROP,
            "pedidos_en_transito": self.pedidos_en_transito,
            "costo_mantenimiento_unitario_H": self.H,
            "costo_compra_anual": self.costo_compra_anual,
            "costo_pedir_anual": self.costo_pedir_anual,
            "costo_mantener_anual": self.costo_mantener_anual,
            "costo_total_inventario": self.costo_total_inventario,
            "costo_total_anual": self.costo_total_anual,
        }
        self.calculado = True
        return self.resultados

    def generar_reporte_txt(self) -> str:
        """Genera el reporte detallado en texto plano (.txt)."""
        if not self.calculado:
            self.calcular()

        lineas = [
            "=" * 78,
            "  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA",
            "  CÁTEDRA: MÉTODOS CUANTITATIVOS / TEORÍA DE INVENTARIOS",
            "  REPORTE DE RESULTADOS: MODELO DETERMINÍSTICO EOQ CLÁSICO",
            "=" * 78,
            "",
            "1. PARÁMETROS DE ENTRADA:",
            f"   • Demanda Anual (D):                 {self.D:,.2f} unidades/año",
            f"   • Costo por Pedir / Ordenar (S o K): ${self.S:,.2f} por orden",
            f"   • Costo Unitario de Compra (C):      ${self.C:,.2f} por unidad",
        ]
        if self.i is not None:
            lineas.append(f"   • Tasa Anual de Almacenamiento (i):  {self.i * 100:.2f}% anual")
        lineas.extend([
            f"   • Costo de Mantenimiento Unit. (H):  ${self.H:,.4f} por unidad/año",
            f"   • Tiempo de Entrega (Lead Time, LT): {self.LT:.2f} días",
            f"   • Días Laborales por Año:            {self.dias_ano} días",
            "",
            "2. FÓRMULAS Y DEDUCCIÓN MATEMÁTICA:",
            "   • Cantidad Económica de Pedido:      Q* = sqrt( (2 * D * S) / H )",
            "   • Demanda Diaria Promedio:           d = D / Días_Año",
            "   • Punto de Reorden:                  ROP = d * LT",
            "   • Frecuencia Anual de Pedidos:       N = D / Q*",
            "   • Tiempo de Ciclo entre Pedidos:     T = Q* / d (días) = Q* / D (años)",
            "   • Costo Anual por Ordenar:           C_pedir = (D / Q*) * S",
            "   • Costo Anual de Almacenamiento:     C_almacenar = (Q* / 2) * H",
            "   • Costo Total del Inventario:        CT_inv = C_pedir + C_almacenar",
            "   • Costo Total Anual Global:          CT = D * C + C_pedir + C_almacenar",
            "",
            "3. RESULTADOS ÓPTIMOS CALCULADOS:",
            f"   ▶ LOTE ÓPTIMO DE PEDIDO (EOQ / Q*):  {self.Q_opt:,.2f} unidades (aprox. {round(self.Q_opt)} unidades)",
            f"   ▶ PUNTO DE REORDEN (ROP):            {self.ROP:,.2f} unidades",
            f"   ▶ NÚMERO DE PEDIDOS AL AÑO (N):      {self.N_pedidos:,.2f} pedidos/año",
            f"   ▶ TIEMPO ENTRE PEDIDOS (T):          {self.T_dias:,.2f} días ({self.T_anos * 12:,.2f} meses)",
            f"   ▶ DEMANDA DIARIA PROMEDIO (d):       {self.d_diaria:,.2f} unidades/día",
        ])
        if self.pedidos_en_transito > 0:
            lineas.append(f"   ▶ PEDIDOS PENDIENTES EN TRÁNSITO:    {self.pedidos_en_transito} órdenes en camino")
        lineas.extend([
            "",
            "4. DESGLOSE DE COSTOS ANUALES:",
            f"   • Costo Anual de Adquisición (D * C): ${self.costo_compra_anual:,.2f}",
            f"   • Costo Anual de Pedidos ((D/Q)*S):   ${self.costo_pedir_anual:,.2f}",
            f"   • Costo Anual de Mantenimiento:       ${self.costo_mantener_anual:,.2f}",
            f"   • Costo Total de Manejo de Inventario:${self.costo_total_inventario:,.2f}",
            "-" * 78,
            f"   ★ COSTO TOTAL ANUAL GLOBAL (CT):      ${self.costo_total_anual:,.2f}",
            "=" * 78,
            "",
            "POLÍTICA DE INVENTARIO RECOMENDADA:",
            f"Colocar una orden de compra por {round(self.Q_opt)} unidades cada vez que el nivel",
            f"de inventario en almacén descienda a {round(self.ROP)} unidades.",
            f"Se realizarán aproximadamente {self.N_pedidos:.1f} pedidos al año, separados por {self.T_dias:.1f} días laborables.",
            "=" * 78,
        ])
        return "\n".join(lineas)

    def generar_figura(self) -> matplotlib.figure.Figure:
        """
        Genera figura Matplotlib con dos paneles:
        1. Curvas de Costos (Orden, Almacenamiento, Total) con punto óptimo.
        2. Simulación temporal de nivel de inventario (Diente de Sierra).
        """
        if not self.calculado:
            self.calcular()

        # Estilo oscuro y limpio
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=100)
        fig.patch.set_facecolor('#1E222D')
        for ax in (ax1, ax2):
            ax.set_facecolor('#181A20')
            ax.tick_params(colors='#C5C8D4', labelsize=8.5)
            for spine in ax.spines.values():
                spine.set_color('#2E3440')
            ax.grid(True, linestyle='--', alpha=0.25, color='#8892B0')

        # --- PANEL 1: Curvas de Costo ---
        q_min = max(1.0, self.Q_opt * 0.2)
        q_max = self.Q_opt * 2.5
        q_vals = np.linspace(q_min, q_max, 400)
        
        c_pedir_vals = (self.D / q_vals) * self.S
        c_mantener_vals = (q_vals / 2.0) * self.H
        c_total_inv_vals = c_pedir_vals + c_mantener_vals

        ax1.plot(q_vals, c_pedir_vals, label='Costo de Ordenar (D/Q * S)', color='#FF758F', lw=2, linestyle=':')
        ax1.plot(q_vals, c_mantener_vals, label='Costo de Mantener (Q/2 * H)', color='#48CAE4', lw=2, linestyle='--')
        ax1.plot(q_vals, c_total_inv_vals, label='Costo Total de Inventario', color='#00F5D4', lw=2.5)

        # Punto óptimo
        ax1.axvline(x=self.Q_opt, color='#FFBE0B', linestyle='-.', alpha=0.8, label=f'Q* = {self.Q_opt:.1f}')
        ax1.plot([self.Q_opt], [self.costo_total_inventario], marker='o', markersize=8, color='#FFBE0B', zorder=5)
        ax1.annotate(
            f'Óptimo Q* = {self.Q_opt:.1f}\nCT = ${self.costo_total_inventario:,.2f}',
            xy=(self.Q_opt, self.costo_total_inventario),
            xytext=(self.Q_opt * 1.1, self.costo_total_inventario * 1.15),
            arrowprops=dict(facecolor='#FFBE0B', shrink=0.05, width=1, headwidth=6),
            color='#FFBE0B',
            fontsize=8.5,
            fontweight='bold'
        )

        ax1.set_title("Curvas de Costos de Inventario vs Lote (Q)", color='#E6EDF3', fontsize=10, pad=10, fontweight='bold')
        ax1.set_xlabel("Tamaño del Lote (Q)", color='#C5C8D4', fontsize=9)
        ax1.set_ylabel("Costo Anual ($)", color='#C5C8D4', fontsize=9)
        ax1.legend(facecolor='#1E222D', edgecolor='#2E3440', labelcolor='#C5C8D4', fontsize=8, loc='upper right')

        # --- PANEL 2: Diente de Sierra (Nivel de Inventario vs Tiempo) ---
        num_ciclos = 3
        t_ciclo = self.T_dias if self.T_dias > 0 else 30.0
        tiempo_total = num_ciclos * t_ciclo
        
        t_points = []
        inv_points = []
        for i in range(num_ciclos):
            t_start = i * t_ciclo
            t_end = (i + 1) * t_ciclo
            t_points.extend([t_start, t_end])
            inv_points.extend([self.Q_opt, 0])

        ax2.plot(t_points, inv_points, color='#38B000', lw=2.5, label='Nivel de Inventario')
        
        # Línea de ROP
        if self.ROP > 0:
            ax2.axhline(y=self.ROP, color='#FF9F1C', linestyle='--', lw=1.8, label=f'ROP = {self.ROP:.1f}')
        
        # Sombreado de inventario promedio
        ax2.axhline(y=self.Q_opt / 2.0, color='#9D4EDD', linestyle=':', lw=1.5, label=f'Inv. Promedio = {self.Q_opt/2:.1f}')
        ax2.fill_between(t_points, 0, inv_points, color='#38B000', alpha=0.12)

        ax2.set_title(f"Simulación Diente de Sierra ({num_ciclos} Ciclos)", color='#E6EDF3', fontsize=10, pad=10, fontweight='bold')
        ax2.set_xlabel("Tiempo (Días laborables)", color='#C5C8D4', fontsize=9)
        ax2.set_ylabel("Unidades en Existencia", color='#C5C8D4', fontsize=9)
        ax2.set_ylim(-5, self.Q_opt * 1.15)
        ax2.set_xlim(0, tiempo_total)
        ax2.legend(facecolor='#1E222D', edgecolor='#2E3440', labelcolor='#C5C8D4', fontsize=8, loc='upper right')

        plt.tight_layout()
        return fig
