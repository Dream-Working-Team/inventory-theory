"""
Vista de Formulario y Resumen Teórico Oficial de la Cátedra de Métodos Cuantitativos.
Universidad José Antonio Páez.
"""

import customtkinter as ctk
from ..theme import Theme


class VistaTeoria(ctk.CTkScrollableFrame):
    """
    Vista POO que presenta el compendio teórico completo, fórmulas oficiales,
    clasificación de costos y deducciones matemáticas de la Teoría de Inventarios.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._construir_interfaz()

    def _construir_interfaz(self):
        # 1. Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))

        ctk.CTkLabel(
            header_frame,
            text="📖 Formulario Oficial y Teoría de Inventarios",
            font=Theme.font_title(),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            header_frame,
            text="Universidad José Antonio Páez • Facultad de Ingeniería • Escuela de Ingeniería en Computación • Métodos Cuantitativos",
            font=Theme.font_body(),
            text_color=Theme.SECONDARY,
            anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # 2. Contenedor de Secciones Teóricas
        main_box = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        main_box.pack(fill="both", expand=True, padx=10, pady=5)

        # Texto enriquecido con todo el contenido del formulario y guías
        txt_teoria = ctk.CTkTextbox(
            main_box,
            font=Theme.font_code(),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_MAIN,
            height=580
        )
        txt_teoria.pack(fill="both", expand=True, padx=15, pady=15)

        guia_texto = """
======================================================================================
  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA
  ESCUELA DE INGENIERÍA EN COMPUTACIÓN
  CÁTEDRA: MÉTODOS CUANTITATIVOS / TEORÍA DE INVENTARIOS
  COMPENDIO TEÓRICO Y FORMULARIO OFICIAL
======================================================================================

1. CONCEPTOS FUNDAMENTALES DE LA TEORÍA DE INVENTARIOS
--------------------------------------------------------------------------------------
La teoría de inventarios es una rama de la Investigación Operativa encargada de
planificar y controlar los niveles de existencias requeridos para el funcionamiento
de una organización, respondiendo a dos interrogantes fundamentales:
  1. ¿Cuánto ordenar en cada ocasión? (Tamaño del lote, Q)
  2. ¿Cuándo colocar la orden de reabastecimiento? (Punto de Reorden, ROP / Frecuencia)

TIPOLOGÍA DE COSTOS EN INVENTARIOS:
• Costo de Adquisición (C): Precio unitario pagado por la compra del bien.
• Costo de Pedido / Emisión (S o K): Costo fijo en que se incurre cada vez que se emite
  una orden de compra (transporte, flete, trámites, preparación de máquinas).
• Costo de Almacenamiento / Mantenimiento (H o Ch): Costo unitario por conservar un
  artículo en almacén durante un año (capital inmovilizado, seguro, espacio, merma).
  Fórmula: H = i * C  (donde i es la tasa porcentual anual de conservación).
• Costo de Escasez / Faltante (π o Cs): Penalización por unidad no disponible para
  satisfacer la demanda inmediata.


2. MODELO DETERMINÍSTICO EOQ CLÁSICO (UN SOLO ARTÍCULO, DEMANDA CONSTANTE)
--------------------------------------------------------------------------------------
SUPUESTOS:
1. Demanda anual (D) conocida, constante y determinista.
2. Tiempo de entrega (Lead Time, LT) conocido y constante.
3. El reabastecimiento es instantáneo al llegar el lote Q.
4. No se permiten faltantes (escasez).
5. Costos unitarios de adquisición (C), orden (S) y mantenimiento (H) constantes.

ECUACIÓN DE COSTO TOTAL ANUAL:
   CT(Q) = (D * C) + (D / Q) * S + (Q / 2) * H
           [Compra]   [Pedidos]    [Almacenamiento]

DEDUCCIÓN DEL LOTE ECONÓMICO (Q*):
   Derivando respecto a Q e igualando a cero:
   dCT/dQ = - (D * S) / Q^2 + H / 2 = 0
   ==> Q* = sqrt( (2 * D * S) / H )

FÓRMULAS ASOCIADAS:
• Demanda Diaria Promedio (d):            d = D / Días_Laborales
• Punto de Reorden (ROP):                 ROP = d * LT
• Número de Pedidos al Año (N):           N = D / Q*
• Tiempo de Ciclo entre Pedidos (T):      T = Q* / d (días) = Q* / D (años)
• Inventario Promedio:                    I_prom = Q* / 2


3. MODELO CON QUIEBRE DE PRECIOS (DESCUENTOS POR VOLUMEN)
--------------------------------------------------------------------------------------
Cuando el proveedor ofrece rebajas de precio unitario C_k condicionadas a adquirir
un lote mínimo dentro de un intervalo [Q_min_k, Q_max_k]:

PROCEDIMIENTO DE RESOLUCIÓN:
1. Para cada tramo de descuento k:
   Calcular H_k = i * C_k
   Calcular EOQ_k = sqrt( (2 * D * S) / H_k )
2. Evaluar Factibilidad del tramo:
   • Si Q_min_k <= EOQ_k <= Q_max_k ==> Lote Factible: Q_k = EOQ_k
   • Si EOQ_k < Q_min_k            ==> Ajustar al punto de quiebre mínimo: Q_k = Q_min_k
   • Si EOQ_k > Q_max_k            ==> Tramo no factible (descartar).
3. Evaluar el Costo Total Anual para cada lote factible:
   CT(Q_k) = (D * C_k) + (D / Q_k) * S + (Q_k / 2) * H_k
4. Seleccionar el tramo que arroje el MENOR Costo Total Anual Global.


4. MODELO DE VARIOS ARTÍCULOS CON RESTRICCIONES (MÉTODO DE LAGRANGE)
--------------------------------------------------------------------------------------
Cuando se gestionan m productos que comparten un recurso escaso:
• Restricción de Espacio:      sum( a_i * Q_i ) <= A_disponible
• Restricción de Presupuesto:  sum( C_i * Q_i ) <= B_disponible

FUNCIÓN LAGRANGIANA:
   L(Q_1, ..., Q_m, λ) = sum[ (D_i * S_i)/Q_i + (Q_i * H_i)/2 ] + λ * [ sum(w_i * Q_i) - Límite ]

CONDICIONES DE OPTIMALIDAD DE PRIMER ORDEN:
   ∂L/∂Q_i = - (D_i * S_i) / Q_i^2 + H_i / 2 + λ * w_i = 0
   ==> Q_i*(λ) = sqrt( (2 * D_i * S_i) / (H_i + 2 * λ * w_i) )

ALGORITMO:
1. Calcular EOQ sin restricción (λ = 0). Si sum(w_i * Q_i0) <= Límite, la solución es óptima.
2. Si excede el límite, hallar λ* > 0 numéricamente tal que sum(w_i * Q_i*(λ*)) = Límite.


5. MODELO PROBABILÍSTICO (DEMANDA NORMAL, TIEMPO DE ENTREGA CONSTANTE)
--------------------------------------------------------------------------------------
SUPUESTOS:
1. Demanda diaria d sigue una distribución normal: d ~ N(d_media, σ_d^2).
2. Tiempo de entrega (LT) es constante.
3. Se opera bajo un sistema de revisión continua (Q, ROP).

PARÁMETROS EN EL TIEMPO DE ENTREGA:
• Demanda Media en Lead Time:             μ_LT = d_media * LT
• Desviación Estándar en Lead Time:       σ_LT = σ_d * sqrt(LT)

DIMENSIONAMIENTO DEL STOCK DE SEGURIDAD (SS):
• Nivel de Servicio (SL = 1 - α):        Probabilidad de no agotar stock durante el LT.
• Factor de Seguridad Normal (Z):        Z = Φ^(-1)(SL)
• Stock de Seguridad (Safety Stock):     SS = Z * σ_LT = Z * σ_d * sqrt(LT)
• Punto de Reorden Óptimo (ROP):         ROP = μ_LT + SS = (d_media * LT) + (Z * σ_LT)

COSTO TOTAL ANUAL ESPERADO:
   CT_esperado = (D * C) + (D / Q*) * S + (Q* / 2) * H + (SS * H)
======================================================================================
"""
        txt_teoria.insert("1.0", guia_texto.strip())
        txt_teoria.configure(state="disabled")
