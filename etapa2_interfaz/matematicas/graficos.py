"""
Módulo de gráficos matemáticos para PC Builder
Genera gráficos interactivos y visualizaciones de análisis matemático
"""

import numpy as np
import matplotlib
matplotlib.use('QtAgg')  # Actualizado para compatibilidad con PyQt6
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
from typing import Dict, List, Tuple, Optional, Any
import seaborn as sns


class GraficosMatematicos:
    """Clase para generar gráficos matemáticos del análisis de PC"""
    
    def __init__(self, estilo_oscuro: bool = True):
        self.estilo_oscuro = estilo_oscuro
        self.configurar_estilo()
        
    def configurar_estilo(self):
        """Configura el estilo visual de los gráficos"""
        if self.estilo_oscuro:
            plt.style.use('dark_background')
            self.colores = {
                'primario': '#00d4ff',
                'secundario': '#ff6b6b',
                'terciario': '#4ecdc4',
                'acento': '#ffe66d',
                'fondo': '#2c3e50',
                'texto': '#ecf0f1'
            }
        else:
            plt.style.use('default')
            self.colores = {
                'primario': '#3498db',
                'secundario': '#e74c3c',
                'terciario': '#2ecc71',
                'acento': '#f39c12',
                'fondo': '#ffffff',
                'texto': '#2c3e50'
            }
            
    def crear_canvas_matplotlib(self, ancho: int = 800, alto: int = 600) -> FigureCanvas:
        """
        Crea un canvas de matplotlib para integrar con PyQt6
        
        Args:
            ancho: Ancho del canvas en píxeles
            alto: Alto del canvas en píxeles
            
        Returns:
            Canvas de matplotlib
        """
        fig = Figure(figsize=(ancho/100, alto/100), dpi=100)
        if self.estilo_oscuro:
            fig.patch.set_facecolor(self.colores['fondo'])
        
        canvas = FigureCanvas(fig)
        return canvas
    
    def grafico_curva_temperatura(self, datos_temperatura: Dict[str, Any]) -> FigureCanvas:
        """
        Crea un gráfico de curva de temperatura vs potencia
        
        Args:
            datos_temperatura: Datos de temperatura calculados
            
        Returns:
            Canvas con el gráfico
        """
        canvas = self.crear_canvas_matplotlib(800, 600)
        fig = canvas.figure
        
        # Crear subplot principal
        ax1 = fig.add_subplot(211)
        
        # Datos
        potencias = datos_temperatura['potencias']
        temperaturas = datos_temperatura['temperaturas']
        derivadas = datos_temperatura['derivadas']
        
        # Gráfico de temperatura
        ax1.plot(potencias, temperaturas, 
                color=self.colores['primario'], 
                linewidth=2.5, 
                label='Temperatura T(P)')
        
        # Marcadores para puntos importantes
        temp_max = max(temperaturas)
        temp_min = min(temperaturas)
        idx_max = temperaturas.index(temp_max)
        idx_min = temperaturas.index(temp_min)
        
        ax1.scatter([potencias[idx_max]], [temp_max], 
                   color=self.colores['secundario'], 
                   s=100, 
                   zorder=5, 
                   label=f'Máximo: {temp_max:.1f}°C')
        
        ax1.scatter([potencias[idx_min]], [temp_min], 
                   color=self.colores['terciario'], 
                   s=100, 
                   zorder=5, 
                   label=f'Mínimo: {temp_min:.1f}°C')
        
        # Configuración del gráfico
        ax1.set_xlabel('Potencia (W)', fontsize=12, color=self.colores['texto'])
        ax1.set_ylabel('Temperatura (°C)', fontsize=12, color=self.colores['texto'])
        ax1.set_title('Análisis Térmico: Temperatura vs Potencia', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        
        # Colorear el área bajo la curva
        ax1.fill_between(potencias, temperaturas, alpha=0.3, color=self.colores['primario'])
        
        # Subplot para derivadas
        ax2 = fig.add_subplot(212)
        
        # Gráfico de derivadas
        ax2.plot(potencias, derivadas, 
                color=self.colores['acento'], 
                linewidth=2, 
                label='dT/dP (°C/W)')
        
        # Línea de referencia en y=0
        ax2.axhline(y=0, color=self.colores['texto'], linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('Potencia (W)', fontsize=12, color=self.colores['texto'])
        ax2.set_ylabel('Derivada (°C/W)', fontsize=12, color=self.colores['texto'])
        ax2.set_title('Derivada: Tasa de Cambio de Temperatura', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper right')
        
        # Ajustar layout
        fig.tight_layout()
        
        return canvas
    
    def grafico_eficiencia_termica(self, datos_eficiencia: Dict[str, Any]) -> FigureCanvas:
        """
        Crea un gráfico de eficiencia térmica vs temperatura
        
        Args:
            datos_eficiencia: Datos de eficiencia calculados
            
        Returns:
            Canvas con el gráfico
        """
        canvas = self.crear_canvas_matplotlib(800, 600)
        fig = canvas.figure
        
        # Crear subplot principal
        ax1 = fig.add_subplot(211)
        
        # Datos
        temperaturas = datos_eficiencia['temperaturas']
        eficiencias = datos_eficiencia['eficiencias']
        temp_optima = datos_eficiencia['temperatura_optima']
        eficiencia_maxima = datos_eficiencia['eficiencia_maxima']
        
        # Gráfico de eficiencia
        ax1.plot(temperaturas, eficiencias, 
                color=self.colores['primario'], 
                linewidth=2.5, 
                label='Eficiencia η(T)')
        
        # Marcar punto óptimo
        ax1.scatter([temp_optima], [eficiencia_maxima], 
                   color=self.colores['secundario'], 
                   s=150, 
                   zorder=5, 
                   label=f'Óptimo: {temp_optima:.1f}°C')
        
        # Línea vertical en el punto óptimo
        ax1.axvline(x=temp_optima, color=self.colores['secundario'], 
                   linestyle='--', alpha=0.7, label='Temp. Óptima')
        
        # Configuración del gráfico
        ax1.set_xlabel('Temperatura (°C)', fontsize=12, color=self.colores['texto'])
        ax1.set_ylabel('Eficiencia', fontsize=12, color=self.colores['texto'])
        ax1.set_title('Análisis de Eficiencia: η vs Temperatura', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right')
        
        # Colorear el área bajo la curva
        ax1.fill_between(temperaturas, eficiencias, alpha=0.3, color=self.colores['primario'])
        
        # Subplot para derivadas
        ax2 = fig.add_subplot(212)
        
        # Gráfico de derivadas
        derivadas = datos_eficiencia['derivadas']
        ax2.plot(temperaturas, derivadas, 
                color=self.colores['acento'], 
                linewidth=2, 
                label='dη/dT (1/°C)')
        
        # Línea de referencia en y=0
        ax2.axhline(y=0, color=self.colores['texto'], linestyle='--', alpha=0.5)
        
        # Marcar donde la derivada es cero (punto crítico)
        ax2.axvline(x=temp_optima, color=self.colores['secundario'], 
                   linestyle='--', alpha=0.7)
        
        ax2.set_xlabel('Temperatura (°C)', fontsize=12, color=self.colores['texto'])
        ax2.set_ylabel('Derivada (1/°C)', fontsize=12, color=self.colores['texto'])
        ax2.set_title('Derivada: Tasa de Cambio de Eficiencia', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper right')
        
        # Ajustar layout
        fig.tight_layout()
        
        return canvas
    
    def grafico_sensibilidad_parametros(self, datos_sensibilidad: Dict[str, Any]) -> FigureCanvas:
        """
        Crea un gráfico de barras para análisis de sensibilidad
        
        Args:
            datos_sensibilidad: Datos de sensibilidad calculados
            
        Returns:
            Canvas con el gráfico
        """
        canvas = self.crear_canvas_matplotlib(800, 600)
        fig = canvas.figure
        
        # Crear subplot
        ax = fig.add_subplot(111)
        
        # Extraer datos del ranking
        ranking = datos_sensibilidad['ranking_sensibilidad']
        parametros = [item[0] for item in ranking]
        sensibilidades = [item[1]['sensibilidad_relativa'] for item in ranking]
        
        # Colores para cada barra
        colores_barras = [self.colores['primario'], self.colores['secundario'], 
                         self.colores['terciario'], self.colores['acento']]
        
        # Crear gráfico de barras
        barras = ax.bar(parametros, sensibilidades, 
                       color=colores_barras[:len(parametros)], 
                       alpha=0.8, 
                       edgecolor=self.colores['texto'], 
                       linewidth=1)
        
        # Agregar valores en las barras
        for i, (barra, valor) in enumerate(zip(barras, sensibilidades)):
            altura = barra.get_height()
            ax.text(barra.get_x() + barra.get_width()/2., altura + 0.01,
                   f'{valor:.3f}', ha='center', va='bottom', 
                   fontsize=10, color=self.colores['texto'])
        
        # Configuración del gráfico
        ax.set_xlabel('Parámetros', fontsize=12, color=self.colores['texto'])
        ax.set_ylabel('Sensibilidad Relativa', fontsize=12, color=self.colores['texto'])
        ax.set_title('Análisis de Sensibilidad de Parámetros', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Línea de referencia
        ax.axhline(y=1.0, color=self.colores['secundario'], 
                  linestyle='--', alpha=0.7, label='Sensibilidad alta (>1.0)')
        
        # Etiquetas de parámetros
        nombres_parametros = {
            'P': 'Potencia',
            'V': 'Volumen',
            'A': 'Área Vent.',
            'f': 'Flujo Aire'
        }
        
        etiquetas = [nombres_parametros.get(param, param) for param in parametros]
        ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        
        ax.legend()
        
        # Ajustar layout
        fig.tight_layout()
        
        return canvas
    
    def grafico_optimizacion_volumen(self, datos_volumen: Dict[str, Any]) -> FigureCanvas:
        """
        Crea un gráfico 3D para optimización de volumen
        
        Args:
            datos_volumen: Datos de optimización de volumen
            
        Returns:
            Canvas con el gráfico
        """
        canvas = self.crear_canvas_matplotlib(800, 600)
        fig = canvas.figure
        
        # Crear subplot 3D
        ax = fig.add_subplot(111, projection='3d')
        
        # Datos actuales
        dimensiones = datos_volumen['dimensiones_actuales']
        x_actual = dimensiones['x']
        y_actual = dimensiones['y']
        z_actual = dimensiones['z']
        
        # Crear malla para superficie
        x_range = np.linspace(x_actual * 0.5, x_actual * 1.5, 20)
        y_range = np.linspace(y_actual * 0.5, y_actual * 1.5, 20)
        X, Y = np.meshgrid(x_range, y_range)
        
        # Calcular volumen para cada punto (Z fijo)
        Z = np.full_like(X, z_actual)
        V = X * Y * Z
        
        # Superficie del volumen
        surf = ax.plot_surface(X, Y, V, 
                              cmap='viridis', 
                              alpha=0.7, 
                              edgecolor='none')
        
        # Punto actual
        volumen_actual = datos_volumen['volumen_actual']
        ax.scatter([x_actual], [y_actual], [volumen_actual], 
                  color=self.colores['secundario'], 
                  s=200, 
                  label=f'Actual: {volumen_actual:.1f}L')
        
        # Configuración del gráfico
        ax.set_xlabel('Largo (cm)', fontsize=10, color=self.colores['texto'])
        ax.set_ylabel('Ancho (cm)', fontsize=10, color=self.colores['texto'])
        ax.set_zlabel('Volumen (L)', fontsize=10, color=self.colores['texto'])
        ax.set_title('Optimización de Volumen del Gabinete', fontsize=12, fontweight='bold')
        
        # Colorbar
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        cbar.set_label('Volumen (L)', fontsize=10, color=self.colores['texto'])
        
        # Ajustar layout
        fig.tight_layout()
        
        return canvas
    
    def crear_dashboard_completo(self, datos_completos: Dict[str, Any]) -> FigureCanvas:
        """
        Crea un dashboard completo con múltiples gráficos
        
        Args:
            datos_completos: Todos los datos de análisis
            
        Returns:
            Canvas con dashboard completo
        """
        canvas = self.crear_canvas_matplotlib(1200, 800)
        fig = canvas.figure
        
        # Crear grid de subplots
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Gráfico 1: Temperatura vs Potencia
        if 'temperatura' in datos_completos:
            ax1 = fig.add_subplot(gs[0, 0])
            datos_temp = datos_completos['temperatura']
            
            ax1.plot(datos_temp['potencias'], datos_temp['temperaturas'], 
                    color=self.colores['primario'], linewidth=2)
            ax1.set_title('Temperatura vs Potencia', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Potencia (W)', fontsize=10)
            ax1.set_ylabel('Temperatura (°C)', fontsize=10)
            ax1.grid(True, alpha=0.3)
            ax1.fill_between(datos_temp['potencias'], datos_temp['temperaturas'], 
                           alpha=0.3, color=self.colores['primario'])
        
        # Gráfico 2: Eficiencia vs Temperatura
        if 'eficiencia' in datos_completos:
            ax2 = fig.add_subplot(gs[0, 1])
            datos_ef = datos_completos['eficiencia']
            
            ax2.plot(datos_ef['temperaturas'], datos_ef['eficiencias'], 
                    color=self.colores['secundario'], linewidth=2)
            ax2.axvline(x=datos_ef['temperatura_optima'], 
                       color=self.colores['acento'], linestyle='--', alpha=0.7)
            ax2.set_title('Eficiencia vs Temperatura', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Temperatura (°C)', fontsize=10)
            ax2.set_ylabel('Eficiencia', fontsize=10)
            ax2.grid(True, alpha=0.3)
            ax2.fill_between(datos_ef['temperaturas'], datos_ef['eficiencias'], 
                           alpha=0.3, color=self.colores['secundario'])
        
        # Gráfico 3: Sensibilidad de Parámetros
        if 'sensibilidad' in datos_completos:
            ax3 = fig.add_subplot(gs[1, 0])
            datos_sens = datos_completos['sensibilidad']
            
            ranking = datos_sens['ranking_sensibilidad']
            parametros = [item[0] for item in ranking]
            sensibilidades = [item[1]['sensibilidad_relativa'] for item in ranking]
            
            ax3.bar(parametros, sensibilidades, 
                   color=self.colores['terciario'], alpha=0.8)
            ax3.set_title('Sensibilidad de Parámetros', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Sensibilidad Relativa', fontsize=10)
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Etiquetas mejoradas
            nombres_param = {'P': 'Potencia', 'V': 'Volumen', 'A': 'Área', 'f': 'Flujo'}
            etiquetas = [nombres_param.get(p, p) for p in parametros]
            ax3.set_xticklabels(etiquetas, rotation=45, ha='right')
        
        # Gráfico 4: Resumen de Optimización
        ax4 = fig.add_subplot(gs[1, 1])
        
        # Crear un gráfico de resumen con métricas clave
        metricas = []
        valores = []
        
        if 'temperatura' in datos_completos:
            temp_prom = np.mean(datos_completos['temperatura']['temperaturas'])
            metricas.append('Temp. Prom.')
            valores.append(temp_prom)
        
        if 'eficiencia' in datos_completos:
            ef_max = datos_completos['eficiencia']['eficiencia_maxima']
            metricas.append('Efic. Max.')
            valores.append(ef_max * 100)  # Convertir a porcentaje
        
        if 'sensibilidad' in datos_completos:
            sens_max = max([item[1]['sensibilidad_relativa'] 
                           for item in datos_completos['sensibilidad']['ranking_sensibilidad']])
            metricas.append('Sens. Max.')
            valores.append(sens_max)
        
        # Agregar volumen si disponible
        if 'volumen' in datos_completos:
            vol_actual = datos_completos['volumen']['volumen_actual']
            metricas.append('Volumen')
            valores.append(vol_actual)
        
        if metricas:
            colores_metricas = [self.colores['primario'], self.colores['secundario'], 
                               self.colores['terciario'], self.colores['acento']]
            
            ax4.bar(metricas, valores, 
                   color=colores_metricas[:len(metricas)], alpha=0.8)
            ax4.set_title('Resumen de Métricas', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Valor', fontsize=10)
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Rotar etiquetas si es necesario
            if len(metricas) > 2:
                ax4.set_xticklabels(metricas, rotation=45, ha='right')
        
        # Título general
        fig.suptitle('Dashboard de Análisis Matemático - PC Builder', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        return canvas
    
    def exportar_grafico(self, canvas: FigureCanvas, nombre_archivo: str, 
                        formato: str = 'png', dpi: int = 300):
        """
        Exporta un gráfico a archivo
        
        Args:
            canvas: Canvas de matplotlib
            nombre_archivo: Nombre del archivo (sin extensión)
            formato: Formato de archivo ('png', 'pdf', 'svg')
            dpi: Resolución para formatos raster
        """
        try:
            canvas.figure.savefig(f"{nombre_archivo}.{formato}", 
                                 dpi=dpi, bbox_inches='tight', 
                                 facecolor=self.colores['fondo'])
            return True
        except Exception as e:
            print(f"Error exportando gráfico: {e}")
            return False
    
    def crear_grafico_personalizado(self, datos: Dict[str, Any], 
                                   tipo_personalizado: str) -> FigureCanvas:
        """
        Crea un gráfico personalizado basado en parámetros específicos
        
        Args:
            datos: Datos para el gráfico
            tipo_personalizado: Tipo de gráfico personalizado
            
        Returns:
            Canvas con el gráfico
        """
        canvas = self.crear_canvas_matplotlib(800, 600)
        fig = canvas.figure
        ax = fig.add_subplot(111)
        
        if tipo_personalizado == 'comparacion_gabinetes':
            # Comparar múltiples gabinetes
            nombres = datos.get('nombres', [])
            temperaturas = datos.get('temperaturas', [])
            eficiencias = datos.get('eficiencias', [])
            
            x_pos = np.arange(len(nombres))
            width = 0.35
            
            ax.bar(x_pos - width/2, temperaturas, width, 
                  label='Temperatura (°C)', color=self.colores['primario'])
            
            ax2 = ax.twinx()
            ax2.bar(x_pos + width/2, eficiencias, width, 
                   label='Eficiencia', color=self.colores['secundario'])
            
            ax.set_xlabel('Gabinetes')
            ax.set_ylabel('Temperatura (°C)', color=self.colores['primario'])
            ax2.set_ylabel('Eficiencia', color=self.colores['secundario'])
            ax.set_title('Comparación de Gabinetes')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(nombres, rotation=45, ha='right')
            
            ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
        # Agregar más tipos personalizados según necesidades
        
        fig.tight_layout()
        return canvas
