"""
Pestaña de Optimización para PC Builder
Contiene aplicaciones de derivadas para optimización de gabinetes
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QComboBox, QGroupBox, QScrollArea, QTextEdit,
    QSplitter, QFrame, QMessageBox, QProgressBar, QTabWidget,
    QSlider, QSpinBox, QDoubleSpinBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

# Importar matplotlib para Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Importar módulos matemáticos
try:
    from matematicas.calculadora_pc import CalculadoraPC
    from matematicas.graficos import GraficosMatematicos
    from matematicas.modelos import crear_analizador_optimizacion
except ImportError as e:
    print(f"Error importando módulos matemáticos: {e}")
    # Fallback para desarrollo
    CalculadoraPC = None
    GraficosMatematicos = None


class OptimizacionTab(QWidget):
    """Pestaña de optimización de componentes"""
    
    # Señales
    optimizacion_completada = pyqtSignal(dict)
    
    def __init__(self, datos_componentes: Dict[str, Any] = None):
        super().__init__()
        self.datos_componentes = datos_componentes or {}
        self.calculadora = None
        self.graficos = None
        self.build_actual = None  # Build seleccionada de PC Builder
        self.configuracion_actual = {}
        
        # Configurar UI
        self.setup_ui()
        self.setup_styles()
        
        # Cargar datos iniciales
        self.cargar_datos_iniciales()
    
    def actualizar_configuracion(self, configuracion_build: Dict[str, Any]):
        """Actualiza la configuración de build desde la pestaña PC Builder"""
        self.build_actual = configuracion_build
        self.configuracion_actual = configuracion_build.copy()
        
        # Actualizar información de la build
        self.actualizar_info_build()
        
        # Actualizar análisis de optimización
        self.actualizar_analisis_optimizacion()
        
        # Mostrar mensaje en barra de estado si existe
        if hasattr(self, 'barra_estado'):
            self.barra_estado.setText(f"Build cargada: {len(configuracion_build)} componentes")
        
        print(f"✓ Configuración actualizada en OptimizacionTab: {len(configuracion_build)} componentes")
    
    def actualizar_info_build(self):
        """Actualiza la información de la build actual"""
        if not self.build_actual:
            return
        
        # Actualizar información en la UI
        info_build = []
        info_build.append("🖥️ Build para Optimización:")
        
        for tipo, componente in self.build_actual.items():
            if componente and isinstance(componente, dict):
                nombre = componente.get('nombre', 'Componente sin nombre')
                info_build.append(f"• {tipo.upper()}: {nombre}")
        
        # Actualizar labels informativos si existen
        if hasattr(self, 'info_build_label'):
            self.info_build_label.setText("\n".join(info_build))
    
    def actualizar_analisis_optimizacion(self):
        """Actualiza el análisis de optimización para la build actual"""
        if not self.build_actual:
            return
        
        try:
            # Calcular parámetros básicos de optimización
            parametros_optimizacion = self.calcular_parametros_optimizacion()
            
            # Actualizar gráficos si existen
            if hasattr(self, 'canvas_optimizacion'):
                self.actualizar_graficos_optimizacion(parametros_optimizacion)
            
            # Actualizar recomendaciones
            if hasattr(self, 'texto_recomendaciones'):
                recomendaciones = self.generar_recomendaciones(parametros_optimizacion)
                self.texto_recomendaciones.setText(recomendaciones)
                
        except Exception as e:
            print(f"Error actualizando análisis de optimización: {e}")
    
    def calcular_parametros_optimizacion(self) -> Dict[str, Any]:
        """Calcula parámetros básicos de optimización"""
        parametros = {
            'potencia_total': 0,
            'costo_total': 0,
            'rendimiento_estimado': 0,
            'eficiencia_termica': 0,
            'score_optimizacion': 0
        }
        
        if not self.build_actual:
            return parametros
        
        # Calcular potencia total
        for tipo, componente in self.build_actual.items():
            if componente and isinstance(componente, dict):
                # Extraer TDP si está disponible
                if 'tdp' in componente:
                    tdp = self.extraer_numero(componente['tdp'])
                    parametros['potencia_total'] += tdp
                
                # Extraer precio si está disponible
                if 'precio' in componente:
                    precio = self.extraer_numero(componente['precio'])
                    parametros['costo_total'] += precio
        
        # Calcular eficiencia térmica básica
        if parametros['potencia_total'] > 0:
            parametros['eficiencia_termica'] = 100 / parametros['potencia_total']
        
        # Score de optimización básico
        parametros['score_optimizacion'] = min(100, parametros['eficiencia_termica'] * 50)
        
        return parametros
    
    def generar_recomendaciones(self, parametros: Dict[str, Any]) -> str:
        """Genera recomendaciones de optimización"""
        recomendaciones = []
        recomendaciones.append("📈 Recomendaciones de Optimización:")
        recomendaciones.append("")
        
        # Recomendaciones basadas en potencia
        potencia = parametros.get('potencia_total', 0)
        if potencia > 500:
            recomendaciones.append("⚠️ Potencia alta detectada:")
            recomendaciones.append("  • Considere una PSU de mayor capacidad")
            recomendaciones.append("  • Verifique la refrigeración del case")
        elif potencia < 200:
            recomendaciones.append("✅ Potencia eficiente:")
            recomendaciones.append("  • Build de bajo consumo")
            recomendaciones.append("  • PSU de 400W-500W será suficiente")
        
        # Recomendaciones basadas en eficiencia
        eficiencia = parametros.get('eficiencia_termica', 0)
        if eficiencia < 0.1:
            recomendaciones.append("🔥 Considere mejorar la refrigeración")
        elif eficiencia > 0.3:
            recomendaciones.append("❄️ Excelente eficiencia térmica")
        
        # Score general
        score = parametros.get('score_optimizacion', 0)
        if score > 80:
            recomendaciones.append("🏆 Build bien optimizado")
        elif score > 60:
            recomendaciones.append("👍 Build decente, hay margen de mejora")
        else:
            recomendaciones.append("⚠️ Build necesita optimización")
        
        return "\n".join(recomendaciones)
    
    def actualizar_graficos_optimizacion(self, parametros: Dict[str, Any]):
        """Actualiza los gráficos de optimización"""
        if not hasattr(self, 'canvas_optimizacion'):
            return
        
        try:
            # Crear gráfico básico de barras con los parámetros
            import matplotlib.pyplot as plt
            
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            
            # Datos para el gráfico
            categorias = ['Potencia (W)', 'Eficiencia (%)', 'Score']
            valores = [
                parametros['potencia_total'],
                parametros['eficiencia_termica'] * 100,
                parametros['score_optimizacion']
            ]
            
            # Crear gráfico de barras
            bars = ax.bar(categorias, valores, color=['#e74c3c', '#3498db', '#2ecc71'])
            
            # Personalizar gráfico
            ax.set_title('Análisis de Optimización de Build', fontsize=14, fontweight='bold')
            ax.set_ylabel('Valor')
            ax.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{valor:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Actualizar canvas si es matplotlib
            if hasattr(self.canvas_optimizacion, 'figure'):
                self.canvas_optimizacion.figure.clear()
                self.canvas_optimizacion.figure = fig
                self.canvas_optimizacion.draw()
            
        except Exception as e:
            print(f"Error actualizando gráficos: {e}")
    
    def extraer_numero(self, valor_str) -> float:
        """Extrae número de una cadena con unidades"""
        if isinstance(valor_str, (int, float)):
            return float(valor_str)
        
        if isinstance(valor_str, str):
            import re
            match = re.search(r'(\d+\.?\d*)', valor_str.replace(',', '.'))
            if match:
                return float(match.group(1))
        
        return 0.0
    
    # ...existing methods...
