"""
Calculadora matemática específica para análisis de builds de PC
Aplica cálculo diferencial a parámetros térmicos y de rendimiento
"""

import numpy as np
import math
from typing import Dict, List, Any, Tuple, Optional
from scipy.optimize import minimize_scalar
try:
    from scipy.misc import derivative
except ImportError:
    # Implementación manual de derivada numérica si scipy no está disponible
    def derivative(func, x, dx=1e-6):
        return (func(x + dx) - func(x - dx)) / (2 * dx)

class CalculadoraBuildMatematica:
    """Calculadora matemática para análisis de builds usando cálculo diferencial"""
    
    def __init__(self):
        self.build_info = None
        self.parametros_termicos = {}
        self.temperatura_ambiente = 25.0
        self.factor_ventilacion_ajuste = 1.0
        
    def establecer_build(self, build_info: Dict[str, Any]):
        """Establece la información de la build actual"""
        self.build_info = build_info
        self.parametros_termicos = build_info.get('parametros_termicos', {})
    
    def configurar_build(self, parametros: Dict[str, Any]):
        """Configura la build con parámetros específicos"""
        self.build_info = parametros
        self.parametros_termicos = parametros.copy()
        
        # Establecer parámetros térmicos específicos
        if 'temperatura_ambiente' in parametros:
            self.temperatura_ambiente = parametros['temperatura_ambiente']
        if 'factor_ventilacion' in parametros:
            self.factor_ventilacion_ajuste = parametros['factor_ventilacion']
    
    def actualizar_parametros(self, parametros: Dict[str, Any]):
        """Actualiza los parámetros existentes"""
        if self.parametros_termicos:
            self.parametros_termicos.update(parametros)
        else:
            self.parametros_termicos = parametros.copy()
            
        # Actualizar parámetros específicos
        if 'temperatura_ambiente' in parametros:
            self.temperatura_ambiente = parametros['temperatura_ambiente']
        if 'factor_ventilacion' in parametros:
            self.factor_ventilacion_ajuste = parametros['factor_ventilacion']
    
    def establecer_parametros_ambiente(self, temp_ambiente: float, factor_ventilacion: float):
        """Establece parámetros ambientales"""
        self.temperatura_ambiente = temp_ambiente
        self.factor_ventilacion_ajuste = factor_ventilacion
    
    def funcion_temperatura(self, potencia: float) -> float:
        """
        Función T(P) = T_ambiente + k * P^n / (ventilacion * sqrt(volumen))
        Modelo térmico no lineal realista
        """
        if not self.parametros_termicos:
            # Valores por defecto si no hay datos
            k = 0.15
            n = 1.3
            ventilacion = 1.0
            volumen = 40.0
        else:
            # Constantes basadas en la build
            k = 0.12  # Constante térmica base
            n = 1.25  # Exponente no lineal (mayor potencia = más calor por watt)
            
            ventilacion = self.parametros_termicos.get('factor_ventilacion', 1.0) * self.factor_ventilacion_ajuste
            volumen = self.parametros_termicos.get('volumen_interno', 40.0)
            
            # Ajustar k según capacidad de enfriamiento
            capacidad_enfriamiento = self.parametros_termicos.get('capacidad_enfriamiento', 0)
            if capacidad_enfriamiento > 0:
                # Mejor enfriamiento reduce k
                k = k * (150.0 / max(capacidad_enfriamiento, 50.0))
        
        # Modelo térmico - validar potencia positiva
        potencia_segura = max(0.1, abs(potencia))  # Evitar valores negativos o cero
        return self.temperatura_ambiente + k * (potencia_segura ** n) / (ventilacion * math.sqrt(volumen))
    
    def derivada_temperatura(self, potencia: float) -> float:
        """
        Calcula dT/dP - Sensibilidad térmica
        Indica cuánto aumenta la temperatura por cada watt adicional
        """
        return derivative(self.funcion_temperatura, potencia, dx=0.1)
    
    def segunda_derivada_temperatura(self, potencia: float) -> float:
        """
        Calcula d²T/dP² - Concavidad de la curva térmica
        Positiva: aceleración térmica (empeora rápidamente)
        Negativa: desaceleración térmica (mejora la eficiencia)
        """
        return derivative(self.derivada_temperatura, potencia, dx=0.1)
    
    def puntos_criticos_temperatura(self, rango_potencia: Tuple[float, float] = (50, 800)) -> List[Dict[str, float]]:
        """
        Encuentra puntos críticos donde dT/dP cambia significativamente
        """
        puntos_criticos = []
        potencias = np.linspace(rango_potencia[0], rango_potencia[1], 200)
        
        derivadas = [self.derivada_temperatura(p) for p in potencias]
        segundas_derivadas = [self.segunda_derivada_temperatura(p) for p in potencias]
        
        # Buscar puntos donde la segunda derivada cambia de signo (inflexión)
        for i in range(1, len(segundas_derivadas)):
            if segundas_derivadas[i-1] * segundas_derivadas[i] < 0:  # Cambio de signo
                punto = {
                    'potencia': potencias[i],
                    'temperatura': self.funcion_temperatura(potencias[i]),
                    'derivada_primera': derivadas[i],
                    'derivada_segunda': segundas_derivadas[i],
                    'tipo': 'inflexion'
                }
                puntos_criticos.append(punto)
        
        # Buscar mínimos locales de la derivada (máxima eficiencia térmica)
        for i in range(1, len(derivadas)-1):
            if derivadas[i] < derivadas[i-1] and derivadas[i] < derivadas[i+1]:
                punto = {
                    'potencia': potencias[i],
                    'temperatura': self.funcion_temperatura(potencias[i]),
                    'derivada_primera': derivadas[i],
                    'derivada_segunda': segundas_derivadas[i],
                    'tipo': 'eficiencia_maxima'
                }
                puntos_criticos.append(punto)
        
        return puntos_criticos
    
    def eficiencia_termica(self, temperatura: float) -> float:
        """
        Función de eficiencia η(T) basada en curva realista de rendimiento
        η(T) = 1 / (1 + e^((T - T_optima) / sigma))
        Función sigmoide que decrece suavemente
        """
        temp_optima = 65.0  # °C - temperatura óptima de operación
        sigma = 8.0  # Suavidad de la curva
        
        return 1.0 / (1.0 + math.exp((temperatura - temp_optima) / sigma))
    
    def derivada_eficiencia(self, temperatura: float) -> float:
        """
        Calcula dη/dT - Sensibilidad de eficiencia a la temperatura
        Negativa: la eficiencia decrece con el aumento de temperatura
        """
        return derivative(self.eficiencia_termica, temperatura, dx=0.01)
    
    def funcion_eficiencia_vs_potencia(self, potencia: float) -> float:
        """
        Eficiencia como función de potencia: η(P) = η(T(P))
        Composición de funciones para análisis completo
        """
        temperatura = self.funcion_temperatura(potencia)
        return self.eficiencia_termica(temperatura)
    
    def derivada_eficiencia_potencia(self, potencia: float) -> float:
        """
        Calcula dη/dP usando regla de la cadena:
        dη/dP = (dη/dT) * (dT/dP)
        """
        temperatura = self.funcion_temperatura(potencia)
        dη_dT = self.derivada_eficiencia(temperatura)
        dT_dP = self.derivada_temperatura(potencia)
        return dη_dT * dT_dP
    
    def optimizar_potencia(self, objetivo: str = 'eficiencia') -> Dict[str, float]:
        """
        Encuentra la potencia óptima usando cálculo de optimización
        """
        # Obtener potencia actual del build
        potencia_actual = self.parametros_termicos.get('potencia_total', 300.0)
        
        # Definir rangos realistas basados en la potencia actual
        potencia_min = max(50, potencia_actual * 0.5)  # Mínimo 50W o 50% de la potencia actual
        potencia_max = min(800, potencia_actual * 1.5)  # Máximo 800W o 150% de la potencia actual
        
        if objetivo == 'eficiencia':
            # Maximizar eficiencia: buscar donde dη/dP = 0
            def neg_eficiencia(p):
                return -self.funcion_eficiencia_vs_potencia(p)
            
            resultado = minimize_scalar(neg_eficiencia, bounds=(potencia_min, potencia_max), method='bounded')
            potencia_optima = resultado.x
            
            # Si el resultado es muy bajo, usar un valor más realista
            if potencia_optima < potencia_actual * 0.7:
                potencia_optima = potencia_actual * 0.8  # 80% de la potencia actual
            
        elif objetivo == 'temperatura':
            # Minimizar temperatura por watt: buscar el mejor compromiso
            def ratio_temp_potencia(p):
                return self.funcion_temperatura(p) / p
            
            resultado = minimize_scalar(ratio_temp_potencia, bounds=(potencia_min, potencia_max), method='bounded')
            potencia_optima = resultado.x
        
        else:
            potencia_optima = potencia_actual  # Usar la potencia actual como valor por defecto
        
        return {
            'potencia_optima': potencia_optima,
            'temperatura_optima': self.funcion_temperatura(potencia_optima),
            'eficiencia_optima': self.funcion_eficiencia_vs_potencia(potencia_optima),
            'derivada_temp': self.derivada_temperatura(potencia_optima),
            'derivada_eficiencia': self.derivada_eficiencia_potencia(potencia_optima)
        }
    
    def analisis_sensibilidad(self, parametro: str, variacion: float = 0.1) -> Dict[str, float]:
        """
        Análisis de sensibilidad usando derivadas parciales numéricas
        """
        potencia_referencia = self.parametros_termicos.get('potencia_total', 300.0)
        temp_base = self.funcion_temperatura(potencia_referencia)
        
        # Guardar valores originales
        factor_vent_original = self.factor_ventilacion_ajuste
        temp_ambiente_original = self.temperatura_ambiente
        
        # Variar parámetro específico
        if parametro == 'ventilacion':
            self.factor_ventilacion_ajuste *= (1 + variacion)
            temp_variada = self.funcion_temperatura(potencia_referencia)
            self.factor_ventilacion_ajuste = factor_vent_original  # Restaurar
            
        elif parametro == 'temperatura_ambiente':
            self.temperatura_ambiente += variacion * 10  # Variación de 1°C
            temp_variada = self.funcion_temperatura(potencia_referencia)
            self.temperatura_ambiente = temp_ambiente_original  # Restaurar
            
        elif parametro == 'volumen':
            # Simular cambio de volumen modificando temporalmente los parámetros
            volumen_original = self.parametros_termicos.get('volumen_interno', 40.0)
            self.parametros_termicos['volumen_interno'] = volumen_original * (1 + variacion)
            temp_variada = self.funcion_temperatura(potencia_referencia)
            self.parametros_termicos['volumen_interno'] = volumen_original  # Restaurar
            
        else:
            temp_variada = temp_base
        
        # Calcular sensibilidad
        if parametro == 'temperatura_ambiente':
            sensibilidad_absoluta = abs(temp_variada - temp_base)
            sensibilidad_relativa = sensibilidad_absoluta / (variacion * 10)
        else:
            sensibilidad_absoluta = abs(temp_variada - temp_base)
            sensibilidad_relativa = sensibilidad_absoluta / (temp_base * variacion) if temp_base > 0 else 0
        
        return {
            'parametro': parametro,
            'sensibilidad_absoluta': sensibilidad_absoluta,
            'sensibilidad_relativa': sensibilidad_relativa,
            'temperatura_base': temp_base,
            'temperatura_variada': temp_variada,
            'impacto_porcentual': (sensibilidad_absoluta / temp_base) * 100 if temp_base > 0 else 0
        }
    
    def generar_curvas_analisis(self, num_puntos: int = 100) -> Dict[str, Any]:
        """
        Genera datos para gráficos de análisis matemático
        """
        potencia_min = 50.0
        potencia_max = min(800.0, self.parametros_termicos.get('potencia_total', 300.0) * 2)
        potencias = np.linspace(potencia_min, potencia_max, num_puntos)
        
        # Calcular todas las curvas
        temperaturas = [self.funcion_temperatura(p) for p in potencias]
        eficiencias = [self.funcion_eficiencia_vs_potencia(p) for p in potencias]
        derivadas_temp = [self.derivada_temperatura(p) for p in potencias]
        derivadas_eficiencia = [self.derivada_eficiencia_potencia(p) for p in potencias]
        
        # Puntos críticos
        puntos_criticos = self.puntos_criticos_temperatura((potencia_min, potencia_max))
        
        # Optimización
        optimizacion_eficiencia = self.optimizar_potencia('eficiencia')
        optimizacion_temperatura = self.optimizar_potencia('temperatura')
        
        return {
            'potencias': potencias.tolist(),
            'temperaturas': temperaturas,
            'eficiencias': eficiencias,
            'derivadas_temperatura': derivadas_temp,
            'derivadas_eficiencia': derivadas_eficiencia,
            'puntos_criticos': puntos_criticos,
            'optimizacion_eficiencia': optimizacion_eficiencia,
            'optimizacion_temperatura': optimizacion_temperatura,
            'potencia_build': self.parametros_termicos.get('potencia_total', 300.0)
        }
    
    def crear_resumen_matematico(self) -> str:
        """
        Crea un resumen matemático detallado del análisis
        """
        if not self.build_info:
            return "No hay información de build disponible para análisis."
        
        # Obtener datos de análisis
        curvas = self.generar_curvas_analisis()
        potencia_build = curvas['potencia_build']
        
        # Análisis en potencia actual de la build
        temp_actual = self.funcion_temperatura(potencia_build)
        eficiencia_actual = self.funcion_eficiencia_vs_potencia(potencia_build)
        sensibilidad_temp = self.derivada_temperatura(potencia_build)
        sensibilidad_eficiencia = self.derivada_eficiencia_potencia(potencia_build)
        
        # Análisis de sensibilidad
        sens_ventilacion = self.analisis_sensibilidad('ventilacion')
        sens_volumen = self.analisis_sensibilidad('volumen')
        sens_temp_ambiente = self.analisis_sensibilidad('temperatura_ambiente')
        
        resumen = f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           ANÁLISIS MATEMÁTICO DE BUILD PC                           ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

📊 PARÁMETROS DE LA BUILD:
────────────────────────────────────────────────────────────────────────────────────────
• Potencia Total: {potencia_build:.1f} W
• Temperatura Ambiente: {self.temperatura_ambiente:.1f} °C
• Factor de Ventilación: {self.factor_ventilacion_ajuste:.2f}x
• Volumen Interno: {self.parametros_termicos.get('volumen_interno', 40.0):.1f} L

🌡️ ANÁLISIS TÉRMICO (usando Cálculo Diferencial):
────────────────────────────────────────────────────────────────────────────────────────
• Modelo: T(P) = T₀ + k·P^n / (v·√V)
• Temperatura Actual: {temp_actual:.1f} °C
• Sensibilidad Térmica (dT/dP): {sensibilidad_temp:.3f} °C/W
  ↳ Por cada watt adicional, la temperatura aumenta {sensibilidad_temp:.3f} °C

⚡ ANÁLISIS DE EFICIENCIA:
────────────────────────────────────────────────────────────────────────────────────────
• Modelo: η(T) = 1/(1 + e^((T-T₀)/σ))
• Eficiencia Actual: {eficiencia_actual:.1%}
• Sensibilidad de Eficiencia (dη/dP): {sensibilidad_eficiencia:.6f} /W
• Óptimo de Eficiencia: {curvas['optimizacion_eficiencia']['potencia_optima']:.1f} W 
  → {curvas['optimizacion_eficiencia']['eficiencia_optima']:.1%} eficiencia

🔍 ANÁLISIS DE SENSIBILIDAD (Derivadas Parciales):
────────────────────────────────────────────────────────────────────────────────────────
• Ventilación:
  ∂T/∂v = {sens_ventilacion['sensibilidad_relativa']:.3f} °C por 10% cambio
  Impacto: {sens_ventilacion['impacto_porcentual']:.2f}% en temperatura

• Volumen del Case:
  ∂T/∂V = {sens_volumen['sensibilidad_relativa']:.3f} °C por 10% cambio
  Impacto: {sens_volumen['impacto_porcentual']:.2f}% en temperatura

• Temperatura Ambiente:
  ∂T/∂T₀ = {sens_temp_ambiente['sensibilidad_relativa']:.3f} °C por °C ambiente
  Impacto: {sens_temp_ambiente['impacto_porcentual']:.2f}% por grado

📈 PUNTOS CRÍTICOS ENCONTRADOS:
────────────────────────────────────────────────────────────────────────────────────────"""

        # Agregar puntos críticos
        puntos_criticos = curvas['puntos_criticos']
        if puntos_criticos:
            for i, punto in enumerate(puntos_criticos[:3]):  # Mostrar máximo 3
                resumen += f"""
• Punto {i+1} ({punto['tipo']}):
  Potencia: {punto['potencia']:.1f} W → Temperatura: {punto['temperatura']:.1f} °C
  dT/dP: {punto['derivada_primera']:.4f}, d²T/dP²: {punto['derivada_segunda']:.6f}"""
        else:
            resumen += "\n• No se encontraron puntos críticos significativos en el rango analizado"

        resumen += f"""

💡 RECOMENDACIONES MATEMÁTICAS:
────────────────────────────────────────────────────────────────────────────────────────"""

        # Recomendaciones basadas en análisis
        if sensibilidad_temp > 0.2:
            resumen += f"\n⚠️  Alta sensibilidad térmica ({sensibilidad_temp:.3f} °C/W)"
            resumen += "\n   → Considerar mejor refrigeración o reducir potencia"

        if eficiencia_actual < 0.8:
            resumen += f"\n⚠️  Baja eficiencia térmica ({eficiencia_actual:.1%})"
            resumen += "\n   → La build opera fuera del rango óptimo"

        if sens_ventilacion['impacto_porcentual'] > 5:
            resumen += f"\n💨 Ventilación crítica (impacto: {sens_ventilacion['impacto_porcentual']:.1f}%)"
            resumen += "\n   → Mejorar flujo de aire tendría gran impacto"

        if sens_volumen['impacto_porcentual'] > 3:
            resumen += f"\n📦 Volumen limitante (impacto: {sens_volumen['impacto_porcentual']:.1f}%)"
            resumen += "\n   → Case más grande mejoraría significativamente las temperaturas"

        # Rango óptimo
        opt_eficiencia = curvas['optimizacion_eficiencia']
        diferencia_optima = abs(potencia_build - opt_eficiencia['potencia_optima'])
        if diferencia_optima > 50:
            resumen += f"\n🎯 Potencia subóptima (diferencia: {diferencia_optima:.1f} W del óptimo)"
            resumen += f"\n   → Óptimo teórico: {opt_eficiencia['potencia_optima']:.1f} W"

        resumen += "\n\n" + "="*88
        resumen += "\nAnálisis generado usando cálculo diferencial aplicado a sistemas térmicos PC"

        return resumen
    
    def calcular_analisis_termico(self) -> Dict[str, Any]:
        """Calcula análisis térmico del build"""
        if not self.parametros_termicos:
            return {}
        
        # Rango de potencia para análisis
        potencia_min = 50
        potencia_max = min(800, self.parametros_termicos.get('potencia_total', 300) * 2)
        
        # Generar datos para gráfico
        potencias = np.linspace(potencia_min, potencia_max, 50)
        temperaturas = [self.funcion_temperatura(p) for p in potencias]
        derivadas = [self.derivada_temperatura(p) for p in potencias]
        
        # Puntos críticos
        puntos_criticos = self.puntos_criticos_temperatura((potencia_min, potencia_max))
        
        return {
            'potencias': potencias.tolist(),
            'temperaturas': temperaturas,
            'derivadas': derivadas,
            'puntos_criticos': puntos_criticos,
            'temperatura_maxima': max(temperaturas),
            'temperatura_minima': min(temperaturas),
            'potencia_optima': self.optimizar_potencia('temperatura')
        }
    
    def calcular_analisis_eficiencia(self) -> Dict[str, Any]:
        """Calcula análisis de eficiencia del build"""
        if not self.parametros_termicos:
            return {}
        
        # Rango de potencia para análisis
        potencia_min = 50
        potencia_max = min(800, self.parametros_termicos.get('potencia_total', 300) * 2)
        
        # Generar datos para gráfico
        potencias = np.linspace(potencia_min, potencia_max, 50)
        eficiencias = [self.funcion_eficiencia_vs_potencia(p) for p in potencias]
        derivadas_eff = [self.derivada_eficiencia_potencia(p) for p in potencias]
        
        # Punto óptimo de eficiencia
        optimo_eficiencia = self.optimizar_potencia('eficiencia')
        
        return {
            'potencias': potencias.tolist(),
            'eficiencias': eficiencias,
            'derivadas_eficiencia': derivadas_eff,
            'eficiencia_maxima': max(eficiencias) if eficiencias else 0,
            'eficiencia_minima': min(eficiencias) if eficiencias else 0,
            'punto_optimo': optimo_eficiencia
        }
    
    def calcular_analisis_sensibilidad(self) -> Dict[str, Any]:
        """Calcula análisis de sensibilidad del build"""
        if not self.parametros_termicos:
            return {}
        
        # Análisis de sensibilidad para diferentes parámetros
        sensibilidades = {}
        
        parametros_analizar = ['potencia_total', 'factor_ventilacion', 'temperatura_ambiente']
        
        for param in parametros_analizar:
            if param in self.parametros_termicos:
                sens = self.analisis_sensibilidad(param)
                sensibilidades[param] = sens
        
        return {
            'sensibilidades': sensibilidades,
            'parametro_mas_sensible': max(sensibilidades.keys(), 
                                        key=lambda k: abs(sensibilidades[k].get('sensibilidad_relativa', 0))) 
                                        if sensibilidades else None
        }
    
    def generar_resumen_completo(self) -> str:
        """Genera un resumen completo del análisis"""
        if not self.parametros_termicos:
            return "Sin datos de build disponibles para análisis"
        
        resumen = self.crear_resumen_matematico()
        
        # Agregar información adicional
        resumen += f"\n\n=== PARÁMETROS DEL BUILD ===\n"
        
        for key, value in self.parametros_termicos.items():
            if isinstance(value, (int, float)):
                resumen += f"• {key}: {value:.2f}\n"
            else:
                resumen += f"• {key}: {value}\n"
        
        return resumen
