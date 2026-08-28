"""
Módulo de Resolución del Parcial II (15%) - Teoría de Inventarios.
Universidad José Antonio Páez - Facultad de Ingeniería - Escuela de Ingeniería en Computación.

Contiene las soluciones modulares y exportadores de los ejercicios de evaluación:
- Ejercicio 1: Modelo EOQ Clásico (Wilson)
- Ejercicio 2: Modelo con Quiebre de Precios (Descuentos por Volumen)
- Ejercicio 3: Modelo Multi-Artículo con Restricciones (Lagrange)
"""

from .ejercicio1_eoq import resolver_ejercicio1
from .ejercicio2_quiebre import resolver_ejercicio2
from .ejercicio3_restricciones import resolver_ejercicio3
from .resolver_parcial import resolver_parcial_completo

__all__ = [
    "resolver_ejercicio1",
    "resolver_ejercicio2",
    "resolver_ejercicio3",
    "resolver_parcial_completo",
]
