"""
Servicio de Exportación de Resultados a Archivos Planos (.txt).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import os
from datetime import datetime
from typing import List, Optional
from models.base import ModeloInventario


class ExportadorServicio:
    """
    Servicio POO encargado de generar, consolidar y guardar reportes
    en archivos de texto plano (.txt) para entrega académica o análisis posterior.
    """

    @staticmethod
    def exportar_modelo_a_txt(modelo: ModeloInventario, ruta_archivo: str) -> str:
        """
        Exporta el reporte de un modelo individual al archivo especificado.
        Retorna la ruta absoluta del archivo guardado.
        """
        reporte_contenido = modelo.generar_reporte_txt()
        
        # Asegurar directorio
        os.makedirs(os.path.dirname(os.path.abspath(ruta_archivo)), exist_ok=True)
        
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(reporte_contenido)
            f.write("\n\n" + "=" * 78 + "\n")
            f.write(f"  Fecha y Hora de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("  Sistema POO de Teoría de Inventarios - Universidad José Antonio Páez\n")
            f.write("=" * 78 + "\n")

        return os.path.abspath(ruta_archivo)

    @staticmethod
    def exportar_consolidados(modelos: List[ModeloInventario], ruta_archivo: str) -> str:
        """
        Exporta un informe consolidado con múltiples modelos calculados.
        """
        os.makedirs(os.path.dirname(os.path.abspath(ruta_archivo)), exist_ok=True)
        
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write("=" * 84 + "\n")
            f.write("  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA\n")
            f.write("  ESCUELA DE INGENIERÍA EN COMPUTACIÓN\n")
            f.write("  CÁTEDRA: MÉTODOS CUANTITATIVOS / TEORÍA DE INVENTARIOS\n")
            f.write("  INFORME CONSOLIDADO DE MODELOS DE INVENTARIO\n")
            f.write(f"  Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("=" * 84 + "\n\n")

            for idx, mod in enumerate(modelos, start=1):
                f.write(f"\n\n{'#' * 84}\n")
                f.write(f"# SECCIÓN {idx}: {mod.nombre.upper()}\n")
                f.write(f"{'#' * 84}\n\n")
                f.write(mod.generar_reporte_txt())
                f.write("\n\n")

            f.write("\n" + "=" * 84 + "\n")
            f.write("  FIN DEL INFORME CONSOLIDADO DE TEORÍA DE INVENTARIOS\n")
            f.write("=" * 84 + "\n")

        return os.path.abspath(ruta_archivo)
