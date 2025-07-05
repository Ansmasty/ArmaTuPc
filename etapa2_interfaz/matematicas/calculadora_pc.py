"""
Calculadora principal para análisis matemático de PCs
Integra todos los modelos matemáticos y proporciona una interfaz unificada
"""

import numpy as np
import sympy as sp
from typing import Dict, List, Tuple, Optional, Any, Union
from .modelos import (
    ModeloTermico, ModeloEficiencia, ModeloVolumen, ModeloFlujoAire,
    AnalizadorOptimizacion, crear_analizador_optimizacion
)


class CalculadoraPC:
    """Calculadora principal para análisis matemático de componentes PC"""
    
    def __init__(self):
        self.analizador = crear_analizador_optimizacion()
        self.configuracion_actual = {}
        self.resultados_cache = {}
        
    def establecer_configuracion(self, configuracion: Dict[str, Any]):
        """Establece la configuración actual de componentes"""
        self.configuracion_actual = configuracion.copy()
        self.resultados_cache.clear()  # Limpiar cache al cambiar configuración
        
        # Asegurar que los parámetros clave estén disponibles
        if 'potencia_total' not in self.configuracion_actual:
            # Calcular potencia total si no está presente
            potencia_total = 0
            for key, value in configuracion.items():
                if isinstance(value, (int, float)) and 'tdp' in key.lower():
                    potencia_total += value
                elif isinstance(value, (int, float)) and 'watt' in key.lower():
                    potencia_total += value
            
            if potencia_total > 0:
                self.configuracion_actual['potencia_total'] = potencia_total
            else:
                self.configuracion_actual['potencia_total'] = 300.0  # Valor por defecto
        
        print(f"DEBUG CalculadoraPC: Configuración establecida con potencia_total: {self.configuracion_actual.get('potencia_total', 'N/A')}")
        
        
    def analizar_gabinete_completo(self, datos_gabinete: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza un análisis matemático completo del gabinete
        
        Args:
            datos_gabinete: Datos del gabinete a analizar
            
        Returns:
            Diccionario con análisis completo incluyendo gráficos y optimización
        """
        # Usar el analizador para obtener resultados básicos
        resultados = self.analizador.analizar_gabinete(datos_gabinete)
        
        # Agregar análisis adicionales
        resultados['optimizacion'] = self._calcular_optimizacion(datos_gabinete)
        resultados['puntos_criticos'] = self._encontrar_puntos_criticos(datos_gabinete)
        resultados['recomendaciones'] = self._generar_recomendaciones(resultados)
        
        return resultados
    
    def calcular_curvas_temperatura(self, datos_gabinete: Dict[str, Any], 
                                  rango_potencia: Tuple[float, float] = (100, 500)) -> Dict[str, Any]:
        """
        Calcula curvas de temperatura vs potencia para análisis gráfico
        
        Args:
            datos_gabinete: Datos del gabinete
            rango_potencia: Rango de potencia a analizar (min, max)
            
        Returns:
            Diccionario con datos para gráficos
        """
        modelo_termico = self.analizador.modelos['termico']
        
        # Extraer parámetros del gabinete
        dimensiones = self.analizador._extraer_dimensiones(datos_gabinete)
        caracteristicas = self.analizador._extraer_caracteristicas(datos_gabinete)
        
        # Generar rango de potencias
        potencias = np.linspace(rango_potencia[0], rango_potencia[1], 50)
        temperaturas = []
        derivadas_temp = []
        
        # Parámetros fijos
        valores_base = {
            'V': dimensiones['volumen'],
            'A': caracteristicas['area_ventilacion'],
            'Ta': 25.0,
            'k': 0.1,
            'f': caracteristicas['factor_flujo']
        }
        
        for potencia in potencias:
            valores = valores_base.copy()
            valores['P'] = potencia
            
            # Calcular temperatura
            temp = modelo_termico.evaluar(valores)
            temperaturas.append(temp)
            
            # Calcular derivada dT/dP
            derivada = modelo_termico.evaluar_derivada('P', valores)
            derivadas_temp.append(derivada)
            
        return {
            'potencias': potencias.tolist(),
            'temperaturas': temperaturas,
            'derivadas': derivadas_temp,
            'parametros': valores_base,
            'unidades': {
                'potencia': 'W',
                'temperatura': '°C',
                'derivada': '°C/W'
            }
        }
    
    def calcular_optimizacion_volumen(self, datos_gabinete: Dict[str, Any],
                                    area_minima: float = 400.0) -> Dict[str, Any]:
        """
        Calcula la optimización de volumen para un gabinete
        
        Args:
            datos_gabinete: Datos del gabinete
            area_minima: Área mínima requerida (cm²)
            
        Returns:
            Resultados de optimización
        """
        modelo_volumen = self.analizador.modelos['volumen']
        
        # Obtener dimensiones actuales
        dimensiones = self.analizador._extraer_dimensiones(datos_gabinete)
        
        # Calcular optimización con restricciones
        optimizacion = modelo_volumen.optimizar_con_restricciones(area_minima)
        
        # Evaluar punto actual
        valores_actuales = {
            'x': dimensiones['largo'],
            'y': dimensiones['ancho'],
            'z': dimensiones['alto']
        }
        
        volumen_actual = modelo_volumen.evaluar(valores_actuales)
        
        # Calcular derivadas en el punto actual
        derivadas_actuales = {}
        for var in ['x', 'y', 'z']:
            derivadas_actuales[var] = modelo_volumen.evaluar_derivada(var, valores_actuales)
            
        return {
            'volumen_actual': volumen_actual,
            'dimensiones_actuales': valores_actuales,
            'derivadas_actuales': derivadas_actuales,
            'optimizacion': optimizacion,
            'area_minima': area_minima,
            'interpretacion': {
                'x': 'Cambio en volumen por unidad de cambio en largo',
                'y': 'Cambio en volumen por unidad de cambio en ancho',
                'z': 'Cambio en volumen por unidad de cambio en alto'
            }
        }
    
    def calcular_eficiencia_termica(self, datos_gabinete: Dict[str, Any],
                                   rango_temperatura: Tuple[float, float] = (40, 80)) -> Dict[str, Any]:
        """
        Calcula la eficiencia térmica en función de la temperatura
        
        Args:
            datos_gabinete: Datos del gabinete
            rango_temperatura: Rango de temperatura a analizar
            
        Returns:
            Datos de eficiencia térmica
        """
        modelo_eficiencia = self.analizador.modelos['eficiencia']
        
        # Generar rango de temperaturas
        temperaturas = np.linspace(rango_temperatura[0], rango_temperatura[1], 50)
        eficiencias = []
        derivadas_eficiencia = []
        
        # Parámetros fijos - usar configuración actual si está disponible
        potencia_util = 250.0
        potencia_total = 300.0
        
        if hasattr(self, 'configuracion_actual') and self.configuracion_actual:
            config = self.configuracion_actual
            if 'potencia_total' in config:
                potencia_total = config['potencia_total']
                potencia_util = potencia_total * 0.85  # 85% de eficiencia típica
        
        valores_base = {
            'P_util': potencia_util,
            'P_total': potencia_total,
            'T_opt': 60.0,
            'alpha': 0.001
        }
        
        for temp in temperaturas:
            valores = valores_base.copy()
            valores['T'] = temp
            
            # Calcular eficiencia
            eficiencia = modelo_eficiencia.evaluar(valores)
            eficiencias.append(eficiencia)
            
            # Calcular derivada dη/dT
            derivada = modelo_eficiencia.evaluar_derivada('T', valores)
            derivadas_eficiencia.append(derivada)
            
        # Encontrar temperatura óptima
        idx_max_eficiencia = np.argmax(eficiencias)
        temp_optima = temperaturas[idx_max_eficiencia]
        eficiencia_maxima = eficiencias[idx_max_eficiencia]
        
        return {
            'temperaturas': temperaturas.tolist(),
            'eficiencias': eficiencias,
            'derivadas': derivadas_eficiencia,
            'temperatura_optima': temp_optima,
            'eficiencia_maxima': eficiencia_maxima,
            'parametros': valores_base,
            'unidades': {
                'temperatura': '°C',
                'eficiencia': 'adimensional',
                'derivada': '1/°C'
            }
        }
    
    def analizar_sensibilidad_parametros(self, datos_gabinete: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza la sensibilidad de la temperatura a cambios en parámetros
        
        Args:
            datos_gabinete: Datos del gabinete
            
        Returns:
            Análisis de sensibilidad
        """
        modelo_termico = self.analizador.modelos['termico']
        
        # Parámetros base
        dimensiones = self.analizador._extraer_dimensiones(datos_gabinete)
        caracteristicas = self.analizador._extraer_caracteristicas(datos_gabinete)
        
        valores_base = {
            'P': 300.0,
            'V': dimensiones['volumen'],
            'A': caracteristicas['area_ventilacion'],
            'Ta': 25.0,
            'k': 0.1,
            'f': caracteristicas['factor_flujo']
        }
        
        # Temperatura base
        temp_base = modelo_termico.evaluar(valores_base)
        
        # Análisis de sensibilidad
        sensibilidad = {}
        parametros_analisis = {
            'P': (200, 400),  # Potencia ±100W
            'V': (dimensiones['volumen'] * 0.5, dimensiones['volumen'] * 1.5),  # Volumen ±50%
            'A': (caracteristicas['area_ventilacion'] * 0.5, caracteristicas['area_ventilacion'] * 1.5),  # Área ±50%
            'f': (0.5, 1.5)  # Factor de flujo ±50%
        }
        
        for param, (min_val, max_val) in parametros_analisis.items():
            valores_temp = valores_base.copy()
            
            # Calcular temperatura con valor mínimo
            valores_temp[param] = min_val
            temp_min = modelo_termico.evaluar(valores_temp)
            
            # Calcular temperatura con valor máximo
            valores_temp[param] = max_val
            temp_max = modelo_termico.evaluar(valores_temp)
            
            # Calcular derivada en el punto base
            derivada_base = modelo_termico.evaluar_derivada(param, valores_base)
            
            # Sensibilidad relativa
            sensibilidad_relativa = abs(derivada_base * valores_base[param] / temp_base)
            
            sensibilidad[param] = {
                'derivada': derivada_base,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'variacion_temp': abs(temp_max - temp_min),
                'sensibilidad_relativa': sensibilidad_relativa,
                'rango_parametro': (min_val, max_val)
            }
            
        return {
            'temperatura_base': temp_base,
            'parametros_base': valores_base,
            'sensibilidad': sensibilidad,
            'ranking_sensibilidad': sorted(
                sensibilidad.items(),
                key=lambda x: x[1]['sensibilidad_relativa'],
                reverse=True
            )
        }
    
    def _calcular_optimizacion(self, datos_gabinete: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula puntos de optimización"""
        # Análisis de temperatura mínima
        curvas_temp = self.calcular_curvas_temperatura(datos_gabinete)
        idx_min_temp = np.argmin(curvas_temp['temperaturas'])
        potencia_optima = curvas_temp['potencias'][idx_min_temp]
        
        # Análisis de eficiencia máxima
        eficiencia_data = self.calcular_eficiencia_termica(datos_gabinete)
        
        # Calcular óptimo de eficiencia más realista basado en la potencia actual
        potencia_actual = 300.0  # Valor por defecto
        if hasattr(self, 'configuracion_actual') and self.configuracion_actual:
            config = self.configuracion_actual
            if 'potencia_total' in config:
                potencia_actual = config['potencia_total']
        
        # El óptimo de eficiencia debe estar cerca del 70-80% de la potencia total
        potencia_eficiencia_optima = potencia_actual * 0.75
        
        return {
            'temperatura_minima': {
                'potencia': potencia_optima,
                'temperatura': curvas_temp['temperaturas'][idx_min_temp]
            },
            'eficiencia_maxima': {
                'potencia': potencia_eficiencia_optima,  # Potencia óptima para eficiencia
                'temperatura': eficiencia_data['temperatura_optima'],
                'eficiencia': eficiencia_data['eficiencia_maxima']
            }
        }
    
    def _encontrar_puntos_criticos(self, datos_gabinete: Dict[str, Any]) -> Dict[str, Any]:
        """Encuentra puntos críticos en las funciones"""
        # Análisis de derivadas
        sensibilidad = self.analizar_sensibilidad_parametros(datos_gabinete)
        
        puntos_criticos = {}
        
        for param, datos in sensibilidad['sensibilidad'].items():
            # Un punto crítico es donde la derivada es cercana a cero
            # o donde hay un cambio significativo en la sensibilidad
            if abs(datos['derivada']) < 0.1:  # Umbral para considerar "crítico"
                puntos_criticos[param] = {
                    'tipo': 'punto_critico',
                    'valor': sensibilidad['parametros_base'][param],
                    'derivada': datos['derivada'],
                    'interpretacion': f'Cambio mínimo en temperatura con variaciones en {param}'
                }
            elif datos['sensibilidad_relativa'] > 1.0:  # Alta sensibilidad
                puntos_criticos[param] = {
                    'tipo': 'alta_sensibilidad',
                    'valor': sensibilidad['parametros_base'][param],
                    'derivada': datos['derivada'],
                    'interpretacion': f'Parámetro muy sensible - pequeños cambios causan grandes efectos'
                }
                
        return puntos_criticos
    
    def _generar_recomendaciones(self, resultados: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recomendaciones = []
        
        # Análisis térmico
        if 'analisis' in resultados and 'termico' in resultados['analisis']:
            temp_estimada = resultados['analisis']['termico']['temperatura_estimada']
            
            if temp_estimada > 75:
                recomendaciones.append("⚠️ Temperatura elevada detectada. Considere mejorar la ventilación.")
            elif temp_estimada > 65:
                recomendaciones.append("🔥 Temperatura moderada. Monitoree el rendimiento térmico.")
            else:
                recomendaciones.append("✅ Temperatura dentro de rangos normales.")
                
        # Análisis de volumen
        if 'analisis' in resultados and 'volumen' in resultados['analisis']:
            eficiencia_espacio = resultados['analisis']['volumen']['eficiencia_espacio']
            
            if eficiencia_espacio < 0.3:
                recomendaciones.append("📦 Gabinete con baja eficiencia de espacio. Considere un diseño más compacto.")
            elif eficiencia_espacio > 0.5:
                recomendaciones.append("✅ Excelente eficiencia de espacio en el gabinete.")
                
        # Análisis de optimización
        if 'optimizacion' in resultados:
            opt_data = resultados['optimizacion']
            recomendaciones.append(
                f"🎯 Para temperatura óptima, opere a {opt_data['eficiencia_maxima']['temperatura']:.1f}°C"
            )
            
        # Puntos críticos
        if 'puntos_criticos' in resultados:
            puntos_alta_sensibilidad = [
                param for param, datos in resultados['puntos_criticos'].items()
                if datos['tipo'] == 'alta_sensibilidad'
            ]
            
            if puntos_alta_sensibilidad:
                recomendaciones.append(
                    f"⚡ Parámetros críticos para optimización: {', '.join(puntos_alta_sensibilidad)}"
                )
                
        return recomendaciones
    
    def obtener_datos_para_grafico(self, tipo_grafico: str, datos_gabinete: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene datos específicos para un tipo de gráfico
        
        Args:
            tipo_grafico: Tipo de gráfico ('temperatura', 'eficiencia', 'volumen', 'sensibilidad')
            datos_gabinete: Datos del gabinete
            
        Returns:
            Datos formateados para el gráfico
        """
        if tipo_grafico == 'temperatura':
            return self.calcular_curvas_temperatura(datos_gabinete)
        elif tipo_grafico == 'eficiencia':
            return self.calcular_eficiencia_termica(datos_gabinete)
        elif tipo_grafico == 'volumen':
            return self.calcular_optimizacion_volumen(datos_gabinete)
        elif tipo_grafico == 'sensibilidad':
            return self.analizar_sensibilidad_parametros(datos_gabinete)
        else:
            raise ValueError(f"Tipo de gráfico no soportado: {tipo_grafico}")
    
    def crear_resumen_matematico(self, datos_gabinete: Dict[str, Any]) -> str:
        """
        Crea un resumen matemático en texto plano del análisis
        
        Args:
            datos_gabinete: Datos del gabinete
            
        Returns:
            Resumen matemático como string
        """
        resumen = []
        resumen.append("=== ANÁLISIS MATEMÁTICO DEL GABINETE ===\n")
        
        # Información básica
        nombre_gabinete = datos_gabinete.get('name', 'Gabinete sin nombre')
        resumen.append(f"Gabinete: {nombre_gabinete}")
        
        # Análisis térmico
        curvas_temp = self.calcular_curvas_temperatura(datos_gabinete)
        temp_promedio = np.mean(curvas_temp['temperaturas'])
        resumen.append(f"\n📊 ANÁLISIS TÉRMICO:")
        resumen.append(f"   Temperatura promedio: {temp_promedio:.1f}°C")
        resumen.append(f"   Rango de potencia analizado: {curvas_temp['potencias'][0]:.0f}W - {curvas_temp['potencias'][-1]:.0f}W")
        
        # Análisis de eficiencia
        eficiencia_data = self.calcular_eficiencia_termica(datos_gabinete)
        resumen.append(f"\n⚡ ANÁLISIS DE EFICIENCIA:")
        resumen.append(f"   Temperatura óptima: {eficiencia_data['temperatura_optima']:.1f}°C")
        resumen.append(f"   Eficiencia máxima: {eficiencia_data['eficiencia_maxima']:.3f}")
        
        # Análisis de sensibilidad
        sensibilidad = self.analizar_sensibilidad_parametros(datos_gabinete)
        resumen.append(f"\n🔍 ANÁLISIS DE SENSIBILIDAD:")
        resumen.append(f"   Temperatura base: {sensibilidad['temperatura_base']:.1f}°C")
        
        # Ranking de sensibilidad
        resumen.append("   Ranking de parámetros por sensibilidad:")
        for i, (param, datos) in enumerate(sensibilidad['ranking_sensibilidad'][:3]):
            resumen.append(f"   {i+1}. {param}: {datos['sensibilidad_relativa']:.3f}")
            
        # Recomendaciones
        resultados_completos = self.analizar_gabinete_completo(datos_gabinete)
        recomendaciones = self._generar_recomendaciones(resultados_completos)
        resumen.append(f"\n💡 RECOMENDACIONES:")
        for rec in recomendaciones:
            resumen.append(f"   {rec}")
            
        return "\n".join(resumen)
