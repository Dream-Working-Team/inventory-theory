"""
Modelo Determinístico de Varios Artículos con Restricciones (Multi-Item Inventory with Constraints).
Resolución mediante Multiplicadores de Lagrange.
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
class ArticuloRestriccion:
    """Representa un producto individual dentro del inventario múltiple."""
    nombre: str
    demanda_anual: float        # D_i
    costo_pedido: float         # S_i
    costo_unitario: float       # C_i
    costo_almacenamiento: float # H_i
    espacio_unitario: float = 1.0  # a_i (m2, m3 o factor)


@dataclass
class ResultadoArticulo:
    """Resultado del cálculo para un artículo individual."""
    nombre: str
    D: float
    S: float
    C: float
    H: float
    espacio_u: float
    q_sin_restriccion: float
    q_con_restriccion: float
    costo_sin_restriccion: float
    costo_con_restriccion: float
    uso_recurso_sin: float
    uso_recurso_con: float


class ModeloRestricciones(ModeloInventario):
    """
    Implementación en POO del Modelo de Varios Artículos con Restricciones de Recursos.
    Utiliza el método analítico de Multiplicadores de Lagrange.
    """

    def __init__(
        self,
        limite_recurso: float,
        tipo_restriccion: str = "espacio",  # "espacio" o "presupuesto"
        es_inventario_promedio: bool = False,
        articulos: Optional[List[ArticuloRestriccion]] = None,
        nombre: str = "Modelo Multi-Producto con Restricciones"
    ):
        super().__init__(nombre=nombre, descripcion="Modelo determinístico de múltiples productos sujetos a restricción de espacio o capital.")
        
        if limite_recurso <= 0:
            raise ValueError("El límite del recurso disponible debe ser mayor a 0.")

        self.limite_recurso = float(limite_recurso)
        self.tipo_restriccion = tipo_restriccion.lower()
        self.es_promedio = es_inventario_promedio
        self.articulos: List[ArticuloRestriccion] = articulos if articulos is not None else []

    def agregar_articulo(self, nombre: str, D: float, S: float, C: float, H: Optional[float] = None, i: Optional[float] = None, espacio: float = 1.0):
        """Agrega un artículo al conjunto."""
        if H is None or H <= 0:
            if i is not None and C > 0:
                H = i * C
            else:
                raise ValueError(f"Debe definirse H o tasa i para el artículo {nombre}.")
        
        self.articulos.append(ArticuloRestriccion(
            nombre=nombre,
            demanda_anual=float(D),
            costo_pedido=float(S),
            costo_unitario=float(C),
            costo_almacenamiento=float(H),
            espacio_unitario=float(espacio)
        ))

    def _coeficiente_recurso(self, art: ArticuloRestriccion) -> float:
        """Retorna el coeficiente w_i que consume cada unidad del artículo."""
        factor_promedio = 0.5 if self.es_promedio else 1.0
        if self.tipo_restriccion == "presupuesto":
            return art.costo_unitario * factor_promedio
        else:  # espacio
            return art.espacio_unitario * factor_promedio

    def _q_lambda(self, art: ArticuloRestriccion, lmbda: float) -> float:
        """Calcula Q_i*(lambda) para un valor dado del multiplicador de Lagrange."""
        w_i = self._coeficiente_recurso(art)
        # Denominador: H_i + 2 * lambda * w_i (o H_i + lambda * w_i según formulación)
        denom = art.costo_almacenamiento + 2.0 * lmbda * w_i
        if denom <= 0:
            return float('inf')
        return math.sqrt((2.0 * art.demanda_anual * art.costo_pedido) / denom)

    def _uso_total_recurso(self, lmbda: float) -> float:
        """Calcula el uso total del recurso con un lambda dado."""
        total = 0.0
        for art in self.articulos:
            q_i = self._q_lambda(art, lmbda)
            w_i = self._coeficiente_recurso(art)
            total += w_i * q_i
        return total

    def calcular(self) -> Dict[str, Any]:
        """Calcula las cantidades óptimas respetando la restricción de recursos."""
        if not self.articulos:
            raise ValueError("Debe registrar al menos un producto para calcular el modelo.")

        # 1. Caso no restringido (lambda = 0)
        uso_sin_restriccion = self._uso_total_recurso(lmbda=0.0)

        if uso_sin_restriccion <= self.limite_recurso:
            # La restricción no está activa
            self.lambda_opt = 0.0
            self.restriccion_activa = False
        else:
            # La restricción está activa -> Bisección para encontrar lambda*
            self.restriccion_activa = True
            low = 0.0
            high = 1e6
            
            # Buscar cota superior adecuada
            for _ in range(50):
                if self._uso_total_recurso(high) < self.limite_recurso:
                    break
                high *= 10.0

            # Bisección
            for _ in range(100):
                mid = (low + high) / 2.0
                uso_mid = self._uso_total_recurso(mid)
                if abs(uso_mid - self.limite_recurso) < 1e-5:
                    break
                if uso_mid > self.limite_recurso:
                    low = mid
                else:
                    high = mid
            self.lambda_opt = mid

        # 2. Desglose de resultados por artículo
        self.resultados_articulos: List[ResultadoArticulo] = []
        costo_total_sin = 0.0
        costo_total_con = 0.0
        uso_total_final = 0.0

        for art in self.articulos:
            q_sin = self._q_lambda(art, lmbda=0.0)
            q_con = self._q_lambda(art, lmbda=self.lambda_opt)
            
            w_i = self._coeficiente_recurso(art)
            uso_sin = w_i * q_sin
            uso_con = w_i * q_con
            
            c_sin = (art.demanda_anual / q_sin) * art.costo_pedido + (q_sin / 2.0) * art.costo_almacenamiento + art.demanda_anual * art.costo_unitario
            c_con = (art.demanda_anual / q_con) * art.costo_pedido + (q_con / 2.0) * art.costo_almacenamiento + art.demanda_anual * art.costo_unitario

            costo_total_sin += c_sin
            costo_total_con += c_con
            uso_total_final += uso_con

            self.resultados_articulos.append(ResultadoArticulo(
                nombre=art.nombre,
                D=art.demanda_anual,
                S=art.costo_pedido,
                C=art.costo_unitario,
                H=art.costo_almacenamiento,
                espacio_u=art.espacio_unitario,
                q_sin_restriccion=q_sin,
                q_con_restriccion=q_con,
                costo_sin_restriccion=c_sin,
                costo_con_restriccion=c_con,
                uso_recurso_sin=uso_sin,
                uso_recurso_con=uso_con
            ))

        self.costo_total_sin_restriccion = costo_total_sin
        self.costo_total_con_restriccion = costo_total_con
        self.uso_total_recurso_calc = uso_total_final
        self.sobrecosto_por_restriccion = costo_total_con - costo_total_sin

        self.resultados = {
            "lambda_optimo": self.lambda_opt,
            "restriccion_activa": self.restriccion_activa,
            "limite_recurso": self.limite_recurso,
            "uso_total_recurso": self.uso_total_recurso_calc,
            "uso_sin_restriccion": uso_sin_restriccion,
            "costo_total_sin_restriccion": self.costo_total_sin_restriccion,
            "costo_total_con_restriccion": self.costo_total_con_restriccion,
            "sobrecosto_restriccion": self.sobrecosto_por_restriccion,
            "articulos": self.resultados_articulos
        }
        self.calculado = True
        return self.resultados

    def generar_reporte_txt(self) -> str:
        """Genera el reporte detallado en texto plano (.txt)."""
        if not self.calculado:
            self.calcular()

        tipo_str = "Espacio de Almacenamiento (m² / m³)" if self.tipo_restriccion == "espacio" else "Presupuesto de Capital ($)"
        unidad_recurso = "m²" if self.tipo_restriccion == "espacio" else "$"

        lineas = [
            "=" * 84,
            "  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA",
            "  CÁTEDRA: MÉTODOS CUANTITATIVOS / TEORÍA DE INVENTARIOS",
            "  REPORTE: MODELO DE VARIOS ARTÍCULOS CON RESTRICCIÓN DE RECURSOS",
            "=" * 84,
            "",
            "1. ESPECIFICACIÓN DE LA RESTRICCIÓN:",
            f"   • Tipo de Recurso Limitante:         {tipo_str}",
            f"   • Límite Máximo Disponible:          {self.limite_recurso:,.2f} {unidad_recurso}",
            f"   • Base de Medición:                  {'Inventario Promedio (Q/2)' if self.es_promedio else 'Lote Máximo de Pedido (Q)'}",
            f"   • Estado de la Restricción:          {'ACTIVA (Recurso agotado al 100%)' if self.restriccion_activa else 'INACTIVA (Capacidad suficiente)'}",
            f"   • Multiplicador de Lagrange (λ*):    {self.lambda_opt:.6f}",
            "",
            "2. TABLA COMPARATIVA DE RESULTADOS POR ARTÍCULO:",
            f"   {'Producto':<16}{'D (anual)':<12}{'EOQ (Sin Rest)':<16}{'Q* Ajustado':<16}{'Recurso Usado':<16}{'CT ($)':<12}",
            "   " + "-" * 80,
        ]
        for r in self.resultados_articulos:
            lineas.append(
                f"   {r.nombre:<16}{r.D:<12.0f}{r.q_sin_restriccion:<16.2f}{r.q_con_restriccion:<16.2f}{r.uso_recurso_con:<16.2f}${r.costo_con_restriccion:<11.2f}"
            )

        lineas.extend([
            "   " + "-" * 80,
            f"   TOTALES:{'':<20}{'':<16}{'':<16}{self.uso_total_recurso_calc:<16.2f}${self.costo_total_con_restriccion:<11.2f}",
            "",
            "3. ANÁLISIS DE IMPACTO DE LA RESTRICCIÓN:",
            f"   • Uso de Recurso Sin Restricción:    {self.resultados['uso_sin_restriccion']:,.2f} {unidad_recurso}",
            f"   • Uso de Recurso Ajustado (Óptimo):  {self.uso_total_recurso_calc:,.2f} {unidad_recurso} (Capacidad: {self.limite_recurso:,.2f})",
            f"   • Costo Total Teórico Sin Límite:    ${self.costo_total_sin_restriccion:,.2f}",
            f"   • Costo Total Real con Restricción:  ${self.costo_total_con_restriccion:,.2f}",
            f"   • Sobrecosto por Limitación de Rec.: ${self.sobrecosto_por_restriccion:,.2f} anuales",
            "=" * 84,
            "",
            "INTERPRETACIÓN MATEMÁTICA (MÉTODO DE LAGRANGE):",
            "El multiplicador lambda* representa el costo marginal o 'precio sombra' del recurso escaso.",
            f"Cada unidad adicional de {unidad_recurso} de capacidad incrementaría el beneficio / reduciría el costo",
            f"en aproximadamente ${self.lambda_opt:.4f} anuales.",
            "=" * 84,
        ])
        return "\n".join(lineas)

    def generar_figura(self) -> matplotlib.figure.Figure:
        """
        Genera gráfico comparativo de barras entre cantidades sin restricción vs con restricción.
        """
        if not self.calculado:
            self.calcular()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=100)
        fig.patch.set_facecolor('#1E222D')
        for ax in (ax1, ax2):
            ax.set_facecolor('#181A20')
            ax.tick_params(colors='#C5C8D4', labelsize=8.5)
            for spine in ax.spines.values():
                spine.set_color('#2E3440')
            ax.grid(True, linestyle='--', alpha=0.25, color='#8892B0')

        nombres = [r.nombre for r in self.resultados_articulos]
        x = np.arange(len(nombres))
        width = 0.35

        q_sin = [r.q_sin_restriccion for r in self.resultados_articulos]
        q_con = [r.q_con_restriccion for r in self.resultados_articulos]

        # Panel 1: Comparativa de Tamaños de Lote
        ax1.bar(x - width/2, q_sin, width, label='Sin Restricción (EOQ)', color='#48CAE4', alpha=0.85)
        ax1.bar(x + width/2, q_con, width, label='Con Restricción (Lagrange)', color='#00F5D4', alpha=0.9)
        ax1.set_xticks(x)
        ax1.set_xticklabels(nombres, color='#C5C8D4', fontsize=8.5)
        ax1.set_title("Comparativa de Lotes de Pedido (Q)", color='#E6EDF3', fontsize=10, pad=10, fontweight='bold')
        ax1.set_ylabel("Unidades por Orden", color='#C5C8D4', fontsize=9)
        ax1.legend(facecolor='#1E222D', edgecolor='#2E3440', labelcolor='#C5C8D4', fontsize=8)

        # Panel 2: Uso del Recurso por Producto
        uso_con = [r.uso_recurso_con for r in self.resultados_articulos]
        ax2.bar(nombres, uso_con, color='#FFBE0B', alpha=0.85, width=0.5, label='Uso de Capacidad')
        ax2.axhline(y=self.limite_recurso / max(1, len(nombres)), color='#FF758F', linestyle='--', label='Promedio Asignado')
        ax2.set_title(f"Distribución del Recurso ({self.tipo_restriccion.capitalize()})", color='#E6EDF3', fontsize=10, pad=10, fontweight='bold')
        ax2.set_ylabel("Uso de Capacidad", color='#C5C8D4', fontsize=9)
        ax2.legend(facecolor='#1E222D', edgecolor='#2E3440', labelcolor='#C5C8D4', fontsize=8)

        plt.tight_layout()
        return fig
