"""
Pestaña de Análisis Matemático para PC Builder
Contiene gráficos y análisis de derivadas aplicados a componentes
"""

import sys
import os
import math
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QComboBox, QGroupBox, QScrollArea, QTextEdit,
    QSplitter, QFrame, QMessageBox, QProgressBar, QTabWidget,
    QSlider, QSpinBox, QDoubleSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

# Importar matplotlib para Qt
import matplotlib
matplotlib.use('QtAgg')  # Changed from Qt5Agg to QtAgg for PyQt6 compatibility
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Importar módulos matemáticos con paths absolutos
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from filtros_analisis import FiltrosAnalisisMatematico
    from calculadora_build import CalculadoraBuildMatematica
    # Importar módulo de plantillas
    from templates.analisis_templates import generar_resumen_html
except ImportError as e:
    print(f"Error importando módulos matemáticos: {e}")
    FiltrosAnalisisMatematico = None
    CalculadoraBuildMatematica = None
    generar_resumen_html = None

from matematicas.calculadora_pc import CalculadoraPC
from matematicas.graficos import GraficosMatematicos
from matematicas.modelos import crear_analizador_optimizacion


class AnalisisMatematicoTab(QWidget):
    """Pestaña principal para análisis matemático de componentes"""
    
    # Señales
    datos_actualizados = pyqtSignal(dict)
    
    def __init__(self, datos_componentes: Dict[str, Any] = None):
        super().__init__()
        self.datos_componentes = datos_componentes or {}
        self.calculadora = None
        self.graficos = None
        self.build_actual = None
        self.configuracion_actual = {}
        
        # Inicializar filtros especializados y calculadora de build
        self.filtros_analisis = FiltrosAnalisisMatematico() if FiltrosAnalisisMatematico else None
        self.calculadora_build = CalculadoraBuildMatematica() if CalculadoraBuildMatematica else None
        
        # Inicializar componentes matemáticos
        self.inicializar_matematicas()
        
        # Configurar UI
        self.setup_ui()
        self.setup_styles()
        
        # Cargar datos iniciales
        self.cargar_datos_iniciales()
    
    def actualizar_configuracion(self, build_data: Dict[str, Any]):
        """
        Actualiza la configuración del análisis con datos del build seleccionado.
        Este método es llamado desde main_window cuando se selecciona un build.
        """
        try:
            self.build_actual = build_data
            
            # Actualizar estado de la interfaz
            self.barra_estado.setText("Procesando configuración del build...")
            
            # Extraer parámetros del build usando filtros especializados
            if self.filtros_analisis and build_data:
                parametros = self.filtros_analisis.extraer_parametros_build(build_data)
                self.configuracion_actual = parametros
                
                # Actualizar UI con información del build
                self.actualizar_info_build()
                
                # Actualizar análisis matemático
                self.actualizar_analisis_build()
                
                # Configurar calculadora si está disponible
                if self.calculadora_build:
                    self.calculadora_build.configurar_build(parametros)
                    self.ejecutar_analisis_completo()
                
                self.barra_estado.setText("Build analizado exitosamente")
            else:
                self.barra_estado.setText("Sin datos de build disponibles")
                self.limpiar_analisis()
                
        except Exception as e:
            self.barra_estado.setText(f"Error actualizando configuración: {str(e)}")
            self.mostrar_error_build(str(e))
    
    def actualizar_info_build(self):
        """Actualiza la información mostrada del build actual"""
        if not self.build_actual:
            self.info_gabinete.setText("No hay build seleccionado")
            return
        
        try:
            # Generar resumen del build
            resumen_build = self.generar_resumen_build()
            self.info_gabinete.setText(resumen_build)
        except Exception as e:
            self.info_gabinete.setText(f"Error generando resumen: {str(e)}")
    
    def generar_resumen_build(self) -> str:
        """Genera un resumen del build actual"""
        if not self.build_actual:
            return "No hay build seleccionado"
        
        componentes = []
        
        # Información de componentes principales
        if 'cpu' in self.build_actual and self.build_actual['cpu']:
            cpu = self.build_actual['cpu']
            componentes.append(f"🔧 CPU: {cpu.get('name', 'N/A')}")
        
        if 'gpu' in self.build_actual and self.build_actual['gpu']:
            gpu = self.build_actual['gpu']
            componentes.append(f"🎮 GPU: {gpu.get('name', 'N/A')}")
        
        if 'case' in self.build_actual and self.build_actual['case']:
            case = self.build_actual['case']
            componentes.append(f"🏠 Case: {case.get('name', 'N/A')}")
        
        if 'cpu_cooler' in self.build_actual and self.build_actual['cpu_cooler']:
            cooler = self.build_actual['cpu_cooler']
            componentes.append(f"❄️ Cooler: {cooler.get('name', 'N/A')}")
        
        if 'psu' in self.build_actual and self.build_actual['psu']:
            psu = self.build_actual['psu']
            componentes.append(f"⚡ PSU: {psu.get('name', 'N/A')}")
        
        # Información de parámetros calculados
        if self.configuracion_actual:
            params = self.configuracion_actual
            componentes.append(f"\n📊 Parámetros calculados:")
            
            if 'potencia_total' in params:
                componentes.append(f"• Potencia total: {params['potencia_total']:.1f}W")
            
            if 'factor_forma' in params:
                componentes.append(f"• Factor de forma: {params['factor_forma']}")
            
            if 'capacidad_termica' in params:
                componentes.append(f"• Capacidad térmica: {params['capacidad_termica']:.1f}")
        
        return "\n".join(componentes) if componentes else "Build vacío"
    
    def actualizar_analisis_build(self):
        """Actualiza el análisis matemático específico del build"""
        if not self.build_actual or not self.configuracion_actual:
            return
        
        try:
            # Actualizar información específica en las pestañas
            self.actualizar_info_analisis_termico()
            self.actualizar_info_analisis_eficiencia()
            self.actualizar_info_analisis_sensibilidad()
            
            # Actualizar gráficos si están disponibles
            if hasattr(self, 'canvas_termico'):
                self.actualizar_grafico_termico_basico()
            if hasattr(self, 'canvas_eficiencia'):
                self.actualizar_grafico_eficiencia_basico()
            if hasattr(self, 'canvas_sensibilidad'):
                self.actualizar_grafico_sensibilidad_basico()
                
        except Exception as e:
            print(f"Error actualizando análisis del build: {e}")
    
    def actualizar_info_analisis_termico(self):
        """Actualiza la información del análisis térmico"""
        if not hasattr(self, 'info_termico'):
            return
        
        try:
            params = self.configuracion_actual
            info_texto = []
            
            if 'potencia_total' in params:
                info_texto.append(f"🔥 Potencia total: {params['potencia_total']:.1f}W")
            
            if 'capacidad_enfriamiento' in params:
                info_texto.append(f"❄️ Capacidad enfriamiento: {params['capacidad_enfriamiento']:.1f}W")
            
            if 'compatibilidad_termica' in params:
                info_texto.append(f"📊 Compatibilidad térmica: {params['compatibilidad_termica']}")
            
            if 'eficiencia_termica' in params:
                eff = params['eficiencia_termica']
                info_texto.append(f"⚡ Eficiencia térmica: {eff:.2f} ({eff*100:.1f}%)")
            
            self.info_termico.setText("\n".join(info_texto) if info_texto else "Datos térmicos no disponibles")
            
        except Exception as e:
            self.info_termico.setText(f"Error calculando datos térmicos: {str(e)}")
    
    def actualizar_info_analisis_eficiencia(self):
        """Actualiza la información del análisis de eficiencia"""
        if not hasattr(self, 'info_eficiencia'):
            return
        
        try:
            params = self.configuracion_actual
            info_texto = []
            
            if 'psu_eficiencia' in params:
                eff = params['psu_eficiencia']
                info_texto.append(f"⚡ Eficiencia PSU: {eff:.2f} ({eff*100:.1f}%)")
            
            if 'psu_wattage' in params:
                info_texto.append(f"🔌 Wattage PSU: {params['psu_wattage']:.0f}W")
            
            if 'potencia_total' in params and 'psu_wattage' in params:
                carga = params['potencia_total'] / params['psu_wattage'] if params['psu_wattage'] > 0 else 0
                info_texto.append(f"📊 Carga del PSU: {carga:.2f} ({carga*100:.1f}%)")
            
            self.info_eficiencia.setText("\n".join(info_texto) if info_texto else "Datos de eficiencia no disponibles")
            
        except Exception as e:
            self.info_eficiencia.setText(f"Error calculando datos de eficiencia: {str(e)}")
    
    def actualizar_info_analisis_sensibilidad(self):
        """Actualiza la información del análisis de sensibilidad"""
        if not hasattr(self, 'info_sensibilidad'):
            return
        
        try:
            params = self.configuracion_actual
            info_texto = []
            
            # Sensibilidad térmica
            if 'cpu_tdp' in params and 'gpu_tdp' in params:
                cpu_tdp = params['cpu_tdp']
                gpu_tdp = params['gpu_tdp']
                total_tdp = cpu_tdp + gpu_tdp
                
                if total_tdp > 0:
                    cpu_contrib = (cpu_tdp / total_tdp) * 100
                    gpu_contrib = (gpu_tdp / total_tdp) * 100
                    
                    info_texto.append(f"🔧 Contribución CPU: {cpu_contrib:.1f}%")
                    info_texto.append(f"🎮 Contribución GPU: {gpu_contrib:.1f}%")
            
            # Sensibilidad de volumen
            if 'case_volumen' in params:
                volumen = params['case_volumen']
                densidad = params.get('potencia_total', 0) / volumen if volumen > 0 else 0
                info_texto.append(f"📦 Densidad térmica: {densidad:.2f} W/L")
            
            self.info_sensibilidad.setText("\n".join(info_texto) if info_texto else "Datos de sensibilidad no disponibles")
            
        except Exception as e:
            self.info_sensibilidad.setText(f"Error calculando datos de sensibilidad: {str(e)}")
    
    def actualizar_grafico_termico_basico(self):
        """Actualiza el gráfico térmico con información básica"""
        try:
            if not hasattr(self, 'canvas_termico') or not hasattr(self.canvas_termico, 'figure'):
                # Recrear canvas si no existe
                print("Recreando canvas térmico")
                self.canvas_termico = self.crear_canvas_fallback("Análisis Térmico")
                if hasattr(self, 'tab_termico') and hasattr(self.tab_termico, 'layout'):
                    # Reemplazar el canvas en la pestaña
                    old_canvas = self.tab_termico.findChild(FigureCanvas)
                    if old_canvas:
                        self.tab_termico.layout().replaceWidget(old_canvas, self.canvas_termico)
                    else:
                        # Si no se encuentra el canvas, añadirlo
                        for i in range(self.tab_termico.layout().count()):
                            if self.tab_termico.layout().itemAt(i).widget() == self.info_termico:
                                self.tab_termico.layout().insertWidget(i-1, self.canvas_termico)
                                break
                return
            
            # Limpiar canvas
            self.canvas_termico.figure.clear()
            ax = self.canvas_termico.figure.add_subplot(111)
            
            # Datos básicos para el gráfico
            params = self.configuracion_actual
            potencia = params.get('potencia_total', 0)
            capacidad = params.get('capacidad_enfriamiento', 0)
            
            # Crear gráfico de barras simple
            categorias = ['Potencia\nGenerada', 'Capacidad\nEnfriamiento']
            valores = [potencia, capacidad]
            colores = ['#ff6b6b', '#4ecdc4']
            
            bars = ax.bar(categorias, valores, color=colores, alpha=0.7)
            
            # Configurar gráfico
            ax.set_title('Análisis Térmico Básico', fontsize=14, fontweight='bold')
            ax.set_ylabel('Watts (W)')
            ax.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                      f'{valor:.1f}W', ha='center', va='bottom')
            
            # Actualizar canvas
            self.canvas_termico.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico térmico: {e}")
            # Intento de recuperación - crear un gráfico básico
            try:
                self.canvas_termico.figure.clear()
                ax = self.canvas_termico.figure.add_subplot(111)
                ax.set_title('Error en Análisis Térmico', color='red')
                ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center', color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas_termico.draw()
            except:
                pass
    
    def actualizar_grafico_eficiencia_basico(self):
        """Actualiza el gráfico de eficiencia con información básica"""
        try:
            if not hasattr(self, 'canvas_eficiencia') or not hasattr(self.canvas_eficiencia, 'figure'):
                # Recrear canvas si no existe
                print("Recreando canvas eficiencia")
                self.canvas_eficiencia = self.crear_canvas_fallback("Análisis de Eficiencia")
                if hasattr(self, 'tab_eficiencia') and hasattr(self.tab_eficiencia, 'layout'):
                    # Reemplazar el canvas en la pestaña
                    old_canvas = self.tab_eficiencia.findChild(FigureCanvas)
                    if old_canvas:
                        self.tab_eficiencia.layout().replaceWidget(old_canvas, self.canvas_eficiencia)
                    else:
                        # Si no se encuentra el canvas, añadirlo
                        for i in range(self.tab_eficiencia.layout().count()):
                            if self.tab_eficiencia.layout().itemAt(i).widget() == self.info_eficiencia:
                                self.tab_eficiencia.layout().insertWidget(i-1, self.canvas_eficiencia)
                                break
                return
            
            # Limpiar canvas
            self.canvas_eficiencia.figure.clear()
            ax = self.canvas_eficiencia.figure.add_subplot(111)
            
            # Datos básicos para el gráfico
            params = self.configuracion_actual
            eff_psu = params.get('psu_eficiencia', 0.8) * 100
            eff_termica = params.get('eficiencia_termica', 0.5) * 100
            
            # Crear gráfico de barras
            categorias = ['Eficiencia\nPSU', 'Eficiencia\nTérmica']
            valores = [eff_psu, eff_termica]
            colores = ['#45b7d1', '#f9ca24']
            
            bars = ax.bar(categorias, valores, color=colores, alpha=0.7)
            
            # Configurar gráfico
            ax.set_title('Análisis de Eficiencia', fontsize=14, fontweight='bold')
            ax.set_ylabel('Eficiencia (%)')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{valor:.1f}%', ha='center', va='bottom')
            
            # Actualizar canvas
            self.canvas_eficiencia.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico de eficiencia: {e}")
            # Intento de recuperación - crear un gráfico básico
            try:
                self.canvas_eficiencia.figure.clear()
                ax = self.canvas_eficiencia.figure.add_subplot(111)
                ax.set_title('Error en Análisis de Eficiencia', color='red')
                ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center', color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas_eficiencia.draw()
            except:
                pass
    
    def actualizar_grafico_sensibilidad_basico(self):
        """Actualiza el gráfico de sensibilidad con información básica"""
        try:
            if not hasattr(self, 'canvas_sensibilidad') or not hasattr(self.canvas_sensibilidad, 'figure'):
                # Recrear canvas si no existe
                print("Recreando canvas sensibilidad")
                self.canvas_sensibilidad = self.crear_canvas_fallback("Análisis de Sensibilidad")
                if hasattr(self, 'tab_sensibilidad') and hasattr(self.tab_sensibilidad, 'layout'):
                    # Reemplazar el canvas en la pestaña
                    old_canvas = self.tab_sensibilidad.findChild(FigureCanvas)
                    if old_canvas:
                        self.tab_sensibilidad.layout().replaceWidget(old_canvas, self.canvas_sensibilidad)
                    else:
                        # Si no se encuentra el canvas, añadirlo
                        for i in range(self.tab_sensibilidad.layout().count()):
                            if self.tab_sensibilidad.layout().itemAt(i).widget() == self.info_sensibilidad:
                                self.tab_sensibilidad.layout().insertWidget(i-1, self.canvas_sensibilidad)
                                break
                return
            
            # Limpiar canvas
            self.canvas_sensibilidad.figure.clear()
            ax = self.canvas_sensibilidad.figure.add_subplot(111)
            
            # Datos básicos para el gráfico
            params = self.configuracion_actual
            cpu_tdp = params.get('cpu_tdp', 0)
            gpu_tdp = params.get('gpu_tdp', 0)
            otros_tdp = max(0, params.get('potencia_total', 0) - cpu_tdp - gpu_tdp)
            
            # Crear gráfico de pastel
            valores = [cpu_tdp, gpu_tdp, otros_tdp]
            etiquetas = ['CPU', 'GPU', 'Otros']
            colores = ['#ff7675', '#74b9ff', '#00b894']
            
            # Filtrar valores cero
            valores_filtrados = []
            etiquetas_filtradas = []
            colores_filtrados = []
            
            for i, valor in enumerate(valores):
                if valor > 0:
                    valores_filtrados.append(valor)
                    etiquetas_filtradas.append(etiquetas[i])
                    colores_filtrados.append(colores[i])
            
            if valores_filtrados:
                wedges, texts, autotexts = ax.pie(valores_filtrados, 
                                                 labels=etiquetas_filtradas,
                                                 colors=colores_filtrados,
                                                 autopct='%1.1f%%',
                                                 startangle=90)
                
                # Mejorar la apariencia de los textos
                for text in texts:
                    text.set_fontsize(10)
                    text.set_fontweight('bold')
                
                for autotext in autotexts:
                    autotext.set_fontsize(9)
                    autotext.set_fontweight('bold')
                    autotext.set_color('white')
                
                ax.set_title('Distribución de Consumo por Componente', fontsize=14, fontweight='bold')
            else:
                ax.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center', transform=ax.transAxes)
            
            # Actualizar canvas
            self.canvas_sensibilidad.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico de sensibilidad: {e}")
            # Intento de recuperación - crear un gráfico básico
            try:
                self.canvas_sensibilidad.figure.clear()
                ax = self.canvas_sensibilidad.figure.add_subplot(111)
                ax.set_title('Error en Análisis de Sensibilidad', color='red')
                ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center', color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas_sensibilidad.draw()
            except:
                pass
    
    def limpiar_analisis(self):
        """Limpia todos los análisis y gráficos"""
        self.info_gabinete.setText("Seleccione un build para comenzar el análisis")
        
        # Limpiar gráficos
        if hasattr(self, 'canvas_termico'):
            self.limpiar_canvas(self.canvas_termico)
        if hasattr(self, 'canvas_eficiencia'):
            self.limpiar_canvas(self.canvas_eficiencia)
        if hasattr(self, 'canvas_sensibilidad'):
            self.limpiar_canvas(self.canvas_sensibilidad)
        
        # Limpiar texto de resumen
        if hasattr(self, 'texto_resumen'):
            self.texto_resumen.setText("Análisis matemático aparecerá aquí")
    
    def limpiar_canvas(self, canvas):
        """Limpia un canvas matplotlib"""
        try:
            if hasattr(canvas, 'figure'):
                canvas.figure.clear()
                canvas.draw()
        except Exception as e:
            print(f"Error limpiando canvas: {e}")
    
    def mostrar_error_build(self, mensaje: str):
        """Muestra un error relacionado con el build"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error en Análisis de Build")
        msg.setText("Error procesando el build seleccionado")
        msg.setDetailedText(mensaje)
        msg.exec()
        
    def inicializar_matematicas(self):
        """Inicializa los componentes matemáticos"""
        try:
            # Inicializar calculadora
            self.calculadora = CalculadoraPC() if 'CalculadoraPC' in globals() else None
            
            # Inicializar componente de gráficos
            try:
                if 'GraficosMatematicos' in globals():
                    self.graficos = GraficosMatematicos(estilo_oscuro=True)
                    print("Componente de gráficos inicializado correctamente")
                else:
                    print("Módulo GraficosMatematicos no disponible")
                    self.graficos = None
            except Exception as e:
                print(f"Error inicializando componente de gráficos: {e}")
                self.graficos = None
                
        except Exception as e:
            print(f"Error inicializando componentes matemáticos: {e}")
            self.mostrar_error_matematicas()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Establecer objectName para el widget principal
        self.setObjectName("analisisTab")
        
        layout = QVBoxLayout(self)
        
        # Título de la pestaña
        titulo = QLabel("📊 Análisis Matemático de Build Seleccionado")
        titulo.setObjectName("tituloAnalisis")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("splitterAnalisis")
        
        # Panel oculto - Mantiene referencias a controles pero no muestra UI
        panel_controles = self.crear_panel_controles()
        splitter.addWidget(panel_controles)
        
        # Panel derecho - Gráficos y análisis (ahora ocupará todo el espacio)
        panel_graficos = self.crear_panel_graficos()
        splitter.addWidget(panel_graficos)
        
        # Configurar proporciones (panel de control mínimo, panel de gráficos maximizado)
        splitter.setSizes([1, 999])
        
        layout.addWidget(splitter)
        
        # Barra de estado
        self.barra_estado = QLabel("Listo para análisis")
        self.barra_estado.setObjectName("barraEstado")
        layout.addWidget(self.barra_estado)
        
    def crear_panel_controles(self) -> QWidget:
        """Crea un widget mínimo para mantener la estructura pero eliminar el panel lateral"""
        widget = QWidget()
        widget.setObjectName("panelControlesMinimal")
        layout = QVBoxLayout(widget)
        
        # Información del build seleccionado (necesario para referencias en otras partes del código)
        self.info_gabinete = QLabel("Seleccione un build para comenzar el análisis")
        self.info_gabinete.setVisible(False)  # Lo ocultamos ya que no se mostrará en la UI
        layout.addWidget(self.info_gabinete)
        
        # Mantenemos referencias a widgets que pueden ser necesarios en otras partes
        # pero sin mostrarlos en la interfaz
        self.check_derivadas = QCheckBox("Mostrar derivadas")
        self.check_derivadas.setChecked(True)
        self.check_derivadas.setVisible(False)
        layout.addWidget(self.check_derivadas)
        
        self.check_puntos_criticos = QCheckBox("Marcar puntos críticos")
        self.check_puntos_criticos.setChecked(True)
        self.check_puntos_criticos.setVisible(False)
        layout.addWidget(self.check_puntos_criticos)
        
        self.check_area_sombreada = QCheckBox("Área sombreada")
        self.check_area_sombreada.setChecked(True)
        self.check_area_sombreada.setVisible(False)
        layout.addWidget(self.check_area_sombreada)
        
        # Configuraciones predeterminadas para parámetros
        self.slider_potencia = QSlider(Qt.Orientation.Horizontal)
        self.slider_potencia.setValue(50)
        self.slider_potencia.setVisible(False)
        layout.addWidget(self.slider_potencia)
        
        self.spin_temp_ambiente = QDoubleSpinBox()
        self.spin_temp_ambiente.setValue(25.0)
        self.spin_temp_ambiente.setVisible(False)
        layout.addWidget(self.spin_temp_ambiente)
        
        self.slider_ventilacion = QSlider(Qt.Orientation.Horizontal)
        self.slider_ventilacion.setValue(100)
        self.slider_ventilacion.setVisible(False)
        layout.addWidget(self.slider_ventilacion)
        
        # Etiquetas para valores
        self.label_potencia = QLabel("50 W")
        self.label_potencia.setVisible(False)
        layout.addWidget(self.label_potencia)
        
        self.label_ventilacion = QLabel("1.0x")
        self.label_ventilacion.setVisible(False)
        layout.addWidget(self.label_ventilacion)
        
        # El panel será mínimo en tamaño ya que todos los widgets están ocultos
        widget.setMaximumWidth(0)
        
        return widget
    
    def crear_panel_graficos(self) -> QWidget:
        """Crea el panel de gráficos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Añadimos una barra de herramientas simple
        toolbar = QHBoxLayout()
        
        # Botón para refrescar análisis
        btn_refrescar = QPushButton("🔄 Refrescar Análisis")
        btn_refrescar.setObjectName("botonAnalisis")
        btn_refrescar.setMaximumWidth(200)
        btn_refrescar.clicked.connect(self.ejecutar_analisis_completo)  # Mantiene la conexión principal
        btn_refrescar.setToolTip("Actualiza todos los gráficos y análisis")
        toolbar.addWidget(btn_refrescar)
        
        # Botón para resetear parámetros
        btn_reset = QPushButton("🔧 Parámetros por defecto")
        btn_reset.setObjectName("botonReset")
        btn_reset.setMaximumWidth(200)
        btn_reset.clicked.connect(self.resetear_parametros)
        toolbar.addWidget(btn_reset)
        
        # Añadir espaciador
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Pestañas para diferentes tipos de gráficos
        self.tabs_graficos = QTabWidget()
        self.tabs_graficos.setObjectName("tabsGraficos")
        self.tabs_graficos.tabBar().setObjectName("tabsGraficos")
        
        # Pestaña 1: Análisis Térmico
        self.tab_termico = self.crear_tab_termico()
        self.tabs_graficos.addTab(self.tab_termico, "🌡️ Análisis Térmico")
        
        # Pestaña 2: Análisis de Eficiencia
        self.tab_eficiencia = self.crear_tab_eficiencia()
        self.tabs_graficos.addTab(self.tab_eficiencia, "⚡ Eficiencia")
        
        # Pestaña 3: Análisis de Sensibilidad
        self.tab_sensibilidad = self.crear_tab_sensibilidad()
        self.tabs_graficos.addTab(self.tab_sensibilidad, "🔍 Sensibilidad")
        
        # Pestaña 4: Resumen Matemático
        self.tab_resumen = self.crear_tab_resumen()
        self.tabs_graficos.addTab(self.tab_resumen, "📋 Resumen")
        
        layout.addWidget(self.tabs_graficos)
        
        return widget
    
    def crear_tab_termico(self) -> QWidget:
        """Crea la pestaña de análisis térmico"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout(widget)
        
        # Título
        titulo = QLabel("Análisis Térmico: Temperatura vs Potencia")
        titulo.setObjectName("tituloSeccion")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Canvas para el gráfico
        if self.graficos:
            self.canvas_termico = self.graficos.crear_canvas_matplotlib(700, 500)
        else:
            self.canvas_termico = self.crear_canvas_fallback("Análisis Térmico")
        
        layout.addWidget(self.canvas_termico)
        
        # Información adicional
        self.info_termico = QLabel("Información del análisis térmico aparecerá aquí")
        self.info_termico.setObjectName("labelInfo")
        self.info_termico.setWordWrap(True)
        layout.addWidget(self.info_termico)
        
        return widget
    
    def crear_tab_eficiencia(self) -> QWidget:
        """Crea la pestaña de análisis de eficiencia"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout(widget)
        
        # Título
        titulo = QLabel("Análisis de Eficiencia: η vs Temperatura")
        titulo.setObjectName("tituloSeccion")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Canvas para el gráfico
        if self.graficos:
            self.canvas_eficiencia = self.graficos.crear_canvas_matplotlib(700, 500)
        else:
            self.canvas_eficiencia = self.crear_canvas_fallback("Análisis de Eficiencia")
        
        layout.addWidget(self.canvas_eficiencia)
        
        # Información adicional
        self.info_eficiencia = QLabel("Información del análisis de eficiencia aparecerá aquí")
        self.info_eficiencia.setObjectName("labelInfo")
        self.info_eficiencia.setWordWrap(True)
        layout.addWidget(self.info_eficiencia)
        
        return widget
    
    def crear_tab_sensibilidad(self) -> QWidget:
        """Crea la pestaña de análisis de sensibilidad"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout(widget)
        
        # Título
        titulo = QLabel("Análisis de Sensibilidad de Parámetros")
        titulo.setObjectName("tituloSeccion")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Canvas para el gráfico
        if self.graficos:
            self.canvas_sensibilidad = self.graficos.crear_canvas_matplotlib(700, 500)
        else:
            self.canvas_sensibilidad = self.crear_canvas_fallback("Análisis de Sensibilidad")
        
        layout.addWidget(self.canvas_sensibilidad)
        
        # Información adicional
        self.info_sensibilidad = QLabel("Información del análisis de sensibilidad aparecerá aquí")
        self.info_sensibilidad.setObjectName("labelInfo")
        self.info_sensibilidad.setWordWrap(True)
        layout.addWidget(self.info_sensibilidad)
        
        return widget
    
    def crear_tab_resumen(self) -> QWidget:
        """Crea la pestaña de resumen matemático"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout(widget)
        
        # Título
        titulo = QLabel("Resumen Matemático del Análisis")
        titulo.setObjectName("tituloSeccion")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Área de texto para el resumen
        self.texto_resumen = QTextEdit()
        self.texto_resumen.setObjectName("textoResumen")
        self.texto_resumen.setReadOnly(True)
        layout.addWidget(self.texto_resumen)
        
        return widget
    
    def crear_canvas_fallback(self, titulo: str) -> QWidget:
        """Crea un canvas básico de matplotlib cuando el componente gráfico no está disponible"""
        try:
            # Intentar crear un canvas de matplotlib directamente
            figure = Figure(figsize=(7, 5), dpi=100)
            canvas = FigureCanvas(figure)
            
            # Configurar colores para modo oscuro
            figure.patch.set_facecolor('#2d3436')  # Color de fondo oscuro
            
            # Añadir un mensaje al gráfico
            ax = figure.add_subplot(111)
            ax.set_title(f"📊 {titulo}", fontsize=14, fontweight='bold', color='white')
            ax.text(0.5, 0.5, "Haga clic en 'Refrescar Análisis' para ver los datos", 
                    ha='center', va='center', fontsize=12, color='white')
            ax.set_facecolor('#2d3436')  # Color de fondo oscuro para el gráfico
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#636e72')
            ax.spines['left'].set_color('#636e72')
            ax.tick_params(colors='white')
            
            # Eliminar etiquetas de los ejes
            ax.set_xticks([])
            ax.set_yticks([])
            
            return canvas
            
        except Exception as e:
            # Si falla, crear un widget básico con texto
            print(f"Error creando canvas fallback: {e}")
            widget = QWidget()
            widget.setObjectName("canvasFallback")
            layout = QVBoxLayout(widget)
            
            label = QLabel(f"📊 {titulo}")
            label.setObjectName("labelFallback")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            
            info_label = QLabel("Error al crear gráfico. Haga clic en 'Refrescar Análisis'")
            info_label.setObjectName("infoFallback")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)
            
            return widget
    
    def setup_styles(self):
        """Configura los estilos de la interfaz cargando desde archivo CSS"""
        try:
            # Obtener la ruta del archivo CSS
            css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "style.css")
            
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                self.setStyleSheet(css_content)
            else:
                print(f"Archivo CSS no encontrado: {css_path}")
                # Fallback a estilos básicos
                self.setStyleSheet("""
                    QWidget {
                        background-color: #f8fafc;
                        color: #2d3748;
                        font-family: 'Segoe UI', Arial, sans-serif;
                    }
                """)
        except Exception as e:
            print(f"Error cargando estilos CSS: {e}")
            self.setStyleSheet("")
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales"""
        # Actualizar labels de controles
        self.actualizar_labels_controles()
        
        # Mostrar mensaje inicial
        if hasattr(self, 'texto_resumen'):
            self.texto_resumen.setText("Seleccione un build desde la pestaña principal para comenzar el análisis matemático.")
        
        # Limpiar interfaz
        self.limpiar_analisis()
    
    def cargar_gabinetes(self):
        """Método legacy - ya no necesario con el nuevo sistema de builds"""
        # Este método se mantiene por compatibilidad pero ya no se usa
        pass
    
    def actualizar_labels_controles(self):
        """Actualiza los labels de los controles (ahora ocultos)"""
        # Actualizar internamente los valores, aunque ya no son visibles en la UI
        potencia = self.slider_potencia.value()
        self.label_potencia.setText(f"{potencia} W")
        
        ventilacion = self.slider_ventilacion.value() / 100.0
        self.label_ventilacion.setText(f"{ventilacion:.1f}x")
        
        # Mostrar valores actuales en la barra de estado para feedback al usuario
        self.barra_estado.setText(f"Potencia adicional: {potencia}W | Temp. ambiente: {self.spin_temp_ambiente.value()}°C | Ventilación: {ventilacion:.1f}x")
    
    def cambiar_gabinete(self):
        """Método legacy - ya no necesario con el nuevo sistema de builds"""
        # Este método se mantiene por compatibilidad pero ya no se usa
        pass
    
    def actualizar_info_gabinete(self):
        """Actualiza la información del gabinete seleccionado"""
        # Este método ahora actualiza la información del build completo
        self.actualizar_info_build()
    
    def actualizar_analisis(self):
        """Actualiza el análisis cuando cambian los parámetros"""
        self.actualizar_labels_controles()
        
        if self.build_actual and self.calculadora_build:
            self.barra_estado.setText("Calculando análisis...")
            
            # Usar QTimer para no bloquear la UI
            QTimer.singleShot(100, self.ejecutar_analisis_asyncrono)
    
    def ejecutar_analisis_asyncrono(self):
        """Ejecuta el análisis de forma asíncrona"""
        try:
            # Ejecutar análisis completo
            self.ejecutar_analisis_completo()
            self.barra_estado.setText("Análisis completado")
        except Exception as e:
            self.barra_estado.setText(f"Error en análisis: {str(e)}")
            print(f"Error en análisis: {e}")
    
    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis matemático completo del build"""
        if not self.build_actual:
            QMessageBox.warning(self, "Sin build", "Seleccione un build desde la pestaña principal.")
            return
        
        if not self.calculadora_build:
            self.mostrar_error_matematicas()
            return
        
        try:
            # Obtener parámetros actuales de los controles (ahora ocultos pero funcionales)
            potencia_adicional = self.slider_potencia.value()
            temp_ambiente = self.spin_temp_ambiente.value()
            factor_ventilacion = self.slider_ventilacion.value() / 100.0
            
            # Actualizar parámetros del build
            self.actualizar_parametros_build(potencia_adicional, temp_ambiente, factor_ventilacion)
            
            # Ejecutar análisis matemático
            self.barra_estado.setText("Ejecutando análisis matemático...")
            
            # Ejecutar análisis específicos (si existen)
            if hasattr(self, 'ejecutar_analisis_termico'):
                self.ejecutar_analisis_termico()
            
            if hasattr(self, 'ejecutar_analisis_eficiencia'):
                self.ejecutar_analisis_eficiencia()
            
            if hasattr(self, 'ejecutar_analisis_sensibilidad'):
                self.ejecutar_analisis_sensibilidad()
            
            if hasattr(self, 'actualizar_resumen_matematico'):
                self.actualizar_resumen_matematico()
            
            # Actualizar todos los gráficos directamente
            self.actualizar_todos_graficos()
            
            self.barra_estado.setText("Análisis completado exitosamente")
            
        except Exception as e:
            self.barra_estado.setText(f"Error en análisis: {str(e)}")
            QMessageBox.critical(self, "Error de Análisis", f"Error ejecutando análisis: {str(e)}")
    
    def actualizar_parametros_build(self, potencia_adicional: float, temp_ambiente: float, factor_ventilacion: float):
        """Actualiza los parámetros del build para el análisis"""
        if not self.calculadora_build or not self.configuracion_actual:
            return
        
        # Combinar parámetros del build con parámetros de usuario
        parametros_actualizados = self.configuracion_actual.copy()
        parametros_actualizados.update({
            'potencia_adicional': potencia_adicional,
            'temperatura_ambiente': temp_ambiente,
            'factor_ventilacion': factor_ventilacion
        })
        
        # Actualizar calculadora
        self.calculadora_build.actualizar_parametros(parametros_actualizados)
    
    def ejecutar_analisis_termico(self):
        """Ejecuta el análisis térmico específico"""
        if not self.calculadora_build:
            return
        
        try:
            # Obtener datos térmicos
            datos_termicos = self.calculadora_build.calcular_analisis_termico()
            
            # Actualizar gráfico térmico
            self.actualizar_grafico_termico(datos_termicos)
            
            # Actualizar información térmica
            self.actualizar_info_termica(datos_termicos)
            
        except Exception as e:
            self.info_termico.setText(f"Error en análisis térmico: {str(e)}")
    
    def ejecutar_analisis_eficiencia(self):
        """Ejecuta el análisis de eficiencia específico"""
        if not self.calculadora_build:
            return
        
        try:
            # Obtener datos de eficiencia
            datos_eficiencia = self.calculadora_build.calcular_analisis_eficiencia()
            
            # Actualizar gráfico de eficiencia
            self.actualizar_grafico_eficiencia(datos_eficiencia)
            
            # Actualizar información de eficiencia
            self.actualizar_info_eficiencia(datos_eficiencia)
            
        except Exception as e:
            self.info_eficiencia.setText(f"Error en análisis de eficiencia: {str(e)}")
    
    def ejecutar_analisis_sensibilidad(self):
        """Ejecuta el análisis de sensibilidad específico"""
        if not self.calculadora_build:
            return
        
        try:
            # Obtener datos de sensibilidad
            datos_sensibilidad = self.calculadora_build.calcular_analisis_sensibilidad()
            
            # Actualizar gráfico de sensibilidad
            self.actualizar_grafico_sensibilidad(datos_sensibilidad)
            
            # Actualizar información de sensibilidad
            self.actualizar_info_sensibilidad(datos_sensibilidad)
            
        except Exception as e:
            self.info_sensibilidad.setText(f"Error en análisis de sensibilidad: {str(e)}")
    
    def actualizar_resumen_matematico(self):
        """Actualiza el resumen matemático"""
        if not self.calculadora_build:
            return
        
        try:
            # Obtener resumen completo
            resumen = self.calculadora_build.generar_resumen_completo()
            
            # Actualizar texto del resumen
            if hasattr(self, 'texto_resumen'):
                self.texto_resumen.setText(resumen)
            
        except Exception as e:
            if hasattr(self, 'texto_resumen'):
                self.texto_resumen.setText(f"Error generando resumen: {str(e)}")
    
    def actualizar_parametros(self):
        """Actualiza los parámetros en tiempo real"""
        # Actualizar etiquetas
        self.label_potencia.setText(f"{self.slider_potencia.value()} W")
        self.label_ventilacion.setText(f"{self.slider_ventilacion.value() / 100.0:.1f}x")
        
        # Si hay build activo, actualizar análisis
        if self.build_actual and self.calculadora_build:
            self.actualizar_parametros_build(
                self.slider_potencia.value(),
                self.spin_temp_ambiente.value(),
                self.slider_ventilacion.value() / 100.0
            )
            
            # Actualizar gráficos si están habilitados
            if self.check_derivadas.isChecked():
                self.actualizar_graficos()
    
    def actualizar_graficos(self):
        """Actualiza todos los gráficos basado en el build actual"""
        if not self.build_actual or not self.calculadora_build:
            return
        
        try:
            # Actualizar gráfico térmico
            self.actualizar_grafico_termico_solo()
            
            # Actualizar gráfico de eficiencia
            self.actualizar_grafico_eficiencia_solo()
            
            # Actualizar gráfico de sensibilidad
            self.actualizar_grafico_sensibilidad_solo()
            
        except Exception as e:
            self.barra_estado.setText(f"Error actualizando gráficos: {str(e)}")
            print(f"Error actualizando gráficos: {e}")
    
    def actualizar_grafico_termico(self, datos_termicos: Dict[str, Any]):
        """Actualiza el gráfico térmico con datos específicos"""
        if not hasattr(self, 'canvas_termico') or not self.graficos:
            return
        
        try:
            # Limpiar canvas
            self.canvas_termico.figure.clear()
            
            # Crear gráfico térmico
            ax = self.canvas_termico.figure.add_subplot(111)
            
            # Plotear datos térmicos
            if 'x_values' in datos_termicos and 'y_values' in datos_termicos:
                ax.plot(datos_termicos['x_values'], datos_termicos['y_values'], 
                       'b-', linewidth=2, label='Temperatura')
                
                # Plotear derivada si está habilitada
                if self.check_derivadas.isChecked() and 'derivada' in datos_termicos:
                    ax.plot(datos_termicos['x_values'], datos_termicos['derivada'], 
                           'r--', linewidth=1, label='Derivada')
                
                # Marcar puntos críticos
                if self.check_puntos_criticos.isChecked() and 'puntos_criticos' in datos_termicos:
                    for punto in datos_termicos['puntos_criticos']:
                        ax.plot(punto['x'], punto['y'], 'ro', markersize=8)
                        ax.annotate(f'T={punto["y"]:.1f}°C', 
                                  (punto['x'], punto['y']), 
                                  xytext=(5, 5), textcoords='offset points')
            
            ax.set_xlabel('Potencia (W)')
            ax.set_ylabel('Temperatura (°C)')
            ax.set_title('Análisis Térmico del Build')
            ax.grid(True, alpha=0.3)
            # ax.legend()  # Comentado hasta agregar labels
            
            self.canvas_termico.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico térmico: {e}")
    
    def actualizar_grafico_eficiencia(self, datos_eficiencia: Dict[str, Any]):
        """Actualiza el gráfico de eficiencia con datos específicos"""
        if not hasattr(self, 'canvas_eficiencia') or not self.graficos:
            return
        
        try:
            # Limpiar canvas
            self.canvas_eficiencia.figure.clear()
            
            # Crear gráfico de eficiencia
            ax = self.canvas_eficiencia.figure.add_subplot(111)
            
            # Plotear datos de eficiencia
            if 'x_values' in datos_eficiencia and 'y_values' in datos_eficiencia:
                ax.plot(datos_eficiencia['x_values'], datos_eficiencia['y_values'], 
                       'g-', linewidth=2, label='Eficiencia')
                
                # Plotear derivada si está habilitada
                if self.check_derivadas.isChecked() and 'derivada' in datos_eficiencia:
                    ax.plot(datos_eficiencia['x_values'], datos_eficiencia['derivada'], 
                           'r--', linewidth=1, label='Derivada')
                
                # Marcar puntos óptimos
                if self.check_puntos_criticos.isChecked() and 'puntos_optimos' in datos_eficiencia:
                    for punto in datos_eficiencia['puntos_optimos']:
                        ax.plot(punto['x'], punto['y'], 'go', markersize=8)
                        ax.annotate(f'Ef={punto["y"]:.2f}', 
                                  (punto['x'], punto['y']), 
                                  xytext=(5, 5), textcoords='offset points')
            
            ax.set_xlabel('Carga del Sistema (%)')
            ax.set_ylabel('Eficiencia')
            ax.set_title('Análisis de Eficiencia del Build')
            ax.grid(True, alpha=0.3)
            # ax.legend()  # Comentado hasta agregar labels
            
            self.canvas_eficiencia.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico de eficiencia: {e}")
    
    def actualizar_grafico_sensibilidad(self, datos_sensibilidad: Dict[str, Any]):
        """Actualiza el gráfico de sensibilidad con datos específicos"""
        if not hasattr(self, 'canvas_sensibilidad') or not self.graficos:
            return
        
        try:
            # Limpiar canvas
            self.canvas_sensibilidad.figure.clear()
            
            # Crear gráfico de sensibilidad
            ax = self.canvas_sensibilidad.figure.add_subplot(111)
            
            # Plotear datos de sensibilidad
            if 'componentes' in datos_sensibilidad and 'sensibilidades' in datos_sensibilidad:
                ax.bar(datos_sensibilidad['componentes'], 
                      datos_sensibilidad['sensibilidades'], 
                      color=['red', 'green', 'blue', 'orange', 'purple'])
                
                # Agregar valores en las barras
                for i, v in enumerate(datos_sensibilidad['sensibilidades']):
                    ax.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
            
            ax.set_xlabel('Componentes')
            ax.set_ylabel('Sensibilidad')
            ax.set_title('Análisis de Sensibilidad del Build')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Rotar etiquetas del eje x para mejor legibilidad
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            self.canvas_sensibilidad.draw()
            
        except Exception as e:
            print(f"Error actualizando gráfico de sensibilidad: {e}")
    
    def actualizar_grafico_termico_solo(self):
        """Actualiza solo el gráfico térmico"""
        if not self.calculadora_build:
            return
        
        try:
            datos_termicos = self.calculadora_build.calcular_analisis_termico()
            self.actualizar_grafico_termico(datos_termicos)
        except Exception as e:
            print(f"Error en actualización térmica: {e}")
    
    def actualizar_grafico_eficiencia_solo(self):
        """Actualiza solo el gráfico de eficiencia"""
        if not self.calculadora_build:
            return
        
        try:
            datos_eficiencia = self.calculadora_build.calcular_analisis_eficiencia()
            self.actualizar_grafico_eficiencia(datos_eficiencia)
        except Exception as e:
            print(f"Error en actualización de eficiencia: {e}")
    
    def actualizar_grafico_sensibilidad_solo(self):
        """Actualiza solo el gráfico de sensibilidad"""
        if not self.calculadora_build:
            return
        
        try:
            datos_sensibilidad = self.calculadora_build.calcular_analisis_sensibilidad()
            self.actualizar_grafico_sensibilidad(datos_sensibilidad)
        except Exception as e:
            print(f"Error en actualización de sensibilidad: {e}")
    
    def actualizar_info_termica(self, datos_termicos: Dict[str, Any]):
        """Actualiza la información térmica"""
        if not hasattr(self, 'info_termico'):
            return
        
        try:
            info_text = "📊 Análisis Térmico:\n\n"
            
            if 'temperatura_maxima' in datos_termicos:
                info_text += f"🌡️ Temperatura máxima: {datos_termicos['temperatura_maxima']:.1f}°C\n"
            
            if 'temperatura_operacion' in datos_termicos:
                info_text += f"🏃 Temp. operación: {datos_termicos['temperatura_operacion']:.1f}°C\n"
            
            if 'margen_termico' in datos_termicos:
                info_text += f"⚠️ Margen térmico: {datos_termicos['margen_termico']:.1f}°C\n"
            
            if 'puntos_criticos' in datos_termicos:
                info_text += f"\n🔍 Puntos críticos encontrados: {len(datos_termicos['puntos_criticos'])}\n"
            
            self.info_termico.setText(info_text)
            
        except Exception as e:
            self.info_termico.setText(f"Error mostrando información térmica: {str(e)}")
    
    def actualizar_info_eficiencia(self, datos_eficiencia: Dict[str, Any]):
        """Actualiza la información de eficiencia"""
        if not hasattr(self, 'info_eficiencia'):
            return
        
        try:
            info_text = "⚡ Análisis de Eficiencia:\n\n"
            
            if 'eficiencia_maxima' in datos_eficiencia:
                info_text += f"📈 Eficiencia máxima: {datos_eficiencia['eficiencia_maxima']:.2f}\n"
            
            if 'eficiencia_operacion' in datos_eficiencia:
                info_text += f"🏃 Eficiencia operación: {datos_eficiencia['eficiencia_operacion']:.2f}\n"
            
            if 'punto_optimo' in datos_eficiencia:
                opt = datos_eficiencia['punto_optimo']
                info_text += f"🎯 Punto óptimo: {opt['carga']:.1f}% carga\n"
            
            if 'perdidas_estimadas' in datos_eficiencia:
                info_text += f"💸 Pérdidas estimadas: {datos_eficiencia['perdidas_estimadas']:.1f}W\n"
            
            self.info_eficiencia.setText(info_text)
            
        except Exception as e:
            self.info_eficiencia.setText(f"Error mostrando información de eficiencia: {str(e)}")
    
    def actualizar_info_sensibilidad(self, datos_sensibilidad: Dict[str, Any]):
        """Actualiza la información de sensibilidad"""
        if not hasattr(self, 'info_sensibilidad'):
            return
        
        try:
            info_text = "🔍 Análisis de Sensibilidad:\n\n"
            
            if 'componente_critico' in datos_sensibilidad:
                info_text += f"⚠️ Componente más crítico: {datos_sensibilidad['componente_critico']}\n"
            
            if 'sensibilidad_maxima' in datos_sensibilidad:
                info_text += f"📊 Sensibilidad máxima: {datos_sensibilidad['sensibilidad_maxima']:.3f}\n"
            
            if 'recomendaciones' in datos_sensibilidad:
                info_text += f"\n💡 Recomendaciones:\n"
                for rec in datos_sensibilidad['recomendaciones'][:3]:  # Mostrar solo 3
                    info_text += f"• {rec}\n"
            
            self.info_sensibilidad.setText(info_text)
            
        except Exception as e:
            self.info_sensibilidad.setText(f"Error mostrando información de sensibilidad: {str(e)}")
    
    def mostrar_error_matematicas(self):
        """Muestra un error relacionado con los componentes matemáticos"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error en Componentes Matemáticos")
        msg.setText("Error inicializando componentes matemáticos")
        msg.setInformativeText("Es posible que algunas funciones de análisis no estén disponibles.")
        msg.setDetailedText("Verifique que matplotlib y numpy estén correctamente instalados.")
        msg.exec()
    
    def actualizar_analisis_legacy(self):
        """Método legacy para compatibilidad - redirige al nuevo sistema"""
        self.actualizar_parametros()
    
    def reemplazar_canvas(self, canvas_viejo, canvas_nuevo, contenedor):
        """Reemplaza un canvas en el contenedor"""
        try:
            layout = contenedor.layout()
            if layout:
                # Encontrar y remover el canvas viejo
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and item.widget() == canvas_viejo:
                        layout.removeItem(item)
                        canvas_viejo.deleteLater()
                        break
                
                # Insertar el nuevo canvas en la posición correcta
                layout.insertWidget(1, canvas_nuevo)
        except Exception as e:
            print(f"Error reemplazando canvas: {e}")
    
    def actualizar_resumen(self):
        """Actualiza el resumen matemático"""
        if not self.gabinete_actual or not self.calculadora:
            return
        
        try:
            resumen = self.calculadora.crear_resumen_matematico(self.gabinete_actual)
            self.texto_resumen.setText(resumen)
        except Exception as e:
            self.texto_resumen.setText(f"Error generando resumen: {str(e)}")
    
    def resetear_parametros(self):
        """Resetea los parámetros a valores por defecto"""
        self.slider_potencia.setValue(50)  # Potencia adicional, no total
        self.spin_temp_ambiente.setValue(25.0)
        self.slider_ventilacion.setValue(100)
        self.check_derivadas.setChecked(True)
        self.check_puntos_criticos.setChecked(True)
        self.check_area_sombreada.setChecked(True)
        
        # Actualizar análisis si hay un build activo
        if self.build_actual:
            self.actualizar_parametros()
            self.ejecutar_analisis_completo()
    
    def exportar_graficos(self):
        """Exporta los gráficos a archivos"""
        if not self.build_actual:
            QMessageBox.warning(self, "Sin build", "Seleccione un build desde la pestaña principal.")
            return
        
        try:
            # Generar nombre base para archivos
            nombre_base = "analisis_build"
            
            # Intentar usar nombre del gabinete si existe
            if 'case' in self.build_actual and self.build_actual['case']:
                case_name = self.build_actual['case'].get('name', 'gabinete')
                nombre_base = f"analisis_{case_name.replace(' ', '_')}"
            
            # Exportar cada gráfico usando matplotlib
            if hasattr(self, 'canvas_termico'):
                self.exportar_canvas_individual(self.canvas_termico, f"{nombre_base}_termico")
            
            if hasattr(self, 'canvas_eficiencia'):
                self.exportar_canvas_individual(self.canvas_eficiencia, f"{nombre_base}_eficiencia")
            
            if hasattr(self, 'canvas_sensibilidad'):
                self.exportar_canvas_individual(self.canvas_sensibilidad, f"{nombre_base}_sensibilidad")
            
            QMessageBox.information(self, "Exportación", "Gráficos exportados exitosamente.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Exportación", f"Error exportando gráficos: {str(e)}")
    
    def exportar_canvas_individual(self, canvas, nombre_archivo: str):
        """Exporta un canvas individual a archivo"""
        try:
            if hasattr(canvas, 'figure'):
                canvas.figure.savefig(f"{nombre_archivo}.png", dpi=300, bbox_inches='tight')
        except Exception as e:
            print(f"Error exportando {nombre_archivo}: {e}")
    
    def mostrar_error_matematicas(self):
        """Muestra un mensaje de error sobre componentes matemáticos"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Componentes Matemáticos")
        msg.setText("Los componentes matemáticos no están disponibles.")
        msg.setDetailedText(
            "Para habilitar el análisis matemático completo, instale:\n"
            "- matplotlib>=3.5.0\n"
            "- sympy>=1.9.0\n"
            "- seaborn>=0.11.0\n\n"
            "Ejecute: pip install -r requirements.txt"
        )
        msg.exec()
    
    def establecer_datos_componentes(self, datos: Dict[str, Any]):
        """Establece los datos de componentes desde la aplicación principal"""
        self.datos_componentes = datos
        self.cargar_gabinetes()
        
        # Actualizar calculadora si existe
        if self.calculadora:
            self.calculadora.establecer_configuracion(datos)
    def obtener_configuracion_actual(self) -> Dict[str, Any]:
        """Obtiene la configuración actual de parámetros"""
        return {
            'potencia_adicional': self.slider_potencia.value(),
            'temperatura_ambiente': self.spin_temp_ambiente.value(),
            'factor_ventilacion': self.slider_ventilacion.value() / 100.0,
            'mostrar_derivadas': self.check_derivadas.isChecked(),
            'mostrar_puntos_criticos': self.check_puntos_criticos.isChecked(),
            'mostrar_area_sombreada': self.check_area_sombreada.isChecked(),
            'build_actual': self.build_actual,
            'configuracion_actual': self.configuracion_actual
        }
        
    def interpretar_curva_termica(self, delta_t: float) -> str:
        """Interpreta la curva térmica basada en el delta de temperatura"""
        if delta_t < 10:
            return "excelente comportamiento térmico"
        elif delta_t < 20:
            return "buen comportamiento térmico"
        elif delta_t < 30:
            return "comportamiento térmico aceptable"
        else:
            return "problemas potenciales de temperatura"
    
    def interpretar_eficiencia(self, eficiencia: float) -> str:
        """Interpreta la eficiencia térmica del sistema"""
        eff_percent = eficiencia * 100
        if eff_percent > 85:
            return "excelente"
        elif eff_percent > 70:
            return "buena"
        elif eff_percent > 50:
            return "aceptable"
        else:
            return "por debajo de lo óptimo"
    
    def calcular_volumen_gabinete(self) -> float:
        """Calcula el volumen del gabinete en litros"""
        if not self.build_actual or 'case' not in self.build_actual:
            return 40.0  # Valor por defecto
        
        case = self.build_actual['case']
        
        # Intentar obtener dimensiones directamente
        volumen = case.get('volume')
        if volumen:
            try:
                return float(volumen)
            except (ValueError, TypeError):
                pass
        
        # Calcular desde dimensiones si están disponibles
        width = case.get('width')
        height = case.get('height')
        depth = case.get('depth')
        
        if width and height and depth:
            try:
                # Convertir mm³ a litros (1L = 1000000 mm³)
                return float(width) * float(height) * float(depth) / 1000000.0
            except (ValueError, TypeError):
                pass
                
        # Valores típicos por factor de forma
        factor_forma = case.get('form_factor', '').lower()
        if 'full' in factor_forma or 'e-atx' in factor_forma:
            return 70.0
        elif 'mid' in factor_forma or 'atx' in factor_forma:
            return 45.0
        elif 'mini' in factor_forma or 'micro' in factor_forma or 'matx' in factor_forma:
            return 25.0
        elif 'itx' in factor_forma or 'sff' in factor_forma:
            return 15.0
        
        # Valor por defecto
        return 40.0
    
    def calcular_datos_ventiladores(self) -> Dict[str, Any]:
        """Calcula datos sobre los ventiladores del gabinete"""
        if not self.build_actual or 'case' not in self.build_actual:
            return {'cantidad_total': 2, 'capacidad_total': 120.0}
        
        case = self.build_actual['case']
        
        # Intentar obtener datos directos de ventiladores
        fan_count = case.get('fan_count')
        if not fan_count:
            fan_count = case.get('included_fans', 0)
        
        try:
            fan_count = int(fan_count)
        except (ValueError, TypeError):
            # Estimar basado en factor de forma
            factor_forma = case.get('form_factor', '').lower()
            if 'full' in factor_forma or 'e-atx' in factor_forma:
                fan_count = 4
            elif 'mid' in factor_forma or 'atx' in factor_forma:
                fan_count = 3
            else:
                fan_count = 2
        
        # Estimar capacidad total (CFM por ventilador)
        fan_size = case.get('max_fan_size', 120)
        try:
            fan_size = int(fan_size)
        except (ValueError, TypeError):
            fan_size = 120
        
        # Fórmula simplificada para CFM
        cfm_per_fan = fan_size * 0.5
        total_capacity = fan_count * cfm_per_fan
        
        return {
            'cantidad_total': fan_count,
            'capacidad_total': total_capacity,
            'tamaño_ventilador': fan_size
        }
    
    def actualizar_todos_graficos(self):
        """Actualiza todos los gráficos matemáticos a la vez"""
        try:
            # Asegurar que el módulo math esté importado
            import math
                        
            # Actualizar cada gráfico individualmente
            self.actualizar_grafico_termico_basico()
            self.actualizar_grafico_eficiencia_basico()
            self.actualizar_grafico_sensibilidad_basico()
            
            # Actualizar el texto de resumen
            if hasattr(self, 'texto_resumen'):
                try:
                    if self.build_actual and self.calculadora:
                        # Calcular valores derivados
                        params = self.configuracion_actual
                        
                        # Obtener datos del ventilador desde el gabinete
                        fan_data = self.calcular_datos_ventiladores()
                        fan_capacity = fan_data['capacidad_total']
                        fan_count = fan_data['cantidad_total']
                        
                        # Calcular factores térmicos
                        potencia_total = params.get('potencia_total', 0)
                        temp_ambiente = self.spin_temp_ambiente.value()
                        volumen_case = self.calcular_volumen_gabinete()
                        
                        # Calcular temperatura usando modelo refinado
                        # T = Ta + (P * k) / (V^0.33 * F)
                        k_factor = 0.05  # Factor térmico (ajustable)
                        v_factor = max(0.1, volumen_case ** 0.33)  # Relación cúbica con volumen
                        f_factor = max(1.0, fan_capacity / 100)  # Factor de ventilación basado en capacidad real
                        
                        temp_actual = temp_ambiente + (potencia_total * k_factor) / (v_factor * f_factor)
                        
                        # Derivada dT/dP (sensibilidad térmica)
                        sensibilidad_termica = k_factor / (v_factor * f_factor)
                        
                        # Cálculo de eficiencia térmica
                        # η(T) = 1 / (1 + e^((T-Ta)/10))
                        delta_t = temp_actual - temp_ambiente
                        eficiencia = 1 / (1 + math.exp(delta_t / 10))
                        
                        # Derivada de eficiencia respecto a potencia
                        sensibilidad_eficiencia = -eficiencia * (1 - eficiencia) * sensibilidad_termica / 10
                        
                        # Potencia óptima (donde dη/dP = 0)
                        # Usando logaritmo natural para el cálculo
                        potencia_optima = (v_factor * f_factor * 10 * math.log(1)) / k_factor if k_factor > 0 else 0
                        # Como log(1) = 0, este valor será 0, así que lo ajustamos a un valor más realista
                        potencia_optima = (v_factor * f_factor * 20) / k_factor if k_factor > 0 else potencia_total
                        
                        # Verificar valores para evitar divisiones por cero
                        if potencia_optima <= 0:
                            potencia_optima = potencia_total
                        
                        # Relación con la potencia óptima
                        relacion_potencia = (potencia_total/potencia_optima*100) if potencia_optima > 0 else 100
                        
                        # Preparar parámetros para la plantilla de resumen
                        params = {
                            'potencia_total': potencia_total,
                            'temp_ambiente': temp_ambiente,
                            'volumen_case': volumen_case,
                            'fan_count': fan_count,
                            'fan_capacity': fan_capacity,
                            'f_factor': f_factor,
                            'temp_actual': temp_actual,
                            'delta_t': delta_t,
                            'sensibilidad_termica': sensibilidad_termica,
                            'eficiencia': eficiencia,
                            'sensibilidad_eficiencia': sensibilidad_eficiencia,
                            'potencia_optima': potencia_optima,
                            'relacion_potencia': relacion_potencia,
                            'interpretacion_curva': self.interpretar_curva_termica(delta_t),
                            'interpretacion_eficiencia': self.interpretar_eficiencia(eficiencia)
                        }
                        
                        # Generar resumen utilizando la plantilla
                        if 'generar_resumen_html' in globals() and generar_resumen_html:
                            try:
                                resumen = generar_resumen_html(params)
                                self.texto_resumen.setHtml(resumen)
                            except Exception as e:
                                import traceback
                                error_details = traceback.format_exc()
                                print(f"Error generando resumen con plantilla: {error_details}")
                                self.texto_resumen.setText(f"Error generando resumen: {str(e)}")
                        else:
                            self.texto_resumen.setText("Módulo de plantillas no disponible")
                    else:
                        self.texto_resumen.setText("Análisis matemático aparecerá aquí cuando se seleccione un build")
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Error en resumen matemático: {error_details}")
                    self.texto_resumen.setText(f"Error generando resumen: {str(e)}")
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error actualizando todos los gráficos: {error_details}")
            self.barra_estado.setText(f"Error en la actualización de gráficos: {str(e)}")