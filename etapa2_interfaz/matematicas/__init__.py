"""
Módulo de análisis matemático para PC Builder
Contiene clases y funciones para análisis de derivadas y optimización
"""

from .calculadora_pc import CalculadoraPC
from .modelos import *
from .graficos import GraficosMatematicos

__all__ = [
    'CalculadoraPC',
    'GraficosMatematicos',
    'ModeloTermico',
    'ModeloEficiencia',
    'ModeloVolumen',
    'ModeloFlujoAire'
]
