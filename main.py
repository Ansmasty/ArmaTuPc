"""
Optimización del armado de un PC: cálculo de volúmenes y consumo energético
Proyecto de investigación para configuración eficiente de componentes
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

@dataclass
class Componente:
    """Clase base para componentes del PC"""
    nombre: str
    precio: float
    consumo_watts: float  # Consumo en watts
    dimensiones: Tuple[float, float, float]  # (largo, ancho, alto) en mm
    marca: str
    
    def volumen(self) -> float:
        """Calcula el volumen del componente en mm³"""
        return self.dimensiones[0] * self.dimensiones[1] * self.dimensiones[2]

@dataclass
class Gabinete(Componente):
    """Gabinete del PC"""
    volumen_interno: float  # mm³
    tipo: str  # ATX, Micro-ATX, Mini-ITX
    
@dataclass
class PlacaBase(Componente):
    """Placa base/motherboard"""
    factor_forma: str  # ATX, Micro-ATX, Mini-ITX
    sockets_ram: int
    socket_cpu: str

@dataclass
class CPU(Componente):
    """Procesador"""
    socket: str
    cores: int
    frecuencia_base: float  # GHz
    tdp: float  # Thermal Design Power en watts

@dataclass
class GPU(Componente):
    """Tarjeta gráfica"""
    vram: int  # GB
    tdp: float
    conectores_power: List[str]  # 6pin, 8pin, etc.

@dataclass
class RAM(Componente):
    """Memoria RAM"""
    capacidad: int  # GB
    velocidad: int  # MHz
    tipo: str  # DDR4, DDR5

@dataclass
class FuentePoder(Componente):
    """Fuente de poder"""
    vatios_max: int
    eficiencia: float  # 0.8 = 80%
    certificacion: str  # 80+ Bronze, Gold, etc.

class OptimizadorPC:
    """Clase principal para optimización de configuraciones de PC"""
    
    def __init__(self, archivo_datos: str = "data.json"):
        self.archivo_datos = archivo_datos
        self.componentes_disponibles = self.cargar_base_datos()
        
    def cargar_base_datos(self) -> Dict:
        """Carga base de datos de componentes desde el archivo JSON"""
        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Archivo {self.archivo_datos} no encontrado. Usando datos vacíos.")
            return {
                'gabinetes': [],
                'placas_base': [],
                'cpus': [],
                'gpus': [],
                'rams': [],
                'fuentes': []
            }
    
    def crear_componente_desde_dict(self, tipo: str, data: Dict):
        """Factory method para crear objetos componente desde diccionarios"""
        dimensiones = tuple(data['dimensiones'])
        
        if tipo == 'gabinetes':
            return Gabinete(
                data['nombre'], data['precio'], data['consumo_watts'],
                dimensiones, data['marca'], data['volumen_interno'], data['tipo']
            )
        elif tipo == 'cpus':
            return CPU(
                data['nombre'], data['precio'], data['consumo_watts'],
                dimensiones, data['marca'], data['socket'], data['cores'],
                data['frecuencia_base'], data['tdp']
            )
        elif tipo == 'gpus':
            return GPU(
                data['nombre'], data['precio'], data['consumo_watts'],
                dimensiones, data['marca'], data['vram'], data['tdp'],
                data['conectores_power']
            )
        elif tipo == 'fuentes':
            return FuentePoder(
                data['nombre'], data['precio'], data['consumo_watts'],
                dimensiones, data['marca'], data['vatios_max'],
                data['eficiencia'], data['certificacion']
            )
        else:
            return Componente(
                data['nombre'], data['precio'], data['consumo_watts'],
                dimensiones, data['marca']
            )
    
    def obtener_componentes_por_tipo(self, tipo: str) -> List:
        """Obtiene lista de componentes de un tipo específico como objetos"""
        componentes_data = self.componentes_disponibles.get(tipo, [])
        return [self.crear_componente_desde_dict(tipo, comp) for comp in componentes_data]
    
    def generar_configuraciones_posibles(self, max_configuraciones: int = 50) -> List[Dict]:
        """Genera configuraciones posibles combinando componentes disponibles"""
        configuraciones = []
        
        gabinetes = self.obtener_componentes_por_tipo('gabinetes')
        cpus = self.obtener_componentes_por_tipo('cpus')
        gpus = self.obtener_componentes_por_tipo('gpus')
        fuentes = self.obtener_componentes_por_tipo('fuentes')
        
        contador = 0
        for gabinete in gabinetes:
            for cpu in cpus:
                for gpu in gpus:
                    if contador >= max_configuraciones:
                        break
                    
                    # Buscar fuente adecuada
                    consumo_estimado = cpu.consumo_watts + gpu.consumo_watts + 100  # +100W para otros componentes
                    fuente_adecuada = self.encontrar_fuente_adecuada(fuentes, consumo_estimado)
                    
                    if fuente_adecuada:
                        config = {
                            'gabinete': gabinete,
                            'cpu': cpu,
                            'gpu': gpu,
                            'fuente': fuente_adecuada
                        }
                        
                        # Verificar compatibilidad básica
                        if self.verificar_compatibilidad_fisica(config):
                            configuraciones.append(config)
                            contador += 1
                
                if contador >= max_configuraciones:
                    break
            if contador >= max_configuraciones:
                break
        
        return configuraciones
    
    def encontrar_fuente_adecuada(self, fuentes: List[FuentePoder], consumo_estimado: float) -> FuentePoder:
        """Encuentra la fuente más económica que cubra el consumo estimado"""
        fuentes_adecuadas = [f for f in fuentes if f.vatios_max >= consumo_estimado * 1.3]
        if fuentes_adecuadas:
            return min(fuentes_adecuadas, key=lambda f: f.precio)
        return None
    
    def verificar_compatibilidad_fisica(self, configuracion: Dict) -> bool:
        """Verifica si los componentes caben físicamente en el gabinete"""
        gabinete = configuracion.get('gabinete')
        if not gabinete:
            return False
            
        volumen_ocupado = 0
        
        for tipo_componente, componente in configuracion.items():
            if tipo_componente != 'gabinete' and componente:
                volumen_ocupado += componente.volumen()
        
        # Factor de seguridad del 20%
        return volumen_ocupado <= (gabinete.volumen_interno * 0.8)
    
    def calcular_consumo_total(self, configuracion: Dict) -> float:
        """Calcula el consumo total de energía de la configuración"""
        consumo_total = 0
        
        for componente in configuracion.values():
            if componente:
                consumo_total += componente.consumo_watts
        
        # Agregar consumo base del sistema (ventiladores, motherboard, etc.)
        consumo_total += 50  # Watts base
        
        return consumo_total
    
    def calcular_costo_total(self, configuracion: Dict) -> float:
        """Calcula el costo total de la configuración"""
        return sum(c.precio for c in configuracion.values() if c)
    
    def funcion_objetivo(self, configuracion: Dict) -> float:
        """
        Función objetivo a minimizar:
        Combina costo, consumo energético y eficiencia
        """
        costo_total = self.calcular_costo_total(configuracion)
        consumo_total = self.calcular_consumo_total(configuracion)
        
        # Normalizar valores para combinar en función objetivo
        peso_costo = 0.4
        peso_consumo = 0.6
        
        return peso_costo * costo_total + peso_consumo * consumo_total
    
    def analizar_puntos_criticos_consumo(self, configuraciones: List[Dict]) -> Dict:
        """
        Usa derivadas numéricas para encontrar puntos críticos de consumo
        """
        if len(configuraciones) < 3:
            return {
                'puntos_criticos': [],
                'derivadas': [],
                'consumos': [],
                'costos': []
            }
        
        consumos = [self.calcular_consumo_total(config) for config in configuraciones]
        costos = [self.calcular_costo_total(config) for config in configuraciones]
        
        # Ordenar por costo para el análisis
        datos_ordenados = sorted(zip(costos, consumos, configuraciones))
        costos_ord, consumos_ord, configs_ord = zip(*datos_ordenados)
        
        # Derivada numérica del consumo respecto al costo
        derivadas = np.gradient(consumos_ord, costos_ord)
        
        # Encontrar puntos donde la derivada cambia de signo (puntos críticos)
        puntos_criticos = []
        for i in range(1, len(derivadas) - 1):
            if derivadas[i-1] * derivadas[i+1] < 0:  # Cambio de signo
                puntos_criticos.append({
                    'indice': i,
                    'costo': costos_ord[i],
                    'consumo': consumos_ord[i],
                    'derivada': derivadas[i],
                    'configuracion': configs_ord[i]
                })
        
        return {
            'puntos_criticos': puntos_criticos,
            'derivadas': derivadas,
            'consumos': list(consumos_ord),
            'costos': list(costos_ord),
            'configuraciones_ordenadas': list(configs_ord)
        }
    
    def recomendar_fuente_poder(self, consumo_total: float) -> int:
        """
        Recomienda la potencia mínima de fuente basada en consumo total
        con margen de seguridad
        """
        # Margen de seguridad del 20% + 10% para picos de consumo
        potencia_recomendada = consumo_total * 1.3
        
        # Redondear a valores estándar de fuentes
        potencias_estandar = [450, 500, 550, 600, 650, 700, 750, 800, 850, 1000, 1200]
        
        for potencia in potencias_estandar:
            if potencia >= potencia_recomendada:
                return potencia
        
        return potencias_estandar[-1]  # Máxima disponible
    
    def calcular_eficiencia_energetica(self, configuracion: Dict) -> float:
        """
        Calcula un índice de eficiencia energética
        (rendimiento / consumo)
        """
        # Simplificado: usar frecuencia CPU y VRAM GPU como medida de rendimiento
        cpu = configuracion.get('cpu')
        gpu = configuracion.get('gpu')
        
        rendimiento = 0
        if cpu and hasattr(cpu, 'frecuencia_base') and hasattr(cpu, 'cores'):
            rendimiento += cpu.frecuencia_base * cpu.cores
        if gpu and hasattr(gpu, 'vram'):
            rendimiento += gpu.vram * 100  # Factor arbitrario
        
        consumo = self.calcular_consumo_total(configuracion)
        
        return rendimiento / consumo if consumo > 0 else 0
    
    def encontrar_configuracion_optima(self) -> Dict:
        """Encuentra la configuración óptima usando análisis matemático"""
        configuraciones = self.generar_configuraciones_posibles()
        
        if not configuraciones:
            return None
        
        # Calcular métricas para cada configuración
        configuraciones_con_metricas = []
        for config in configuraciones:
            metricas = {
                'configuracion': config,
                'costo': self.calcular_costo_total(config),
                'consumo': self.calcular_consumo_total(config),
                'eficiencia': self.calcular_eficiencia_energetica(config),
                'funcion_objetivo': self.funcion_objetivo(config)
            }
            configuraciones_con_metricas.append(metricas)
        
        # Encontrar la mejor según la función objetivo
        mejor_config = min(configuraciones_con_metricas, key=lambda x: x['funcion_objetivo'])
        
        return mejor_config

def main():
    """Función principal del programa"""
    print("🖥️  Optimizador de PC - Investigación")
    print("====================================")
    
    # Crear optimizador
    optimizador = OptimizadorPC("data.json")
    
    # Mostrar componentes disponibles
    print("\n📦 Componentes disponibles:")
    for tipo in ['gabinetes', 'cpus', 'gpus', 'fuentes']:
        componentes = optimizador.obtener_componentes_por_tipo(tipo)
        print(f"  {tipo.upper()}: {len(componentes)} disponibles")
    
    # Generar y analizar configuraciones
    print("\n🔍 Generando configuraciones...")
    configuraciones = optimizador.generar_configuraciones_posibles(20)
    print(f"✅ {len(configuraciones)} configuraciones válidas generadas")
    
    if configuraciones:
        # Encontrar configuración óptima
        config_optima = optimizador.encontrar_configuracion_optima()
        
        if config_optima:
            print("\n🏆 CONFIGURACIÓN ÓPTIMA ENCONTRADA:")
            print("=" * 40)
            config = config_optima['configuracion']
            
            for tipo, componente in config.items():
                if componente:
                    print(f"📱 {tipo.upper()}: {componente.nombre} - ${componente.precio}")
            
            print(f"\n💰 Costo total: ${config_optima['costo']:.2f}")
            print(f"💡 Consumo total: {config_optima['consumo']:.1f}W")
            print(f"📊 Índice de eficiencia: {config_optima['eficiencia']:.2f}")
            print(f"⚡ Fuente recomendada: {optimizador.recomendar_fuente_poder(config_optima['consumo'])}W")
            
            # Análisis de puntos críticos
            analisis = optimizador.analizar_puntos_criticos_consumo(configuraciones)
            if analisis['puntos_criticos']:
                print(f"\n🎯 {len(analisis['puntos_criticos'])} puntos críticos encontrados")
                for i, punto in enumerate(analisis['puntos_criticos'][:3]):  # Mostrar solo los primeros 3
                    print(f"   Punto {i+1}: ${punto['costo']:.0f} - {punto['consumo']:.0f}W")
        
        # Ofrecer análisis visual
        print("\n📊 ¿Deseas ver el análisis visual? (Ejecuta script2.py para visualizaciones)")
        print("📁 ¿Deseas gestionar la base de datos? (Ejecuta script3.py para gestión)")
    
    else:
        print("❌ No se pudieron generar configuraciones válidas.")
        print("   Verifica que data.json tenga componentes compatibles.")

if __name__ == "__main__":
    main()