"""
Modelo de Quiebre de Precios / Descuentos por Cantidad (Volume Discounts).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
from .base import ModeloInventario


@dataclass
class TramoDescuento:
    """Representa un tramo o rango de volumen con su precio unitario."""
    q_min: float
    q_max: float  # float('inf') para el último tramo sin límite
    precio_unitario: float
    descuento_porcentaje: float = 0.0
    costo_almacenamiento_fijo: Optional[float] = None


@dataclass
class ResultadoTramo:
    """Almacena el resultado del cálculo para un tramo individual."""
    tramo_index: int
    q_min: float
    q_max: float
    precio_unitario: float
    descuento_pct: float
    H_tramo: float
    eoq_calculado: float
    q_ajustado: float
    es_factible: bool
    estado: str
    costo_compra: float
    costo_ordenar: float
    costo_mantener: float
    costo_total_anual: float


class ModeloQuiebrePrecios(ModeloInventario):
    """
    Implementación en POO del Modelo de Inventario con Quiebre de Precios.
    """

    def __init__(
        self,
        demanda_anual: float,
        costo_pedido: float,
        tasa_almacenamiento: Optional[float] = None,
        tramos: Optional[List[TramoDescuento]] = None,
        nombre: str = "Modelo con Descuentos por Volumen"
    ):
        super().__init__(nombre=nombre, descripcion="Modelo determinístico con descuentos de precio según el volumen del lote.")
        
        if demanda_anual <= 0:
            raise ValueError("La demanda anual (D) debe ser mayor a 0.")
        if costo_pedido <= 0:
            raise ValueError("El costo de pedido (S) debe ser mayor a 0.")

        self.D = float(demanda_anual)
        self.S = float(costo_pedido)
        self.i = float(tasa_almacenamiento) if tasa_almacenamiento is not None else 0.20
        self.tramos: List[TramoDescuento] = tramos if tramos is not None else []

    def agregar_tramo(self, q_min: float, q_max: float, precio: float, descuento_pct: float = 0.0, H_fijo: Optional[float] = None):
        """Agrega un nuevo tramo de descuento."""
        self.tramos.append(TramoDescuento(
            q_min=float(q_min),
            q_max=float(q_max),
            precio_unitario=float(precio),
            descuento_porcentaje=float(descuento_pct),
            costo_almacenamiento_fijo=H_fijo
        ))

    def calcular(self) -> Dict[str, Any]:
        """Calcula el lote óptimo global evaluando todos los tramos de descuento."""
        if not self.tramos:
            raise ValueError("Debe existir al menos un tramo de descuento para calcular.")

        # Ordenar tramos por q_min
        self.tramos_ordenados = sorted(self.tramos, key=lambda t: t.q_min)
        self.resultados_tramos: List[ResultadoTramo] = []

        mejor_costo = float('inf')
        mejor_tramo: Optional[ResultadoTramo] = None

        for idx, tramo in enumerate(self.tramos_ordenados, start=1):
            # 1. Determinar H para este tramo
            if tramo.costo_almacenamiento_fijo is not None and tramo.costo_almacenamiento_fijo > 0:
                H_k = tramo.costo_almacenamiento_fijo
            else:
                H_k = self.i * tramo.precio_unitario

            # 2. Calcular EOQ del tramo
            eoq_k = math.sqrt((2.0 * self.D * self.S) / H_k)

            # 3. Determinar factibilidad y ajuste
            if tramo.q_min <= eoq_k <= tramo.q_max:
                q_ajustado = eoq_k
                es_factible = True
                estado = "Factible (EOQ dentro del rango)"
            elif eoq_k < tramo.q_min:
                q_ajustado = tramo.q_min
                es_factible = True
                estado = f"Ajustado al punto de quiebre mínimo ({tramo.q_min:,.0f})"
            else:
                # EOQ > q_max: no conviene quedarse corto
                q_ajustado = tramo.q_max
                es_factible = False
                estado = "No Factible (EOQ excede límite superior)"

            # 4. Calcular Costos
            costo_compra = self.D * tramo.precio_unitario
            costo_ordenar = (self.D / q_ajustado) * self.S
            costo_mantener = (q_ajustado / 2.0) * H_k
            costo_total = costo_compra + costo_ordenar + costo_mantener

            res = ResultadoTramo(
                tramo_index=idx,
                q_min=tramo.q_min,
                q_max=tramo.q_max,
                precio_unitario=tramo.precio_unitario,
                descuento_pct=tramo.descuento_porcentaje,
                H_tramo=H_k,
                eoq_calculado=eoq_k,
                q_ajustado=q_ajustado,
                es_factible=es_factible,
                estado=estado,
                costo_compra=costo_compra,
                costo_ordenar=costo_ordenar,
                costo_mantener=costo_mantener,
                costo_total_anual=costo_total
            )
            self.resultados_tramos.append(res)

            if es_factible and costo_total < mejor_costo:
                mejor_costo = costo_total
                mejor_tramo = res

        self.mejor_tramo = mejor_tramo
        # Ahorro comparado con tramo 1
        tramo_base = self.resultados_tramos[0]
        self.ahorro_anual = tramo_base.costo_total_anual - mejor_costo if mejor_tramo else 0.0

        self.resultados = {
            "tramos_analizados": self.resultados_tramos,
            "mejor_tramo_index": mejor_tramo.tramo_index if mejor_tramo else 1,
            "Q_optimo_global": mejor_tramo.q_ajustado if mejor_tramo else 0.0,
            "precio_unitario_optimo": mejor_tramo.precio_unitario if mejor_tramo else 0.0,
            "costo_total_minimo": mejor_costo,
            "ahorro_anual_respecto_base": self.ahorro_anual,
        }
        self.calculado = True
        return self.resultados

    def generar_reporte_txt(self) -> str:
        """Genera el reporte detallado en texto plano (.txt)."""
        if not self.calculado:
            self.calcular()

        lineas = [
            "=" * 82,
            "  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA",
            "  CÁTEDRA: MÉTODOS CUANTITATIVOS / TEORÍA DE INVENTARIOS",
            "  REPORTE: MODELO DETERMINÍSTICO CON QUIEBRE DE PRECIOS (DESCUENTOS)",
            "=" * 82,
            "",
            "1. PARÁMETROS GENERALES:",
            f"   • Demanda Anual (D):                 {self.D:,.2f} unidades/año",
            f"   • Costo por Pedido (S):              ${self.S:,.2f}",
            f"   • Tasa Anual de Almacenamiento (i):  {self.i * 100:.2f}%",
            "",
            "2. TABLA DE TRAMOS DE DESCUENTO CONFIGURADOS:",
            f"   {'Tramo':<8}{'Rango Unidades':<22}{'Precio ($)':<14}{'Desc. (%)':<12}{'H ($/u/año)':<12}",
            "   " + "-" * 70,
        ]
        for idx, t in enumerate(self.tramos_ordenados, start=1):
            rango_str = f"{t.q_min:,.0f} a {t.q_max:,.0f}" if t.q_max != float('inf') else f"{t.q_min:,.0f} o más"
            h_val = t.costo_almacenamiento_fijo if t.costo_almacenamiento_fijo else self.i * t.precio_unitario
            lineas.append(f"   {idx:<8}{rango_str:<22}${t.precio_unitario:<13.2f}{t.descuento_porcentaje:<12.1f}%${h_val:<11.2f}")

        lineas.extend([
            "",
            "3. ANÁLISIS DE FACTIBILIDAD Y EVALUACIÓN DE COSTOS POR TRAMO:",
            f"   {'Tr.':<5}{'EOQ Calc.':<12}{'Q Ajust.':<12}{'C.Compra':<14}{'C.Pedir':<12}{'C.Almacen':<12}{'Costo Total':<14}",
            "   " + "-" * 79,
        ])
        for r in self.resultados_tramos:
            marcador = " * ÓPTIMO" if self.mejor_tramo and r.tramo_index == self.mejor_tramo.tramo_index else ""
            lineas.append(
                f"   {r.tramo_index:<5}{r.eoq_calculado:<12.2f}{r.q_ajustado:<12.2f}${r.costo_compra:<13.2f}${r.costo_ordenar:<11.2f}${r.costo_mantener:<11.2f}${r.costo_total_anual:<13.2f}{marcador}"
            )

        lineas.extend([
            "",
            "4. CONCLUSIÓN Y DECISIÓN ÓPTIMA:",
            "=" * 82,
            f"   ▶ LOTE ÓPTIMO RECOMENDADO (Q*):      {self.mejor_tramo.q_ajustado:,.2f} unidades",
            f"   ▶ PRECIO UNITARIO APLICABLE:         ${self.mejor_tramo.precio_unitario:,.2f} por unidad",
            f"   ▶ TRAMO SELECCIONADO:                Tramo #{self.mejor_tramo.tramo_index} ({self.mejor_tramo.estado})",
            f"   ▶ COSTO TOTAL ANUAL MÍNIMO:          ${self.mejor_tramo.costo_total_anual:,.2f}",
        ])
        if self.ahorro_anual > 0:
            lineas.append(f"   ▶ AHORRO ANUAL POR DESCUENTO:        ${self.ahorro_anual:,.2f} (con respecto al Tramo 1)")
        lineas.extend([
            "=" * 82,
            "",
            "INTERPRETACIÓN EJECUTIVA:",
            f"Se debe emitir cada orden por {round(self.mejor_tramo.q_ajustado)} unidades para acceder al precio de",
            f"${self.mejor_tramo.precio_unitario:.2f}. Esto minimiza la suma del costo de adquisición, costo de pedidos",
            f"y costo de almacenamiento anual.",
            "=" * 82,
        ])
        return "\n".join(lineas)

    def generar_figura(self) -> matplotlib.figure.Figure:
        """
        Genera gráfico comparativo de curvas de costo total para los diferentes tramos
        con resaltado del rango válido y del punto óptimo global.
        """
        if not self.calculado:
            self.calcular()

        fig, ax = plt.subplots(figsize=(10, 4.5), dpi=100)
        fig.patch.set_facecolor('#1E222D')
        ax.set_facecolor('#181A20')
        ax.tick_params(colors='#C5C8D4', labelsize=8.5)
        for spine in ax.spines.values():
            spine.set_color('#2E3440')
        ax.grid(True, linestyle='--', alpha=0.25, color='#8892B0')

        colores = ['#48CAE4', '#00F5D4', '#FFBE0B', '#FF758F', '#9D4EDD']
        q_max_plot = max([r.q_ajustado for r in self.resultados_tramos]) * 1.8
        q_vals = np.linspace(10, q_max_plot, 500)

        for idx, res in enumerate(self.resultados_tramos):
            color = colores[idx % len(colores)]
            H_k = res.H_tramo
            P_k = res.precio_unitario

            # Curva total para este precio
            ct_vals = (self.D * P_k) + (self.D / q_vals) * self.S + (q_vals / 2.0) * H_k
            
            # Dibujar curva completa tenue
            ax.plot(q_vals, ct_vals, color=color, linestyle=':', alpha=0.35, lw=1.2)
            
            # Dibujar segmento válido resaltado
            q_valid_min = res.q_min
            q_valid_max = min(res.q_max, q_max_plot)
            mask = (q_vals >= q_valid_min) & (q_vals <= q_valid_max)
            if np.any(mask):
                label_tramo = f'Tramo {res.tramo_index} (${P_k:.2f}/u)'
                ax.plot(q_vals[mask], ct_vals[mask], color=color, lw=2.5, label=label_tramo)

            # Punto candidato del tramo
            ax.plot([res.q_ajustado], [res.costo_total_anual], marker='s', markersize=6, color=color, alpha=0.7)

        # Destacar óptimo global
        if self.mejor_tramo:
            ax.plot(
                [self.mejor_tramo.q_ajustado],
                [self.mejor_tramo.costo_total_anual],
                marker='*',
                markersize=14,
                color='#FFBE0B',
                zorder=10,
                label=f'Óptimo Global: Q*={self.mejor_tramo.q_ajustado:.0f}'
            )
            ax.annotate(
                f'ÓPTIMO: Q*={self.mejor_tramo.q_ajustado:.0f}\nCT = ${self.mejor_tramo.costo_total_anual:,.2f}',
                xy=(self.mejor_tramo.q_ajustado, self.mejor_tramo.costo_total_anual),
                xytext=(self.mejor_tramo.q_ajustado * 1.08, self.mejor_tramo.costo_total_anual * 1.05),
                arrowprops=dict(facecolor='#FFBE0B', shrink=0.08, width=1.5, headwidth=6),
                color='#FFBE0B',
                fontsize=8.5,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1E222D', edgecolor='#FFBE0B', alpha=0.9)
            )

        ax.set_title("Curvas de Costo Total Anual por Tramo de Descuento", color='#E6EDF3', fontsize=10.5, pad=10, fontweight='bold')
        ax.set_xlabel("Tamaño del Lote de Compra (Q)", color='#C5C8D4', fontsize=9)
        ax.set_ylabel("Costo Total Anual ($)", color='#C5C8D4', fontsize=9)
        ax.legend(facecolor='#1E222D', edgecolor='#2E3440', labelcolor='#C5C8D4', fontsize=8, loc='upper right')

        plt.tight_layout()
        return fig
