"""
Solucionador y Exportador Automatizado del Parcial II (15%).
Universidad José Antonio Páez - Facultad de Ingeniería - Escuela de Ingeniería en Computación.
Cátedra: Métodos Cuantitativos / Teoría de Inventarios.

Ejecuta y consolida los 3 ejercicios del Parcial II:
- Ejercicio 1: EOQ Clásico Wilson
- Ejercicio 2: Quiebre de Precios (Descuentos por Cantidad)
- Ejercicio 3: Multi-Artículo con Restricciones de Presupuesto y Capacidad (Lagrange)
"""

import sys
import os

# Asegurar importación de la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.exportador import ExportadorServicio
from .ejercicio1_eoq import resolver_ejercicio1
from .ejercicio2_quiebre import resolver_ejercicio2
from .ejercicio3_restricciones import resolver_ejercicio3


def resolver_parcial_completo():
    """Ejecuta todos los ejercicios del Parcial II y genera salidas en reportes/."""
    print("\n" + "=" * 84)
    print("  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA")
    print("  ESCUELA DE INGENIERÍA EN COMPUTACIÓN")
    print("  PARCIAL II (15%) - TEORÍA DE INVENTARIOS")
    print("  GENERADOR AUTOMATIZADO DE CÓDIGOS Y SALIDAS TXT")
    print("=" * 84 + "\n")

    # 1. Ejercicio 1
    print(">>> [1/3] EJECUTANDO EJERCICIO 1 (EOQ Clásico)...")
    mod1 = resolver_ejercicio1(exportar=True)
    print("")

    # 2. Ejercicio 2
    print(">>> [2/3] EJECUTANDO EJERCICIO 2 (Quiebre de Precios)...")
    mod2 = resolver_ejercicio2(exportar=True)
    print("")

    # 3. Ejercicio 3
    print(">>> [3/3] EJECUTANDO EJERCICIO 3 (Varios Artículos con Restricciones)...")
    mod3 = resolver_ejercicio3(exportar=True)
    print("")

    # 4. Generar informe consolidado del Parcial II
    ruta_consolidado = ExportadorServicio.normalizar_ruta("salida_parcial_completo.txt")
    ExportadorServicio.exportar_consolidados([mod1, mod2, mod3], ruta_consolidado)
    print(f"[OK] Informe Consolidado Completo exportado en: {ruta_consolidado}")

    print("\n" + "=" * 84)
    print("  ¡TODOS LOS EJERCICIOS HAN SIDO PROCESADOS Y EXPORTADOS CON ÉXITO!")
    print("  Archivos organizados en la carpeta 'reportes/':")
    print(f"   1. {ExportadorServicio.normalizar_ruta('salida_ejercicio1.txt')}")
    print(f"   2. {ExportadorServicio.normalizar_ruta('salida_ejercicio2.txt')}")
    print(f"   3. {ExportadorServicio.normalizar_ruta('salida_ejercicio3.txt')}")
    print(f"   4. {ruta_consolidado}")
    print("=" * 84 + "\n")


if __name__ == "__main__":
    resolver_parcial_completo()
