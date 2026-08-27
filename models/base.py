"""
Módulo base para modelos de Teoría de Inventarios.
Define la clase abstracta ModeloInventario que establece la interfaz común (POO).
Universidad José Antonio Páez - Métodos Cuantitativos
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import matplotlib.figure


class ModeloInventario(ABC):
    """
    Clase abstracta base para todos los modelos de inventario.
    Implementa el principio de abstracción y polimorfismo de POO.
    """

    def __init__(self, nombre: str, descripcion: str = ""):
        self.nombre = nombre
        self.descripcion = descripcion
        self.calculado = False
        self.resultados: Dict[str, Any] = {}

    @abstractmethod
    def calcular(self) -> Dict[str, Any]:
        """
        Ejecuta los cálculos matemáticos del modelo.
        Debe actualizar self.resultados y retornar el diccionario de resultados.
        """
        pass

    @abstractmethod
    def generar_reporte_txt(self) -> str:
        """
        Genera el reporte detallado en formato texto plano (.txt).
        Incluye supuestos, parámetros de entrada, fórmulas utilizadas,
        desarrollo paso a paso y resultados finales.
        """
        pass

    @abstractmethod
    def generar_figura(self) -> Optional[matplotlib.figure.Figure]:
        """
        Genera y retorna la figura de Matplotlib correspondiente a la visualización
        gráfica del modelo (curvas de costo, diente de sierra, campana normal, etc.).
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(nombre='{self.nombre}', calculado={self.calculado})>"
