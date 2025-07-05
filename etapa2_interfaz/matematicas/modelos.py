"""
Modelos matemáticos para análisis de componentes PC
Incluye modelos térmicos, de eficiencia, volumen y flujo de aire
"""

import numpy as np
import sympy as sp
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod


class ModeloMatematico(ABC):
    """Clase base para modelos matemáticos"""
    
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.variables = {}
        self.expresion = None
        self.derivadas = {}
        
    @abstractmethod
    def definir_modelo(self, parametros: Dict[str, Any]) -> sp.Expr:
        """Define la expresión matemática del modelo"""
        pass
    
    @abstractmethod
    def calcular_derivadas(self) -> Dict[str, sp.Expr]:
        """Calcula las derivadas del modelo"""
        pass
    
    def evaluar(self, valores: Dict[str, float]) -> float:
        """Evalúa el modelo con valores específicos"""
        if self.expresion is None:
            raise ValueError("Modelo no definido")
        return float(self.expresion.subs(valores))
    
    def evaluar_derivada(self, variable: str, valores: Dict[str, float]) -> float:
        """Evalúa la derivada respecto a una variable"""
        if variable not in self.derivadas:
            raise ValueError(f"Derivada respecto a {variable} no calculada")
        return float(self.derivadas[variable].subs(valores))


class ModeloTermico(ModeloMatematico):
    """Modelo térmico para análisis de temperatura en gabinetes"""
    
    def __init__(self):
        super().__init__("Modelo Térmico")
        self.definir_variables()
        
    def definir_variables(self):
        """Define las variables del modelo térmico"""
        self.variables = {
            'P': sp.Symbol('P', positive=True),  # Potencia disipada (W)
            'V': sp.Symbol('V', positive=True),  # Volumen del gabinete (L)
            'A': sp.Symbol('A', positive=True),  # Área de ventilación (cm²)
            'Ta': sp.Symbol('Ta', positive=True),  # Temperatura ambiente (°C)
            'k': sp.Symbol('k', positive=True),  # Constante térmica del material
            'f': sp.Symbol('f', positive=True),  # Factor de flujo de aire
        }
        
    def definir_modelo(self, parametros: Dict[str, Any] = None) -> sp.Expr:
        """
        Define el modelo térmico:
        T(P,V,A,f) = Ta + (P * k) / (V^0.6 * A^0.3 * f^0.5)
        
        Esta ecuación representa cómo la temperatura interna del gabinete
        depende de la potencia disipada, volumen, área de ventilación y flujo de aire.
        """
        P, V, A, Ta, k, f = [self.variables[var] for var in ['P', 'V', 'A', 'Ta', 'k', 'f']]
        
        # Modelo térmico simplificado basado en principios de transferencia de calor
        self.expresion = Ta + (P * k) / (V**0.6 * A**0.3 * f**0.5)
        
        # Calcular derivadas automáticamente
        self.calcular_derivadas()
        
        return self.expresion
        
    def calcular_derivadas(self) -> Dict[str, sp.Expr]:
        """Calcula las derivadas parciales del modelo térmico"""
        if self.expresion is None:
            raise ValueError("Modelo no definido")
            
        variables_interes = ['P', 'V', 'A', 'f']
        
        for var in variables_interes:
            self.derivadas[var] = sp.diff(self.expresion, self.variables[var])
            
        return self.derivadas
    
    def interpretar_derivadas(self) -> Dict[str, str]:
        """Interpreta el significado físico de las derivadas"""
        interpretaciones = {
            'P': 'Tasa de cambio de temperatura respecto a la potencia disipada',
            'V': 'Cómo el volumen del gabinete afecta la temperatura (negativo = más volumen, menos temperatura)',
            'A': 'Efecto del área de ventilación en la temperatura (negativo = más ventilación, menos temperatura)',
            'f': 'Impacto del flujo de aire en la temperatura (negativo = más flujo, menos temperatura)'
        }
        return interpretaciones


class ModeloEficiencia(ModeloMatematico):
    """Modelo de eficiencia energética del sistema"""
    
    def __init__(self):
        super().__init__("Modelo de Eficiencia")
        self.definir_variables()
        
    def definir_variables(self):
        """Define las variables del modelo de eficiencia"""
        self.variables = {
            'P_util': sp.Symbol('P_util', positive=True),  # Potencia útil (W)
            'P_total': sp.Symbol('P_total', positive=True),  # Potencia total consumida (W)
            'T': sp.Symbol('T', positive=True),  # Temperatura de operación (°C)
            'T_opt': sp.Symbol('T_opt', positive=True),  # Temperatura óptima (°C)
            'alpha': sp.Symbol('alpha', positive=True),  # Coeficiente de eficiencia térmica
        }
        
    def definir_modelo(self, parametros: Dict[str, Any] = None) -> sp.Expr:
        """
        Define el modelo de eficiencia:
        η(P_util, P_total, T) = (P_util / P_total) * exp(-alpha * (T - T_opt)²)
        
        La eficiencia depende de la relación potencia útil/total y
        se ve afectada por la temperatura de operación.
        """
        P_util, P_total, T, T_opt, alpha = [
            self.variables[var] for var in ['P_util', 'P_total', 'T', 'T_opt', 'alpha']
        ]
        
        # Eficiencia básica
        eficiencia_base = P_util / P_total
        
        # Factor de corrección térmica (gaussiano)
        factor_termico = sp.exp(-alpha * (T - T_opt)**2)
        
        # Modelo completo
        self.expresion = eficiencia_base * factor_termico
        
        # Calcular derivadas
        self.calcular_derivadas()
        
        return self.expresion
        
    def calcular_derivadas(self) -> Dict[str, sp.Expr]:
        """Calcula las derivadas del modelo de eficiencia"""
        if self.expresion is None:
            raise ValueError("Modelo no definido")
            
        variables_interes = ['P_util', 'P_total', 'T']
        
        for var in variables_interes:
            self.derivadas[var] = sp.diff(self.expresion, self.variables[var])
            
        return self.derivadas
    
    def encontrar_temperatura_optima(self) -> sp.Expr:
        """Encuentra la temperatura óptima derivando respecto a T"""
        if 'T' not in self.derivadas:
            return None
        
        # Resolver dη/dT = 0
        temp_optima = sp.solve(self.derivadas['T'], self.variables['T'])
        return temp_optima


class ModeloVolumen(ModeloMatematico):
    """Modelo de optimización de volumen del gabinete"""
    
    def __init__(self):
        super().__init__("Modelo de Volumen")
        self.definir_variables()
        
    def definir_variables(self):
        """Define las variables del modelo de volumen"""
        self.variables = {
            'x': sp.Symbol('x', positive=True),  # Largo (cm)
            'y': sp.Symbol('y', positive=True),  # Ancho (cm)
            'z': sp.Symbol('z', positive=True),  # Alto (cm)
            'A_min': sp.Symbol('A_min', positive=True),  # Área mínima requerida
            'k_material': sp.Symbol('k_material', positive=True),  # Costo por unidad de área
        }
        
    def definir_modelo(self, parametros: Dict[str, Any] = None) -> sp.Expr:
        """
        Define el modelo de volumen a optimizar:
        V(x,y,z) = x * y * z
        
        Sujeto a restricciones de área mínima y aspectos prácticos
        """
        x, y, z = [self.variables[var] for var in ['x', 'y', 'z']]
        
        # Volumen del gabinete
        self.expresion = x * y * z
        
        # Calcular derivadas
        self.calcular_derivadas()
        
        return self.expresion
        
    def calcular_derivadas(self) -> Dict[str, sp.Expr]:
        """Calcula las derivadas del modelo de volumen"""
        if self.expresion is None:
            raise ValueError("Modelo no definido")
            
        variables_interes = ['x', 'y', 'z']
        
        for var in variables_interes:
            self.derivadas[var] = sp.diff(self.expresion, self.variables[var])
            
        return self.derivadas
    
    def optimizar_con_restricciones(self, area_min: float) -> Dict[str, Any]:
        """
        Optimiza el volumen sujeto a restricciones de área mínima
        usando multiplicadores de Lagrange
        """
        x, y, z, A_min = [self.variables[var] for var in ['x', 'y', 'z', 'A_min']]
        
        # Restricción: área de la base debe ser >= A_min
        restriccion = x * y - A_min
        
        # Función Lagrangiana
        lam = sp.Symbol('lambda')
        L = self.expresion - lam * restriccion
        
        # Condiciones de primer orden
        condiciones = [
            sp.diff(L, x),
            sp.diff(L, y),
            sp.diff(L, z),
            sp.diff(L, lam)
        ]
        
        return {
            'lagrangiana': L,
            'condiciones': condiciones,
            'restriccion': restriccion
        }


class ModeloFlujoAire(ModeloMatematico):
    """Modelo de flujo de aire en el gabinete"""
    
    def __init__(self):
        super().__init__("Modelo de Flujo de Aire")
        self.definir_variables()
        
    def definir_variables(self):
        """Define las variables del modelo de flujo de aire"""
        self.variables = {
            'v': sp.Symbol('v', positive=True),  # Velocidad del ventilador (RPM)
            'A_entrada': sp.Symbol('A_entrada', positive=True),  # Área de entrada (cm²)
            'A_salida': sp.Symbol('A_salida', positive=True),  # Área de salida (cm²)
            'P_presion': sp.Symbol('P_presion', positive=True),  # Presión diferencial (Pa)
            'mu': sp.Symbol('mu', positive=True),  # Viscosidad del aire
            'rho': sp.Symbol('rho', positive=True),  # Densidad del aire
        }
        
    def definir_modelo(self, parametros: Dict[str, Any] = None) -> sp.Expr:
        """
        Define el modelo de flujo de aire:
        Q(v, A, P) = k * v * A * sqrt(P/rho)
        
        Donde Q es el caudal de aire
        """
        v, A_entrada, A_salida, P_presion, rho = [
            self.variables[var] for var in ['v', 'A_entrada', 'A_salida', 'P_presion', 'rho']
        ]
        
        # Área efectiva (mínimo entre entrada y salida)
        A_efectiva = sp.Min(A_entrada, A_salida)
        
        # Caudal de aire (modelo simplificado)
        k = sp.Symbol('k', positive=True)  # Constante de proporcionalidad
        self.expresion = k * v * A_efectiva * sp.sqrt(P_presion / rho)
        
        # Calcular derivadas
        self.calcular_derivadas()
        
        return self.expresion
        
    def calcular_derivadas(self) -> Dict[str, sp.Expr]:
        """Calcula las derivadas del modelo de flujo de aire"""
        if self.expresion is None:
            raise ValueError("Modelo no definido")
            
        variables_interes = ['v', 'A_entrada', 'A_salida', 'P_presion']
        
        for var in variables_interes:
            try:
                self.derivadas[var] = sp.diff(self.expresion, self.variables[var])
            except:
                # Para casos complejos como Min(), usar aproximación numérica
                self.derivadas[var] = sp.Symbol(f'd_flujo_d_{var}')
                
        return self.derivadas


class AnalizadorOptimizacion:
    """Clase para análisis de optimización usando los modelos matemáticos"""
    
    def __init__(self):
        self.modelos = {
            'termico': ModeloTermico(),
            'eficiencia': ModeloEficiencia(),
            'volumen': ModeloVolumen(),
            'flujo_aire': ModeloFlujoAire()
        }
        
    def inicializar_modelos(self):
        """Inicializa todos los modelos matemáticos"""
        for modelo in self.modelos.values():
            modelo.definir_modelo()
            
    def analizar_gabinete(self, datos_gabinete: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza un gabinete específico usando todos los modelos
        
        Args:
            datos_gabinete: Datos del gabinete a analizar
            
        Returns:
            Diccionario con análisis completo
        """
        # Extraer dimensiones y características
        dimensiones = self._extraer_dimensiones(datos_gabinete)
        caracteristicas = self._extraer_caracteristicas(datos_gabinete)
        
        resultados = {
            'gabinete': datos_gabinete.get('name', 'Gabinete sin nombre'),
            'dimensiones': dimensiones,
            'analisis': {}
        }
        
        # Análisis térmico
        if 'termico' in self.modelos:
            resultados['analisis']['termico'] = self._analizar_termico(dimensiones, caracteristicas)
            
        # Análisis de eficiencia
        if 'eficiencia' in self.modelos:
            resultados['analisis']['eficiencia'] = self._analizar_eficiencia(dimensiones, caracteristicas)
            
        # Análisis de volumen
        if 'volumen' in self.modelos:
            resultados['analisis']['volumen'] = self._analizar_volumen(dimensiones)
            
        # Análisis de flujo de aire
        if 'flujo_aire' in self.modelos:
            resultados['analisis']['flujo_aire'] = self._analizar_flujo_aire(dimensiones, caracteristicas)
            
        return resultados
    
    def _extraer_dimensiones(self, datos_gabinete: Dict[str, Any]) -> Dict[str, float]:
        """Extrae las dimensiones del gabinete"""
        # Buscar dimensiones en la estructura de datos
        dimensiones = {
            'largo': 0,
            'ancho': 0,
            'alto': 0,
            'volumen': 0
        }
        
        # Intentar extraer de diferentes campos posibles
        if 'dimensions' in datos_gabinete:
            dim_data = datos_gabinete['dimensions']
            if isinstance(dim_data, dict):
                dimensiones['largo'] = dim_data.get('length', {}).get('value', 0) or 0
                dimensiones['ancho'] = dim_data.get('width', {}).get('value', 0) or 0
                dimensiones['alto'] = dim_data.get('height', {}).get('value', 0) or 0
                
        # Calcular volumen si tenemos las dimensiones
        if all(dimensiones[key] > 0 for key in ['largo', 'ancho', 'alto']):
            dimensiones['volumen'] = dimensiones['largo'] * dimensiones['ancho'] * dimensiones['alto']
        else:
            # Valores por defecto para gabinetes típicos
            dimensiones = {
                'largo': 45.0,  # cm
                'ancho': 20.0,  # cm
                'alto': 45.0,   # cm
                'volumen': 40.5  # L
            }
            
        return dimensiones
    
    def _extraer_caracteristicas(self, datos_gabinete: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae características térmicas y de ventilación"""
        caracteristicas = {
            'area_ventilacion': 100.0,  # cm² (estimación)
            'num_ventiladores': 2,
            'factor_flujo': 1.0,
            'material': 'steel'
        }
        
        # Intentar extraer datos reales
        if 'ventilation' in datos_gabinete:
            vent_data = datos_gabinete['ventilation']
            if isinstance(vent_data, dict):
                caracteristicas['num_ventiladores'] = vent_data.get('fan_count', 2)
                
        return caracteristicas
    
    def _analizar_termico(self, dimensiones: Dict[str, float], caracteristicas: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análisis térmico"""
        modelo = self.modelos['termico']
        
        # Valores típicos para evaluación
        valores = {
            'P': 300.0,  # 300W de potencia total
            'V': dimensiones['volumen'],  # Volumen del gabinete
            'A': caracteristicas['area_ventilacion'],  # Área de ventilación
            'Ta': 25.0,  # Temperatura ambiente
            'k': 0.1,   # Constante térmica
            'f': caracteristicas['factor_flujo']  # Factor de flujo
        }
        
        # Evaluar temperatura
        temp_estimada = modelo.evaluar(valores)
        
        # Evaluar derivadas
        derivadas_evaluadas = {}
        for var in ['P', 'V', 'A', 'f']:
            try:
                derivadas_evaluadas[var] = modelo.evaluar_derivada(var, valores)
            except:
                derivadas_evaluadas[var] = 0.0
                
        return {
            'temperatura_estimada': temp_estimada,
            'derivadas': derivadas_evaluadas,
            'interpretacion': modelo.interpretar_derivadas()
        }
    
    def _analizar_eficiencia(self, dimensiones: Dict[str, float], caracteristicas: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análisis de eficiencia"""
        modelo = self.modelos['eficiencia']
        
        # Valores típicos
        valores = {
            'P_util': 250.0,  # Potencia útil
            'P_total': 300.0,  # Potencia total
            'T': 65.0,  # Temperatura de operación
            'T_opt': 60.0,  # Temperatura óptima
            'alpha': 0.001  # Coeficiente térmico
        }
        
        eficiencia = modelo.evaluar(valores)
        
        # Evaluar derivadas
        derivadas_evaluadas = {}
        for var in ['P_util', 'P_total', 'T']:
            try:
                derivadas_evaluadas[var] = modelo.evaluar_derivada(var, valores)
            except:
                derivadas_evaluadas[var] = 0.0
                
        return {
            'eficiencia': eficiencia,
            'derivadas': derivadas_evaluadas,
            'temperatura_optima': valores['T_opt']
        }
    
    def _analizar_volumen(self, dimensiones: Dict[str, float]) -> Dict[str, Any]:
        """Realiza análisis de volumen"""
        modelo = self.modelos['volumen']
        
        valores = {
            'x': dimensiones['largo'],
            'y': dimensiones['ancho'],
            'z': dimensiones['alto']
        }
        
        volumen = modelo.evaluar(valores)
        
        # Evaluar derivadas
        derivadas_evaluadas = {}
        for var in ['x', 'y', 'z']:
            try:
                derivadas_evaluadas[var] = modelo.evaluar_derivada(var, valores)
            except:
                derivadas_evaluadas[var] = 0.0
                
        return {
            'volumen': volumen,
            'derivadas': derivadas_evaluadas,
            'eficiencia_espacio': volumen / (dimensiones['largo'] + dimensiones['ancho'] + dimensiones['alto'])
        }
    
    def _analizar_flujo_aire(self, dimensiones: Dict[str, float], caracteristicas: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análisis de flujo de aire"""
        modelo = self.modelos['flujo_aire']
        
        valores = {
            'v': 1200.0,  # RPM típico
            'A_entrada': 80.0,  # cm²
            'A_salida': 80.0,   # cm²
            'P_presion': 50.0,  # Pa
            'rho': 1.225  # kg/m³ (aire a 20°C)
        }
        
        try:
            flujo = modelo.evaluar(valores)
        except:
            flujo = 30.0  # CFM estimado
            
        return {
            'flujo_estimado': flujo,
            'parametros': valores,
            'eficiencia_ventilacion': flujo / caracteristicas['num_ventiladores']
        }


def crear_analizador_optimizacion() -> AnalizadorOptimizacion:
    """Crea y inicializa un analizador de optimización"""
    analizador = AnalizadorOptimizacion()
    analizador.inicializar_modelos()
    return analizador
