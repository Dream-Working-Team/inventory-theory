"""
Modelo Probabilístico de Inventarios (Demanda Normal y Tiempo de Entrega Constante).
Sistema de Revisión Continua (Q, ROP) con Stock de Seguridad.
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import math
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
from .base import ModeloInventario


def normal_pdf_np(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Función de densidad de probabilidad normal para arrays numpy."""
    return (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def normal_ppf_puro(p: float) -> float:
    """
    Aproximación racional de alta precisión (Acklam) para la función cuantil
    de la distribución normal estándar (Φ^-1(p)). Precisión absoluta < 1.15e-9.
    """
    if p <= 0.0 or p >= 1.0:
        raise ValueError("La probabilidad p debe estar en el intervalo (0, 1).")
    
    # Coeficientes para la región central
    a = [-3.969683028665376e+01,  2.209460984245205e+02, -2.759285104469687e+02,
          1.383577518672690e+02, -3.066479804614020e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798598866e+02,
          6.680131188771972e+01, -1.328068155288572e+01]

    # Coeficientes para las colas
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549738039691901e+00,  4.374664141464968e+00,  2.938163982698783e+00]
    d = [ 7.784695709041462e-03,  3.224671290700398e-01,  2.445134137142996e+00,
          3.754408661907416e+00]

    p_low = 0.02425
    p_high = 1.0 - p_low

    if p < p_low:
        # Cola inferior
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)
    elif p <= p_high:
        # Región central
        q = p - 0.5
        r = q * q
        return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q / \
               (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1.0)
    else:
        # Cola superior
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)


class ModeloProbabilistico(ModeloInventario):
    """
    Implementación en POO del Modelo Probabilístico con Demanda Normal.
    Calcula Stock de Seguridad (SS), Punto de Reorden (ROP), Lote Económico (EOQ)
    y ejecuta simulaciones Monte Carlo para evaluar el nivel de servicio real.
    """

    def __init__(
        self,
        demanda_promedio_diaria: float,
        desviacion_diaria: float,
        lead_time_dias: float,
        nivel_servicio_pct: float,
        costo_pedido: float,
        costo_unitario: float = 0.0,
        tasa_almacenamiento: Optional[float] = None,
        costo_almacenamiento: Optional[float] = None,
        dias_laborales_anuales: int = 250,
        nombre: str = "Modelo Probabilístico (Q, ROP)"
    ):
        super().__init__(nombre=nombre, descripcion="Modelo probabilístico con demanda normal durante el tiempo de entrega.")
        
        if demanda_promedio_diaria <= 0:
            raise ValueError("La demanda promedio diaria debe ser mayor a 0.")
        if desviacion_diaria < 0:
            raise ValueError("La desviación estándar diaria no puede ser negativa.")
        if lead_time_dias <= 0:
            raise ValueError("El tiempo de entrega (Lead Time) debe ser mayor a 0.")
        if not (50.0 <= nivel_servicio_pct < 100.0):
            raise ValueError("El nivel de servicio debe estar entre 50% y 99.99%.")
        if costo_pedido <= 0:
            raise ValueError("El costo de pedido (S) debe ser mayor a 0.")

        self.d_media = float(demanda_promedio_diaria)
        self.sigma_d = float(desviacion_diaria)
        self.LT = float(lead_time_dias)
        self.SL_pct = float(nivel_servicio_pct)
        self.SL_decimal = self.SL_pct / 100.0
        self.S = float(costo_pedido)
        self.C = float(costo_unitario)
        self.i = float(tasa_almacenamiento) if tasa_almacenamiento is not None else None
        self.H_input = float(costo_almacenamiento) if costo_almacenamiento is not None else None
        self.dias_ano = int(dias_laborales_anuales)

        # Demanda anual estimada
        self.D = self.d_media * self.dias_ano

        # Determinar H
        if self.H_input is not None and self.H_input > 0:
            self.H = self.H_input
        elif self.i is not None and self.C > 0:
            self.H = self.i * self.C
        else:
            self.H = 1.0  # Valor base por defecto si no se ingresa

    def calcular(self) -> Dict[str, Any]:
        """Calcula los parámetros probabilísticos del sistema (Q, ROP, SS, Z)."""
        # 1. Demanda esperada y desviación estándar durante el Lead Time
        self.mu_LT = self.d_media * self.LT
        self.sigma_LT = self.sigma_d * math.sqrt(self.LT)

        # 2. Factor de seguridad Z (distribución normal estándar)
        self.Z = normal_ppf_puro(self.SL_decimal)

        # 3. Stock de Seguridad (Buffer / Safety Stock)
        self.SS = self.Z * self.sigma_LT

        # 4. Punto de Reorden (ROP)
        self.ROP = self.mu_LT + self.SS

        # 5. Cantidad Óptima de Pedido (EOQ)
        self.Q_opt = math.sqrt((2.0 * self.D * self.S) / self.H)

        # 6. Frecuencia y tiempos de ciclo
        self.N_pedidos = self.D / self.Q_opt
        self.T_dias = self.Q_opt / self.d_media

        # 7. Desglose de Costos Anuales
        self.costo_compra_anual = self.D * self.C
        self.costo_pedir_anual = (self.D / self.Q_opt) * self.S
        # El costo de mantenimiento incluye el inventario de ciclo (Q/2) + el stock de seguridad (SS)
        self.costo_mantener_ciclo = (self.Q_opt / 2.0) * self.H
        self.costo_mantener_ss = self.SS * self.H
        self.costo_mantener_total = self.costo_mantener_ciclo + self.costo_mantener_ss
        self.costo_total_anual = self.costo_compra_anual + self.costo_pedir_anual + self.costo_mantener_total

        # Probabilidad de agotamiento / riesgo de quiebre (alpha)
        self.alpha_riesgo = 1.0 - self.SL_decimal

        self.resultados = {
            "mu_LT": self.mu_LT,
            "sigma_LT": self.sigma_LT,
            "factor_Z": self.Z,
            "stock_seguridad_SS": self.SS,
            "punto_reorden_ROP": self.ROP,
            "Q_optimo_EOQ": self.Q_opt,
            "N_pedidos_anuales": self.N_pedidos,
            "T_dias_entre_pedidos": self.T_dias,
            "riesgo_agotamiento_alpha": self.alpha_riesgo,
            "costo_pedir_anual": self.costo_pedir_anual,
            "costo_mantener_total": self.costo_mantener_total,
            "costo_mantener_ss": self.costo_mantener_ss,
            "costo_total_anual": self.costo_total_anual,
        }
        self.calculado = True
        return self.resultados

    def simular_monte_carlo(self, dias_simulacion: int = 150, semilla: Optional[int] = 42) -> Dict[str, Any]:
        """
        Ejecuta una simulación estocástica día a día del comportamiento del inventario.
        Modela llegadas con lead time estocástico/fijo y evalúa roturas de stock.
        """
        if not self.calculado:
            self.calcular()

        rng = np.random.default_rng(semilla)
        
        inventario_actual = self.Q_opt + self.SS
        historial_inventario = []
        historial_demanda = []
        pedidos_en_camino = []  # Lista de (dia_llegada, cantidad)
        
        roturas_stock = 0
        unidades_faltantes = 0
        pedidos_realizados = 0

        for dia in range(dias_simulacion):
            # 1. Recibir pedidos que llegan hoy
            llegaron_hoy = [cant for (dia_ll, cant) in pedidos_en_camino if dia_ll == dia]
            for cant in llegaron_hoy:
                inventario_actual += cant
            pedidos_en_camino = [(dia_ll, cant) for (dia_ll, cant) in pedidos_en_camino if dia_ll > dia]

            # 2. Generar demanda aleatoria del día (distribución normal truncada en 0)
            demanda_dia = max(0.0, float(rng.normal(self.d_media, self.sigma_d)))
            historial_demanda.append(demanda_dia)

            # 3. Satisfacer demanda
            if inventario_actual >= demanda_dia:
                inventario_actual -= demanda_dia
            else:
                faltante = demanda_dia - inventario_actual
                unidades_faltantes += faltante
                roturas_stock += 1
                inventario_actual = 0.0

            historial_inventario.append(inventario_actual)

            # 4. Evaluar posición de inventario y colocar pedido si está bajo el ROP
            # Posición = inventario físico + pedidos en tránsito
            posicion = inventario_actual + sum([c for (_, c) in pedidos_en_camino])
            if posicion <= self.ROP and len(pedidos_en_camino) == 0:
                dia_entrega = dia + int(round(self.LT))
                pedidos_en_camino.append((dia_entrega, self.Q_opt))
                pedidos_realizados += 1

        nivel_servicio_observado = 1.0 - (roturas_stock / dias_simulacion)

        return {
            "dias": list(range(dias_simulacion)),
            "inventario": historial_inventario,
            "demanda": historial_demanda,
            "pedidos_realizados": pedidos_realizados,
            "roturas_stock_dias": roturas_stock,
            "unidades_faltantes_total": unidades_faltantes,
            "nivel_servicio_observado": nivel_servicio_observado * 100.0,
        }

    def generar_reporte_txt(self) -> str:
        """Genera el reporte detallado en texto plano (.txt)."""
        if not self.calculado:
            self.calcular()

        lineas = [
            "=" * 84,
            "  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA",
            "  CÁTEDRA: MÉTODOS CUANTITATIVOS / TEORÍA DE INVENTARIOS",
            "  REPORTE: MODELO PROBABILÍSTICO DE INVENTARIOS (SISTEMA CONTINUO Q, ROP)",
            "=" * 84,
            "",
            "1. PARÁMETROS DE LA DEMANDA Y OPERACIÓN:",
            f"   • Demanda Promedio Diaria (d_media): {self.d_media:,.2f} unidades/día",
            f"   • Desviación Estándar Diaria (σ_d):  {self.sigma_d:,.2f} unidades/día",
            f"   • Días Laborales Anuales:            {self.dias_ano} días",
            f"   • Demanda Promedio Anual (D):        {self.D:,.2f} unidades/año",
            f"   • Tiempo de Entrega (Lead Time, LT): {self.LT:.2f} días",
            f"   • Nivel de Servicio Deseado (SL):    {self.SL_pct:.2f}% ({self.SL_decimal:.4f})",
            f"   • Riesgo de Escasez Tolerado (α):    {self.alpha_riesgo * 100:.2f}%",
            f"   • Costo por Pedido (S o K):          ${self.S:,.2f}",
            f"   • Costo Unitario de Compra (C):      ${self.C:,.2f}",
            f"   • Costo de Mantenimiento Unit. (H):  ${self.H:,.2f} por unidad/año",
            "",
            "2. FÓRMULAS Y DEDUCCIÓN MATEMÁTICA:",
            "   • Demanda Media en Lead Time:        μ_LT = d_media * LT",
            "   • Desviación Estándar en Lead Time:  σ_LT = σ_d * sqrt(LT)",
            "   • Factor de Seguridad Normal (Z):    Z = Φ^(-1)(Nivel de Servicio)",
            "   • Stock de Seguridad (Safety Stock): SS = Z * σ_LT = Z * σ_d * sqrt(LT)",
            "   • Punto de Reorden (ROP):            ROP = μ_LT + SS = (d * LT) + (Z * σ_LT)",
            "   • Lote Económico de Pedido (EOQ):    Q* = sqrt( (2 * D * S) / H )",
            "   • Costo Total Anual Esperado:        CT = D*C + (D/Q*)*S + (Q*/2)*H + SS*H",
            "",
            "3. RESULTADOS ÓPTIMOS DEL SISTEMA PROBABILÍSTICO:",
            f"   - DEMANDA PROMEDIO EN LEAD TIME:     {self.mu_LT:,.2f} unidades",
            f"   - DESVIACIÓN ESTÁNDAR EN LEAD TIME:  {self.sigma_LT:,.2f} unidades",
            f"   - FACTOR DE SEGURIDAD (Z):           {self.Z:.4f} desviaciones estándar",
            f"   - STOCK DE SEGURIDAD (SS):           {self.SS:,.2f} unidades (aprox. {math.ceil(self.SS)} u.)",
            f"   - PUNTO DE REORDEN ÓPTIMO (ROP):     {self.ROP:,.2f} unidades (aprox. {round(self.ROP)} u.)",
            f"   - LOTE ECONÓMICO DE PEDIDO (Q*):     {self.Q_opt:,.2f} unidades (aprox. {round(self.Q_opt)} u.)",
            f"   - FRECUENCIA DE PEDIDOS ESTIMADA:    {self.N_pedidos:,.2f} pedidos/año",
            f"   - TIEMPO ESTIMADO ENTRE PEDIDOS:     {self.T_dias:,.2f} días de trabajo",
            "",
            "4. DESGLOSE DE COSTOS ANUALES:",
            f"   • Costo Anual de Compra:             ${self.costo_compra_anual:,.2f}",
            f"   • Costo Anual por Ordenar:           ${self.costo_pedir_anual:,.2f}",
            f"   • Costo Mantenimiento Ciclo (Q/2*H): ${self.costo_mantener_ciclo:,.2f}",
            f"   • Costo Mantener Stock Seg. (SS*H):  ${self.costo_mantener_ss:,.2f}",
            "-" * 84,
            f"   * COSTO TOTAL ANUAL ESPERADO:        ${self.costo_total_anual:,.2f}",
            "=" * 84,
            "",
            "POLÍTICA DE INVENTARIO (Q, ROP):",
            f"Colocar una orden de {round(self.Q_opt)} unidades cada vez que la posición del inventario",
            f"(físico + pedidos en tránsito) disminuya hasta alcanzar {round(self.ROP)} unidades.",
            f"Esto garantiza una protección del {self.SL_pct:.1f}% contra quiebres de stock durante el lead time,",
            f"manteniendo un amortiguador de seguridad de {math.ceil(self.SS)} unidades.",
            "=" * 84,
        ]
        return "\n".join(lineas)

    def generar_figura(self) -> matplotlib.figure.Figure:
        """
        Genera figura Matplotlib con dos paneles:
        1. Campana de Gauss durante el Lead Time (Área de Servicio vs Riesgo de Quiebre).
        2. Simulación temporal Monte Carlo estocástica con llegadas y ROP.
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

        # --- PANEL 1: Distribución Normal en Lead Time ---
        x_min = max(0.0, self.mu_LT - 4 * self.sigma_LT)
        x_max = self.mu_LT + 4 * self.sigma_LT
        x_vals = np.linspace(x_min, x_max, 400)
        y_vals = normal_pdf_np(x_vals, self.mu_LT, self.sigma_LT)

        ax1.plot(x_vals, y_vals, color='#48CAE4', lw=2.5, label='Demanda en Lead Time N(μ, σ²)')

        # Sombreado Nivel de Servicio (Demanda <= ROP)
        x_safe = x_vals[x_vals <= self.ROP]
        y_safe = normal_pdf_np(x_safe, self.mu_LT, self.sigma_LT)
        ax1.fill_between(x_safe, 0, y_safe, color='#00F5D4', alpha=0.35, label=f'Nivel de Servicio ({self.SL_pct:.1f}%)')

        # Sombreado Riesgo de Agotamiento (Demanda > ROP)
        x_risk = x_vals[x_vals >= self.ROP]
        y_risk = normal_pdf_np(x_risk, self.mu_LT, self.sigma_LT)
        ax1.fill_between(x_risk, 0, y_risk, color='#FF758F', alpha=0.55, label=f'Riesgo Quiebre α ({self.alpha_riesgo*100:.1f}%)')

        # Líneas clave
        ax1.axvline(x=self.mu_LT, color='#FFBE0B', linestyle='--', lw=1.8, label=f'μ_LT = {self.mu_LT:.1f}')
        ax1.axvline(x=self.ROP, color='#FF758F', linestyle='-', lw=2.0, label=f'ROP = {self.ROP:.1f}')

        ax1.set_title(f"Distribución en Lead Time (Z = {self.Z:.2f})", color='#E6EDF3', fontsize=10, pad=10, fontweight='bold')
        ax1.set_xlabel("Demanda Durante Lead Time (unidades)", color='#C5C8D4', fontsize=9)
        ax1.set_ylabel("Densidad de Probabilidad", color='#C5C8D4', fontsize=9)
        ax1.legend(facecolor='#1E222D', edgecolor='#2E3440', labelcolor='#C5C8D4', fontsize=7.8, loc='upper right')

        # --- PANEL 2: Simulación Monte Carlo ---
        sim_res = self.simular_monte_carlo(dias_simulacion=120)
        ax2.plot(sim_res["dias"], sim_res["inventario"], color='#38B000', lw=2.0, label='Inv. Simulado')
        ax2.axhline(y=self.ROP, color='#FF9F1C', linestyle='--', lw=1.6, label=f'ROP = {self.ROP:.0f}')
        ax2.axhline(y=self.SS, color='#9D4EDD', linestyle=':', lw=1.6, label=f'SS = {self.SS:.0f}')

        ax2.set_title(f"Simulación Monte Carlo (Servicio Real: {sim_res['nivel_servicio_observado']:.1f}%)", color='#E6EDF3', fontsize=10, pad=10, fontweight='bold')
        ax2.set_xlabel("Día de Operación", color='#C5C8D4', fontsize=9)
        ax2.set_ylabel("Unidades en Stock", color='#C5C8D4', fontsize=9)
        ax2.legend(facecolor='#1E222D', edgecolor='#2E3440', labelcolor='#C5C8D4', fontsize=8, loc='upper right')

        plt.tight_layout()
        return fig
