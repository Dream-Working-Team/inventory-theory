"""
Pruebas Unitarias Automatizadas para los Modelos de Teoría de Inventarios.
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import unittest
import math
import os
import sys
import shutil

# Agregar raíz al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib
matplotlib.use('Agg')  # Modo no interactivo para pruebas unitarias

from models.eoq import ModeloEOQ
from models.quiebre_precios import ModeloQuiebrePrecios, TramoDescuento
from models.restricciones import ModeloRestricciones, ArticuloRestriccion
from models.probabilistico import ModeloProbabilistico
from services.exportador import ExportadorServicio
from services.banco_ejercicios import BancoEjerciciosService


class TestModelosInventario(unittest.TestCase):
    """Conjunto de pruebas para validar la exactitud matemática y funcionalidad POO."""

    def test_modelo_eoq_clasico(self):
        """Verifica los cálculos del EOQ básico y la igualdad de costos en el óptimo."""
        # D = 1000, S = 5, C = 20, H = 4
        modelo = ModeloEOQ(demanda_anual=1000, costo_pedido=5, costo_unitario=20, costo_almacenamiento=4)
        res = modelo.calcular()

        # Q* = sqrt(2 * 1000 * 5 / 4) = sqrt(2500) = 50
        self.assertAlmostEqual(res["Q_optimo"], 50.0, places=4)
        self.assertAlmostEqual(res["N_pedidos_anuales"], 20.0, places=4)
        self.assertAlmostEqual(res["costo_pedir_anual"], 100.0, places=4)
        self.assertAlmostEqual(res["costo_mantener_anual"], 100.0, places=4)
        self.assertAlmostEqual(res["costo_total_inventario"], 200.0, places=4)
        self.assertAlmostEqual(res["costo_compra_anual"], 20000.0, places=4)
        self.assertAlmostEqual(res["costo_total_anual"], 20200.0, places=4)

        reporte = modelo.generar_reporte_txt()
        self.assertIn("50.00 unidades", reporte)
        self.assertIn("REPORTE DE RESULTADOS", reporte)

    def test_ejercicio_ramon_oruro(self):
        """Verifica el ejercicio de Laptops en Oruro (Ramón) de la guía de la cátedra."""
        # D = 500 u/mes * 12 = 6000 u/año, S = 5000 Bs, H = 25 * 12 = 300 Bs/año
        modelo = ModeloEOQ(demanda_anual=6000, costo_pedido=5000, costo_unitario=3700, costo_almacenamiento=300)
        res = modelo.calcular()

        # Q* = sqrt(2 * 6000 * 5000 / 300) = sqrt(200000) ≈ 447.2136
        self.assertAlmostEqual(res["Q_optimo"], 447.2136, places=3)
        self.assertAlmostEqual(res["N_pedidos_anuales"], 13.416, places=2)

    def test_modelo_quiebre_precios(self):
        """Verifica la optimización por tramos de descuento de 5,000 unidades de la guía."""
        modelo = ModeloQuiebrePrecios(
            demanda_anual=5000,
            costo_pedido=49,
            tasa_almacenamiento=0.20,
            tramos=[
                TramoDescuento(q_min=0, q_max=999, precio_unitario=5.00),
                TramoDescuento(q_min=1000, q_max=1999, precio_unitario=4.80),
                TramoDescuento(q_min=2000, q_max=float('inf'), precio_unitario=4.75),
            ]
        )
        res = modelo.calcular()

        # Tramo 2 debe ser el óptimo con Q = 1000 y Costo Total = $24,725.00
        self.assertEqual(res["mejor_tramo_index"], 2)
        self.assertAlmostEqual(res["Q_optimo_global"], 1000.0, places=2)
        self.assertAlmostEqual(res["precio_unitario_optimo"], 4.80, places=2)
        self.assertAlmostEqual(res["costo_total_minimo"], 24725.0, places=2)

    def test_modelo_restricciones_lagrange(self):
        """Verifica la convergencia del multiplicador de Lagrange para restricción de espacio."""
        modelo = ModeloRestricciones(
            limite_recurso=220.0,
            tipo_restriccion="espacio",
            es_inventario_promedio=False,
            articulos=[
                ArticuloRestriccion(nombre="Prod A", demanda_anual=1000, costo_pedido=40, costo_unitario=20, costo_almacenamiento=4.0, espacio_unitario=1.0),
                ArticuloRestriccion(nombre="Prod B", demanda_anual=1500, costo_pedido=50, costo_unitario=35, costo_almacenamiento=7.0, espacio_unitario=1.5),
                ArticuloRestriccion(nombre="Prod C", demanda_anual=800, costo_pedido=60, costo_unitario=50, costo_almacenamiento=10.0, espacio_unitario=2.0),
            ]
        )
        res = modelo.calcular()

        self.assertTrue(res["restriccion_activa"])
        self.assertGreater(res["lambda_optimo"], 0.0)
        self.assertAlmostEqual(res["uso_total_recurso"], 220.0, delta=0.01)

    def test_modelo_probabilistico_desayunos(self):
        """Verifica el caso de estudio probabilístico de la distribuidora de desayunos."""
        modelo = ModeloProbabilistico(
            demanda_promedio_diaria=200,
            desviacion_diaria=150,
            lead_time_dias=4,
            nivel_servicio_pct=95.0,
            costo_pedido=20,
            costo_unitario=10,
            tasa_almacenamiento=0.20,
            dias_laborales_anuales=250
        )
        res = modelo.calcular()

        # D = 50,000, H = 2.0 -> Q* = 1000
        self.assertAlmostEqual(res["Q_optimo_EOQ"], 1000.0, places=2)
        self.assertAlmostEqual(res["mu_LT"], 800.0, places=2)
        self.assertAlmostEqual(res["sigma_LT"], 300.0, places=2)
        # Z para 95% = 1.644853...
        self.assertAlmostEqual(res["factor_Z"], 1.6449, places=3)
        # SS = 1.64485 * 300 ≈ 493.45 u
        self.assertAlmostEqual(res["stock_seguridad_SS"], 493.456, places=1)
        # ROP = 800 + 493.456 ≈ 1293.456 u
        self.assertAlmostEqual(res["punto_reorden_ROP"], 1293.456, places=1)

    def test_exportador_txt(self):
        """Verifica que el servicio de exportación escriba archivos .txt válidos."""
        modelo = ModeloEOQ(demanda_anual=1000, costo_pedido=10, costo_unitario=5, costo_almacenamiento=2)
        modelo.calcular()

        ruta_test = "test_reporte_output.txt"
        ruta_salida = ExportadorServicio.exportar_modelo_a_txt(modelo, ruta_test)

        self.assertTrue(os.path.exists(ruta_salida))
        with open(ruta_salida, "r", encoding="utf-8") as f:
            contenido = f.read()
            self.assertIn("REPORTE DE RESULTADOS", contenido)
            self.assertIn("UNIVERSIDAD JOSÉ ANTONIO PÁEZ", contenido)

        if os.path.exists(ruta_test):
            os.remove(ruta_test)

    def test_banco_ejercicios_integridad(self):
        """Verifica que todos los ejercicios del banco estén debidamente instanciados y calculados."""
        ejercicios = BancoEjerciciosService.obtener_todos_los_ejercicios()
        self.assertGreaterEqual(len(ejercicios), 7)
        for ej in ejercicios:
            self.assertTrue(ej.modelo_instanciado.calculado)
            self.assertIsNotNone(ej.modelo_instanciado.generar_reporte_txt())


if __name__ == "__main__":
    unittest.main()
