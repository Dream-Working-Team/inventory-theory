"""
Parcial II - Ejercicio 2: Modelo de Quiebre de Precios (Descuentos por Cantidad).
Universidad José Antonio Páez - Escuela de Ingeniería en Computación.

Enunciado:
Demanda anual D = 10,000 unidades, Precio base C = $10/u, Costo de orden S = $100,
Tasa anual de almacenamiento i = 25% anual.
Tramos de descuento:
- Tramo 1 [0 - 999]:     Desc. 0% -> Precio: $10.00
- Tramo 2 [1000 - 1999]: Desc. 3% -> Precio: $9.70
- Tramo 3 [2000 - 2999]: Desc. 5% -> Precio: $9.50
- Tramo 4 [3000 o más]:  Desc. 7% -> Precio: $9.30
"""

import sys
import os

# Asegurar importación de la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.quiebre_precios import ModeloQuiebrePrecios, TramoDescuento
from services.exportador import ExportadorServicio


def resolver_ejercicio2(exportar: bool = True) -> ModeloQuiebrePrecios:
    """Resuelve el Ejercicio 2 del Parcial II."""
    demanda_anual = 10000.0
    costo_pedido = 100.0
    tasa_almacenamiento = 0.25
    precio_base = 10.0

    tramos = [
        TramoDescuento(q_min=0, q_max=999, precio_unitario=precio_base * (1 - 0.00), descuento_porcentaje=0.0),
        TramoDescuento(q_min=1000, q_max=1999, precio_unitario=precio_base * (1 - 0.03), descuento_porcentaje=3.0),
        TramoDescuento(q_min=2000, q_max=2999, precio_unitario=precio_base * (1 - 0.05), descuento_porcentaje=5.0),
        TramoDescuento(q_min=3000, q_max=float('inf'), precio_unitario=precio_base * (1 - 0.07), descuento_porcentaje=7.0),
    ]

    modelo = ModeloQuiebrePrecios(
        demanda_anual=demanda_anual,
        costo_pedido=costo_pedido,
        tasa_almacenamiento=tasa_almacenamiento,
        tramos=tramos,
        nombre="Parcial II - Ejercicio 2: Modelo de Quiebre de Precios"
    )
    modelo.calcular()

    if exportar:
        ruta = ExportadorServicio.normalizar_ruta("salida_ejercicio2.txt")
        ExportadorServicio.exportar_modelo_a_txt(modelo, ruta)
        print(f"[OK] Ejercicio 2 exportado en: {ruta}")

    return modelo


if __name__ == "__main__":
    mod = resolver_ejercicio2(exportar=True)
    print(mod.generar_reporte_txt())
