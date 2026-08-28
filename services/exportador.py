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

    CARPETA_REPORTES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reportes"))

    @classmethod
    def asegurar_carpeta_reportes(cls) -> str:
        """Crea y retorna la ruta absoluta a la carpeta reportes/."""
        os.makedirs(cls.CARPETA_REPORTES, exist_ok=True)
        return cls.CARPETA_REPORTES

    @classmethod
    def normalizar_ruta(cls, ruta_archivo: str) -> str:
        """Si solo se proporciona el nombre del archivo, lo guarda dentro de reportes/."""
        if not os.path.isabs(ruta_archivo) and not os.path.dirname(ruta_archivo):
            return os.path.join(cls.asegurar_carpeta_reportes(), ruta_archivo)
        os.makedirs(os.path.dirname(os.path.abspath(ruta_archivo)), exist_ok=True)
        return os.path.abspath(ruta_archivo)

    @classmethod
    def exportar_modelo_a_txt(cls, modelo: ModeloInventario, ruta_archivo: str) -> str:
        """
        Exporta el reporte de un modelo individual al archivo especificado.
        Retorna la ruta absoluta del archivo guardado.
        """
        ruta_final = cls.normalizar_ruta(ruta_archivo)
        reporte_contenido = modelo.generar_reporte_txt()
        
        with open(ruta_final, "w", encoding="utf-8") as f:
            f.write(reporte_contenido)
            f.write("\n\n" + "=" * 78 + "\n")
            f.write(f"  Fecha y Hora de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("  Sistema POO de Teoría de Inventarios - Universidad José Antonio Páez\n")
            f.write("=" * 78 + "\n")

        return ruta_final

    @classmethod
    def exportar_consolidados(cls, modelos: List[ModeloInventario], ruta_archivo: str) -> str:
        """
        Exporta un informe consolidado con múltiples modelos calculados.
        """
        ruta_final = cls.normalizar_ruta(ruta_archivo)
        
        with open(ruta_final, "w", encoding="utf-8") as f:
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
