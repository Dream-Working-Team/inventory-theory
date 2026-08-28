"""
Parcial II - Ejercicio 1: Modelo Determinístico Clásico EOQ (Modelo de Wilson).
Universidad José Antonio Páez - Escuela de Ingeniería en Computación.
"""

import sys
import os

# Asegurar importación de la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.eoq import ModeloEOQ
from services.exportador import ExportadorServicio


def resolver_ejercicio1(exportar: bool = True) -> ModeloEOQ:
    """
    Resuelve el Ejercicio 1 del Parcial II:
    - Demanda Anual (D): 6,000 unidades
    - Costo por Pedido (S): $50.00
    - Costo Unitario (C): $20.00
    - Tasa de Almacenamiento (i): 20% anual (H = $4.00/u/año)
    - Lead Time (LT): 5 días
    - Días Laborales: 300 días/año
    """
    modelo = ModeloEOQ(
        demanda_anual=6000,
        costo_pedido=50,
        costo_unitario=20,
        tasa_almacenamiento=0.20,
        lead_time_dias=5,
        dias_laborales_anuales=300,
        nombre="Parcial II - Ejercicio 1: EOQ Clásico Wilson"
    )
    modelo.calcular()

    if exportar:
        ruta = ExportadorServicio.normalizar_ruta("salida_ejercicio1.txt")
        ExportadorServicio.exportar_modelo_a_txt(modelo, ruta)
        print(f"[OK] Ejercicio 1 exportado en: {ruta}")

    return modelo


if __name__ == "__main__":
    mod = resolver_ejercicio1(exportar=True)
    print(mod.generar_reporte_txt())
