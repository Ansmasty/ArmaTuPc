"""
Filtros especializados para análisis matemático
Hereda funcionalidad de filtros.py y agrega capacidades específicas
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Importar filtros base - arreglar el import
try:
    # Primero intentar import relativo
    from filtros import crear_workflow_seleccion_componentes
    # Como no existe FiltrosComponentes, crear una clase base propia
    class FiltrosComponentesBase:
        def __init__(self, ruta_datos: str = None):
            self.ruta_datos = ruta_datos or os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "normalized_data"
            )
            self.datos = {}
            self.cargar_datos()
            
        def cargar_datos(self):
            """Carga los datos de componentes desde normalized_data"""
            # Mapeo de tipos de componentes a nombres de archivos reales
            mapeo_archivos = {
                'cpu': 'CPUData_normalized.json',
                'motherboard': 'MotherboardData_normalized.json',
                'ram': 'RAMData_normalized.json',
                'gpu': 'GPUData_normalized.json',
                'case': 'CaseData_normalized.json',
                'psu': 'PSUData_normalized.json',
                'cpu_cooler': 'CPUCoolerData_normalized.json',
                'hdd': 'HDDData_normalized.json',
                'ssd': 'SSDData_normalized.json'
            }
            
            for tipo, nombre_archivo in mapeo_archivos.items():
                try:
                    archivo = os.path.join(self.ruta_datos, nombre_archivo)
                    if os.path.exists(archivo):
                        with open(archivo, 'r', encoding='utf-8') as f:
                            self.datos[tipo] = json.load(f)
                        print(f"✓ Cargado {tipo}: {len(self.datos[tipo])} elementos")
                    else:
                        print(f"⚠️ No se encontró {archivo}")
                        self.datos[tipo] = []
                except Exception as e:
                    print(f"❌ Error cargando {tipo}: {e}")
                    self.datos[tipo] = []
                    
        def obtener_componentes_por_tipo(self, tipo: str) -> List[Dict[str, Any]]:
            """Obtiene todos los componentes de un tipo específico"""
            return self.datos.get(tipo, [])
            
except ImportError as e:
    print(f"Error importando filtros base: {e}")
    # Crear clase base simple
    class FiltrosComponentesBase:
        def __init__(self, ruta_datos: str = None):
            self.ruta_datos = ruta_datos
            self.datos = {}

class FiltrosAnalisisMatematico(FiltrosComponentesBase):
    """
    Filtros especializados para análisis matemático de builds
    Hereda funcionalidad básica y agrega funcionalidad específica
    """
    
    def __init__(self, ruta_datos: str = None):
        super().__init__(ruta_datos)
        self.build_actual = None
        self.datos_extendidos = {}
        
    def establecer_build_actual(self, configuracion_build: Dict[str, Any]):
        """Establece la build actual para análisis"""
        self.build_actual = configuracion_build
        self.cargar_datos_extendidos_build()
    
    def cargar_datos_extendidos_build(self):
        """Carga datos extendidos específicos para cada componente de la build"""
        if not self.build_actual:
            return
        
        self.datos_extendidos = {}
        
        # Para cada componente en la build, cargar datos detallados
        for tipo_componente, componente in self.build_actual.items():
            if componente and isinstance(componente, dict):
                datos_detallados = self.obtener_datos_detallados_componente(
                    tipo_componente, componente
                )
                self.datos_extendidos[tipo_componente] = datos_detallados
    
    def obtener_datos_detallados_componente(self, tipo: str, componente: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene datos detallados de un componente específico"""
        # Usar la funcionalidad heredada
        todos_componentes = self.obtener_componentes_por_tipo(tipo)
        
        # Buscar el componente específico usando varios campos posibles
        campos_nombre = ['nombre', 'name', 'model', 'title', 'product_name']
        nombre_componente = ''
        
        for campo in campos_nombre:
            if campo in componente and componente[campo]:
                nombre_componente = str(componente[campo]).strip()
                break
        
        print(f"DEBUG: Buscando {tipo} con nombre: '{nombre_componente}'")
        
        componente_detallado = None
        
        # Buscar por coincidencia exacta primero
        for comp in todos_componentes:
            for campo in campos_nombre:
                if campo in comp and comp[campo]:
                    if str(comp[campo]).strip() == nombre_componente:
                        componente_detallado = comp
                        print(f"DEBUG: Coincidencia exacta encontrada para {tipo}")
                        break
            if componente_detallado:
                break
        
        # Si no se encontró coincidencia exacta, buscar coincidencia parcial
        if not componente_detallado and nombre_componente:
            for comp in todos_componentes:
                for campo in campos_nombre:
                    if campo in comp and comp[campo]:
                        if nombre_componente.lower() in str(comp[campo]).lower() or str(comp[campo]).lower() in nombre_componente.lower():
                            componente_detallado = comp
                            print(f"DEBUG: Coincidencia parcial encontrada para {tipo}")
                            break
                if componente_detallado:
                    break
        
        if componente_detallado:
            print(f"DEBUG: Datos encontrados para {tipo}, campos disponibles: {list(componente_detallado.keys())[:15]}")
            # Agregar datos calculados específicos para análisis
            return self.agregar_datos_analisis(tipo, componente_detallado)
        else:
            print(f"DEBUG: No se encontraron datos detallados para {tipo}, usando datos básicos")
            # Si no se encuentra, usar el componente original pero agregar datos calculados
            return self.agregar_datos_analisis(tipo, componente)
    
    def agregar_datos_analisis(self, tipo: str, componente: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega datos específicos para análisis matemático"""
        componente_extendido = componente.copy()
        
        # Agregar datos específicos por tipo
        if tipo == 'cpu':
            componente_extendido.update(self.calcular_parametros_cpu(componente))
        elif tipo == 'gpu':
            componente_extendido.update(self.calcular_parametros_gpu(componente))
        elif tipo == 'case':
            componente_extendido.update(self.calcular_parametros_case(componente))
        elif tipo == 'cpu_cooler':
            componente_extendido.update(self.calcular_parametros_cooling(componente))
        elif tipo == 'psu':
            componente_extendido.update(self.calcular_parametros_psu(componente))
        
        return componente_extendido
    
    def calcular_parametros_cpu(self, cpu: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula parámetros matemáticos para CPU"""
        parametros = {}
        
        print(f"DEBUG CPU: Campos disponibles: {list(cpu.keys())[:10]}")
        
        # Buscar TDP en varios campos posibles
        tdp_campos = ['tdp', 'TDP', 'thermal_design_power', 'power_consumption', 'watts', 'wattage']
        tdp_valor = 0.0
        
        for campo in tdp_campos:
            if campo in cpu and cpu[campo]:
                print(f"DEBUG CPU: Encontrado campo {campo} con valor: {cpu[campo]}")
                tdp_valor = self.extraer_numero(cpu[campo])
                print(f"DEBUG CPU: TDP extraído: {tdp_valor}")
                if tdp_valor > 0:
                    break
        
        # Si no se encontró TDP, estimar basado en otros datos
        if tdp_valor == 0:
            # Estimar TDP basado en el nombre del procesador
            nombre = cpu.get('name', cpu.get('nombre', '')).lower()
            print(f"DEBUG CPU: Estimando TDP basado en nombre: '{nombre}'")
            if any(x in nombre for x in ['i9', 'ryzen 9', 'threadripper']):
                tdp_valor = 125.0  # Procesadores de gama alta
            elif any(x in nombre for x in ['i7', 'ryzen 7']):
                tdp_valor = 95.0   # Procesadores de gama media-alta
            elif any(x in nombre for x in ['i5', 'ryzen 5']):
                tdp_valor = 65.0   # Procesadores de gama media
            elif any(x in nombre for x in ['i3', 'ryzen 3']):
                tdp_valor = 45.0   # Procesadores de gama baja
            else:
                tdp_valor = 65.0   # Valor por defecto
            print(f"DEBUG CPU: TDP estimado: {tdp_valor}")
        
        parametros['tdp_numerico'] = tdp_valor
        parametros['disipacion_termica'] = tdp_valor * 0.85  # 85% se convierte en calor
        
        # Extraer frecuencia base
        freq_campos = ['base_clock', 'base_frequency', 'frequency', 'clock_speed', 'speed']
        freq_valor = 0.0
        
        # Buscar primero en campos directos
        for campo in freq_campos:
            if campo in cpu and cpu[campo]:
                print(f"DEBUG CPU: Encontrado frecuencia en {campo}: {cpu[campo]}")
                freq_valor = self.extraer_numero(cpu[campo])
                print(f"DEBUG CPU: Frecuencia extraída: {freq_valor}")
                if freq_valor > 0:
                    break
        
        # Si no se encuentra, buscar en subcampos como performance.base_clock
        if freq_valor == 0 and 'performance' in cpu:
            perf = cpu['performance']
            if isinstance(perf, dict):
                if 'base_clock' in perf:
                    base_clock = perf['base_clock']
                    if isinstance(base_clock, dict) and 'value' in base_clock:
                        freq_valor = float(base_clock['value'])
                        print(f"DEBUG CPU: Frecuencia encontrada en performance.base_clock.value: {freq_valor}")
                    elif isinstance(base_clock, (int, float)):
                        freq_valor = float(base_clock)
                        print(f"DEBUG CPU: Frecuencia encontrada en performance.base_clock: {freq_valor}")
                elif 'frequency' in perf:
                    freq_valor = self.extraer_numero(perf['frequency'])
                    print(f"DEBUG CPU: Frecuencia encontrada en performance.frequency: {freq_valor}")
        
        parametros['frecuencia_base'] = freq_valor
        
        # Calcular eficiencia térmica estimada
        if tdp_valor > 0 and freq_valor > 0:
            parametros['eficiencia_termica'] = freq_valor / tdp_valor
        
        print(f"DEBUG CPU: Parámetros finales: {parametros}")
        return parametros
    
    def calcular_parametros_gpu(self, gpu: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula parámetros matemáticos para GPU"""
        parametros = {}
        
        print(f"DEBUG GPU: Campos disponibles: {list(gpu.keys())[:10]}")
        
        # Buscar TDP en varios campos posibles
        tdp_campos = ['tdp', 'TDP', 'power_consumption', 'watts', 'wattage', 'total_graphics_power']
        tdp_valor = 0.0
        
        for campo in tdp_campos:
            if campo in gpu and gpu[campo]:
                print(f"DEBUG GPU: Encontrado campo {campo}: {gpu[campo]}")
                tdp_valor = self.extraer_numero(gpu[campo])
                print(f"DEBUG GPU: TDP extraído: {tdp_valor}")
                if tdp_valor > 0:
                    break
        
        # Buscar TDP en subcampo performance
        if tdp_valor == 0 and 'performance' in gpu:
            performance = gpu['performance']
            if isinstance(performance, dict):
                if 'tdp' in performance:
                    tdp_data = performance['tdp']
                    if isinstance(tdp_data, dict) and 'value' in tdp_data:
                        tdp_valor = float(tdp_data['value'])
                        print(f"DEBUG GPU: TDP encontrado en performance.tdp.value: {tdp_valor}")
                    elif isinstance(tdp_data, (int, float)):
                        tdp_valor = float(tdp_data)
                        print(f"DEBUG GPU: TDP encontrado en performance.tdp: {tdp_valor}")
                    elif isinstance(tdp_data, str):
                        tdp_valor = self.extraer_numero(tdp_data)
                        print(f"DEBUG GPU: TDP extraído de performance.tdp string: {tdp_valor}")
        
        # Buscar en subcampo power si existe
        if tdp_valor == 0 and 'power' in gpu:
            power = gpu['power']
            if isinstance(power, dict):
                for subcampo in ['consumption', 'tdp', 'wattage', 'total_power']:
                    if subcampo in power:
                        valor_power = power[subcampo]
                        if isinstance(valor_power, dict) and 'value' in valor_power:
                            tdp_valor = float(valor_power['value'])
                        elif isinstance(valor_power, (int, float)):
                            tdp_valor = float(valor_power)
                        elif isinstance(valor_power, str):
                            tdp_valor = self.extraer_numero(valor_power)
                        print(f"DEBUG GPU: TDP encontrado en power.{subcampo}: {tdp_valor}")
                        if tdp_valor > 0:
                            break
        
        # Si no se encontró TDP, estimar basado en el nombre
        if tdp_valor == 0:
            nombre = gpu.get('name', '').lower()
            print(f"DEBUG GPU: Estimando TDP basado en nombre: '{nombre}'")
            if any(x in nombre for x in ['4090', '4080', '7900 xt', '7800 xt']):
                tdp_valor = 300.0  # GPUs de gama alta
            elif any(x in nombre for x in ['4070', '4060', '7700 xt', '7600 xt']):
                tdp_valor = 200.0  # GPUs de gama media-alta
            elif any(x in nombre for x in ['4050', '3060', '7500 xt', '6600 xt', 'arc a750']):
                tdp_valor = 150.0  # GPUs de gama media
            elif any(x in nombre for x in ['3050', '1660', '6500 xt', 'rx 6600']):
                tdp_valor = 100.0  # GPUs de gama baja
            else:
                tdp_valor = 150.0  # Valor por defecto
            print(f"DEBUG GPU: TDP estimado: {tdp_valor}")
        
        parametros['tdp_numerico'] = tdp_valor
        parametros['disipacion_termica'] = tdp_valor * 0.90  # GPU genera más calor
        
        print(f"DEBUG GPU: Parámetros finales: {parametros}")
        return parametros
    
    def calcular_parametros_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula parámetros matemáticos para Case"""
        parametros = {}
        
        # Estimar volumen interno
        if 'dimensions' in case:
            dim = case['dimensions']
            volumen = self.calcular_volumen_case(dim)
            parametros['volumen_interno'] = volumen
            parametros['factor_ventilacion'] = self.calcular_factor_ventilacion(case)
        
        return parametros
    
    def calcular_parametros_cooling(self, cooling: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula parámetros matemáticos para Cooling"""
        parametros = {}
        
        # Buscar capacidad de enfriamiento en varios campos
        cap_campos = ['tdp', 'TDP', 'cooling_capacity', 'max_tdp', 'rated_tdp']
        cap_valor = 0.0
        
        for campo in cap_campos:
            if campo in cooling and cooling[campo]:
                cap_valor = self.extraer_numero(cooling[campo])
                if cap_valor > 0:
                    break
        
        # Si no se encontró capacidad, estimar basado en el tipo
        if cap_valor == 0:
            nombre = cooling.get('name', '').lower()
            if any(x in nombre for x in ['liquid', 'aio', 'water', 'h100', 'h150']):
                cap_valor = 200.0  # Refrigeración líquida
            elif any(x in nombre for x in ['tower', 'cooler', 'fan']):
                cap_valor = 150.0  # Refrigeración por aire grande
            elif 'stock' in nombre or 'included' in nombre:
                cap_valor = 65.0   # Cooler stock
            else:
                cap_valor = 120.0  # Valor por defecto
        
        parametros['capacidad_enfriamiento'] = cap_valor
        
        return parametros
    
    def calcular_parametros_psu(self, psu: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula parámetros matemáticos para PSU"""
        parametros = {}
        
        print(f"DEBUG PSU: Campos disponibles: {list(psu.keys())[:10]}")
        
        # Buscar Wattage en varios campos posibles
        watt_campos = ['wattage', 'watts', 'power', 'max_power', 'capacity']
        watt_valor = 0.0
        
        for campo in watt_campos:
            if campo in psu and psu[campo]:
                print(f"DEBUG PSU: Encontrado campo {campo}: {psu[campo]}")
                if campo == 'power' and isinstance(psu[campo], dict):
                    # No extraer número del objeto completo, ir directamente a subcampos
                    print(f"DEBUG PSU: Campo power es un diccionario, buscando subcampos...")
                    continue
                watt_valor = self.extraer_numero(psu[campo])
                print(f"DEBUG PSU: Wattage extraído: {watt_valor}")
                if watt_valor > 0:
                    break
        
        # Buscar en subcampo power si existe
        if watt_valor == 0 and 'power' in psu:
            power = psu['power']
            if isinstance(power, dict):
                for subcampo in ['wattage', 'max_power', 'capacity', 'rated_power']:
                    if subcampo in power:
                        valor_power = power[subcampo]
                        if isinstance(valor_power, dict) and 'value' in valor_power:
                            watt_valor = float(valor_power['value'])
                        elif isinstance(valor_power, (int, float)):
                            watt_valor = float(valor_power)
                        elif isinstance(valor_power, str):
                            watt_valor = self.extraer_numero(valor_power)
                        print(f"DEBUG PSU: Wattage encontrado en power.{subcampo}: {watt_valor}")
                        if watt_valor > 0:
                            break
        
        # Si no se encontró wattage, extraer del nombre
        if watt_valor == 0:
            nombre = psu.get('name', '')
            print(f"DEBUG PSU: Extrayendo wattage del nombre: '{nombre}'")
            import re
            match = re.search(r'(\d+)\s*w', nombre.lower())
            if match:
                watt_valor = float(match.group(1))
                print(f"DEBUG PSU: Wattage extraído del nombre: {watt_valor}")
            else:
                watt_valor = 650.0  # Valor por defecto
                print(f"DEBUG PSU: Usando valor por defecto: {watt_valor}")
        
        parametros['wattage_numerico'] = watt_valor
        
        # Buscar eficiencia
        eff_campos = ['efficiency', 'rating', 'certification', '80plus']
        eff_valor = 0.8  # Valor por defecto
        
        for campo in eff_campos:
            if campo in psu and psu[campo]:
                print(f"DEBUG PSU: Encontrado eficiencia en {campo}: {psu[campo]}")
                eff_valor = self.extraer_eficiencia(psu[campo])
                print(f"DEBUG PSU: Eficiencia extraída: {eff_valor}")
                if eff_valor > 0:
                    break
        
        # Buscar en subcampo power para eficiencia
        if eff_valor == 0.8 and 'power' in psu:
            power = psu['power']
            if isinstance(power, dict):
                for subcampo in ['efficiency', 'certification', 'rating']:
                    if subcampo in power:
                        eff_valor = self.extraer_eficiencia(power[subcampo])
                        print(f"DEBUG PSU: Eficiencia encontrada en power.{subcampo}: {eff_valor}")
                        if eff_valor > 0:
                            break
        
        parametros['eficiencia_numerica'] = eff_valor
        
        print(f"DEBUG PSU: Parámetros finales: {parametros}")
        return parametros
    
    def obtener_potencia_total_build(self) -> float:
        """Calcula la potencia total de la build actual"""
        potencia_total = 0
        
        if not self.datos_extendidos:
            return potencia_total
        
        # Sumar TDP de todos los componentes
        for tipo, datos in self.datos_extendidos.items():
            if 'tdp_numerico' in datos:
                potencia_total += datos['tdp_numerico']
        
        return potencia_total
    
    def obtener_parametros_termicos_build(self) -> Dict[str, Any]:
        """Obtiene parámetros térmicos de la build completa"""
        return {
            'potencia_total': self.obtener_potencia_total_build(),
            'disipacion_total': sum(
                datos.get('disipacion_termica', 0) 
                for datos in self.datos_extendidos.values()
            ),
            'capacidad_enfriamiento': self.datos_extendidos.get('cpu_cooler', {}).get('capacidad_enfriamiento', 0),
            'factor_ventilacion': self.datos_extendidos.get('case', {}).get('factor_ventilacion', 1.0),
            'volumen_interno': self.datos_extendidos.get('case', {}).get('volumen_interno', 40.0)
        }
    
    def extraer_numero(self, valor_str: str) -> float:
        """Extrae número de una cadena con unidades - versión mejorada"""
        if isinstance(valor_str, (int, float)):
            return float(valor_str)
        
        if isinstance(valor_str, str):
            # Limpiar la cadena
            valor_limpio = valor_str.lower().strip()
            
            # Remover unidades comunes
            unidades = ['w', 'watt', 'watts', 'ghz', 'mhz', 'hz', 'mb', 'gb', 'tb', 'rpm', 'cfm', 'db', 'v', 'volt', 'volts', 'a', 'amp', 'amps']
            for unidad in unidades:
                valor_limpio = valor_limpio.replace(unidad, '').strip()
            
            # Remover símbolos comunes
            valor_limpio = valor_limpio.replace('~', '').replace('±', '').replace('≤', '').replace('≥', '').replace('<', '').replace('>', '').replace('=', '')
            
            # Buscar números (incluyendo decimales)
            import re
            # Buscar patrones como 65, 65.0, 65.5, etc.
            match = re.search(r'(\d+\.?\d*)', valor_limpio.replace(',', '.'))
            if match:
                numero = float(match.group(1))
                
                # Ajustar por prefijos comunes
                if 'k' in valor_limpio or 'kilo' in valor_limpio:
                    numero *= 1000
                elif 'm' in valor_limpio and 'mhz' not in valor_str.lower():
                    numero *= 1000000
                elif 'g' in valor_limpio and 'ghz' not in valor_str.lower():
                    numero *= 1000000000
                    
                return numero
        
        return 0.0
    
    def extraer_eficiencia(self, eficiencia_str: str) -> float:
        """Extrae eficiencia de string como 80+ Gold"""
        if isinstance(eficiencia_str, (int, float)):
            return float(eficiencia_str) / 100.0 if eficiencia_str > 1 else float(eficiencia_str)
        
        if isinstance(eficiencia_str, str):
            eficiencia_limpia = eficiencia_str.lower().strip()
            
            # Buscar patrones específicos de eficiencia
            if 'titanium' in eficiencia_limpia or '94+' in eficiencia_limpia:
                return 0.94
            elif 'platinum' in eficiencia_limpia or '92+' in eficiencia_limpia:
                return 0.92
            elif 'gold' in eficiencia_limpia or '87+' in eficiencia_limpia:
                return 0.87
            elif 'silver' in eficiencia_limpia or '85+' in eficiencia_limpia:
                return 0.85
            elif 'bronze' in eficiencia_limpia or '82+' in eficiencia_limpia:
                return 0.82
            elif '80+' in eficiencia_limpia:
                return 0.80
            
            # Buscar números directos
            import re
            match = re.search(r'(\d+)', eficiencia_limpia)
            if match:
                numero = float(match.group(1))
                return numero / 100.0 if numero > 1 else numero
        
        return 0.8  # Valor por defecto
    
    def calcular_volumen_case(self, dimensiones: str) -> float:
        """Calcula volumen aproximado del case"""
        # Implementar lógica para calcular volumen basado en dimensiones
        # Por ahora, valores típicos por form factor
        form_factors = {
            'ATX': 50.0,      # litros
            'Micro-ATX': 30.0,
            'Mini-ITX': 20.0,
            'E-ATX': 70.0
        }
        
        # Buscar en dimensiones o usar valor por defecto
        if isinstance(dimensiones, str):
            for ff, vol in form_factors.items():
                if ff.lower() in dimensiones.lower():
                    return vol
        
        return 40.0  # Valor por defecto
    
    def calcular_factor_ventilacion(self, case: Dict[str, Any]) -> float:
        """Calcula factor de ventilación del case"""
        # Implementar lógica basada en número de ventiladores, etc.
        # Por ahora, factor base
        return 1.0
    
    def extraer_parametros_build(self, build_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae parámetros matemáticos del build completo"""
        if not build_data:
            return {}
        
        print(f"DEBUG: Datos del build recibidos: {list(build_data.keys())}")
        
        # Establecer build actual
        self.establecer_build_actual(build_data)
        
        # Depurar datos extendidos
        print(f"DEBUG: Datos extendidos generados: {list(self.datos_extendidos.keys())}")
        # for tipo, datos in self.datos_extendidos.items():
        #     if datos:
        #         print(f"DEBUG: {tipo} tiene {len(datos)} campos: {list(datos.keys())[:10]}")  # Mostrar primeros 10 campos
        
        # Obtener parámetros térmicos
        parametros_termicos = self.obtener_parametros_termicos_build()
        print(f"DEBUG: Parámetros térmicos calculados: {parametros_termicos}")
        
        # Extraer información adicional del build
        parametros_build = {
            'nombre_build': build_data.get('nombre', 'Build Sin Nombre'),
            'tipo_build': build_data.get('tipo', 'Personalizado'),
            'potencia_total': parametros_termicos.get('potencia_total', 0),
            'disipacion_total': parametros_termicos.get('disipacion_total', 0),
            'capacidad_enfriamiento': parametros_termicos.get('capacidad_enfriamiento', 0),
            'factor_ventilacion': parametros_termicos.get('factor_ventilacion', 1.0),
            'volumen_interno': parametros_termicos.get('volumen_interno', 40.0),
            'eficiencia_termica': self.calcular_eficiencia_termica_build(),
            'factor_forma': self.extraer_factor_forma_build(build_data),
            'compatibilidad_termica': self.evaluar_compatibilidad_termica()
        }
        
        # Agregar parámetros específicos por componente
        parametros_build.update(self.extraer_parametros_componentes_individuales())
        
        return parametros_build
    
    def calcular_eficiencia_termica_build(self) -> float:
        """Calcula la eficiencia térmica general del build"""
        if not self.datos_extendidos:
            return 0.0
        
        # Calcular eficiencia basada en la relación entre capacidad de enfriamiento y calor generado
        capacidad_enfriamiento = self.datos_extendidos.get('cpu_cooler', {}).get('capacidad_enfriamiento', 0)
        disipacion_total = sum(
            datos.get('disipacion_termica', 0) 
            for datos in self.datos_extendidos.values()
        )
        
        if disipacion_total > 0:
            return min(capacidad_enfriamiento / disipacion_total, 1.0)
        
        return 0.0
    
    def extraer_factor_forma_build(self, build_data: Dict[str, Any]) -> str:
        """Extrae el factor de forma principal del build"""
        # Buscar en motherboard primero
        if 'motherboard' in build_data and build_data['motherboard']:
            mb = build_data['motherboard']
            if 'form_factor' in mb:
                return mb['form_factor']
        
        # Buscar en case
        if 'case' in build_data and build_data['case']:
            case = build_data['case']
            if 'form_factor' in case:
                return case['form_factor']
        
        return 'ATX'  # Valor por defecto
    
    def evaluar_compatibilidad_termica(self) -> str:
        """Evalúa la compatibilidad térmica del build"""
        if not self.datos_extendidos:
            return 'Desconocido'
        
        # Obtener parámetros térmicos
        parametros = self.obtener_parametros_termicos_build()
        
        capacidad_enfriamiento = parametros.get('capacidad_enfriamiento', 0)
        disipacion_total = parametros.get('disipacion_total', 0)
        
        if capacidad_enfriamiento == 0 or disipacion_total == 0:
            return 'Información insuficiente'
        
        # Calcular margen térmico
        margen = capacidad_enfriamiento / disipacion_total
        
        if margen >= 1.3:
            return 'Excelente'
        elif margen >= 1.1:
            return 'Buena'
        elif margen >= 0.9:
            return 'Aceptable'
        else:
            return 'Insuficiente'
    
    def extraer_parametros_componentes_individuales(self) -> Dict[str, Any]:
        """Extrae parámetros específicos de cada componente individual"""
        parametros = {}
        
        if not self.datos_extendidos:
            return parametros
        
        # Parámetros del CPU
        if 'cpu' in self.datos_extendidos:
            cpu_data = self.datos_extendidos['cpu']
            parametros['cpu_tdp'] = cpu_data.get('tdp_numerico', 0)
            parametros['cpu_frecuencia'] = cpu_data.get('frecuencia_base', 0)
            parametros['cpu_eficiencia'] = cpu_data.get('eficiencia_termica', 0)
        
        # Parámetros del GPU
        if 'gpu' in self.datos_extendidos:
            gpu_data = self.datos_extendidos['gpu']
            parametros['gpu_tdp'] = gpu_data.get('tdp_numerico', 0)
            parametros['gpu_disipacion'] = gpu_data.get('disipacion_termica', 0)
        
        # Parámetros del PSU
        if 'psu' in self.datos_extendidos:
            psu_data = self.datos_extendidos['psu']
            parametros['psu_wattage'] = psu_data.get('wattage_numerico', 0)
            parametros['psu_eficiencia'] = psu_data.get('eficiencia_numerica', 0.8)
        
        # Parámetros del Case
        if 'case' in self.datos_extendidos:
            case_data = self.datos_extendidos['case']
            parametros['case_volumen'] = case_data.get('volumen_interno', 40.0)
            parametros['case_ventilacion'] = case_data.get('factor_ventilacion', 1.0)
        
        # Parámetros del Cooler
        if 'cpu_cooler' in self.datos_extendidos:
            cooler_data = self.datos_extendidos['cpu_cooler']
            parametros['cooler_capacidad'] = cooler_data.get('capacidad_enfriamiento', 0)
        
        return parametros
