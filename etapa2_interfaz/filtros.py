import json
import os
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class Arquitectura(Enum):
    """Enum para arquitecturas de CPU"""
    AMD = "AMD"
    INTEL = "Intel"


@dataclass
class FiltroCompatibilidad:
    """Clase base para configurar filtros de compatibilidad"""
    arquitectura: Optional[Arquitectura] = None
    socket_cpu: Optional[str] = None
    motherboard_form_factor: Optional[str] = None
    ram_type: Optional[str] = None
    psu_form_factor: Optional[str] = None
    case_form_factor: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'arquitectura': self.arquitectura.value if self.arquitectura else None,
            'socket_cpu': self.socket_cpu,
            'motherboard_form_factor': self.motherboard_form_factor,
            'ram_type': self.ram_type,
            'psu_form_factor': self.psu_form_factor,
            'case_form_factor': self.case_form_factor
        }


class GestorFiltros:
    """Gestor principal para aplicar filtros de compatibilidad entre componentes"""
    
    def __init__(self, ruta_datos_normalizados: str):
        """
        Inicializa el gestor con la ruta a los datos normalizados
        
        Args:
            ruta_datos_normalizados: Ruta al directorio con los archivos JSON normalizados
        """
        self.ruta_datos = ruta_datos_normalizados
        self.datos = {}
        self._cargar_datos()
        
    def _cargar_datos(self):
        """Carga todos los datos normalizados en memoria"""
        archivos_datos = {
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
        
        for componente, archivo in archivos_datos.items():
            ruta_archivo = os.path.join(self.ruta_datos, archivo)
            if os.path.exists(ruta_archivo):
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        self.datos[componente] = json.load(f)
                    print(f"✓ Cargado {componente}: {len(self.datos[componente])} elementos")
                except Exception as e:
                    print(f"✗ Error cargando {componente}: {e}")
                    self.datos[componente] = []
            else:
                print(f"✗ Archivo no encontrado: {archivo}")
                self.datos[componente] = []
    
    def obtener_arquitecturas_disponibles(self) -> List[str]:
        """Obtiene las arquitecturas de CPU disponibles"""
        arquitecturas = set()
        for cpu in self.datos.get('cpu', []):
            if cpu.get('producer'):
                arquitecturas.add(cpu['producer'])
        return sorted(list(arquitecturas))
    
    def obtener_sockets_por_arquitectura(self, arquitectura: str) -> List[str]:
        """
        Obtiene los sockets de CPU disponibles para una arquitectura específica
        
        Args:
            arquitectura: Arquitectura de CPU (AMD, Intel)
            
        Returns:
            Lista de sockets disponibles
        """
        sockets = set()
        for cpu in self.datos.get('cpu', []):
            if (cpu.get('producer') == arquitectura and 
                cpu.get('architecture', {}).get('socket')):
                sockets.add(cpu['architecture']['socket'])
        return sorted(list(sockets))
    
    def filtrar_cpus_por_arquitectura(self, arquitectura: str) -> List[Dict]:
        """
        Filtra CPUs por arquitectura
        
        Args:
            arquitectura: Arquitectura deseada (AMD, Intel)
            
        Returns:
            Lista de CPUs compatibles
        """
        cpus_compatibles = []
        for cpu in self.datos.get('cpu', []):
            if cpu.get('producer') == arquitectura:
                cpus_compatibles.append(cpu)
        return cpus_compatibles
    
    def filtrar_motherboards_por_socket(self, socket: str) -> List[Dict]:
        """
        Filtra motherboards por socket de CPU
        
        Args:
            socket: Socket de CPU (ej: AM4, LGA1200)
            
        Returns:
            Lista de motherboards compatibles
        """
        motherboards_compatibles = []
        for mb in self.datos.get('motherboard', []):
            if mb.get('platform', {}).get('socket') == socket:
                motherboards_compatibles.append(mb)
        return motherboards_compatibles
    
    def obtener_form_factors_motherboard(self, socket: str = None) -> List[str]:
        """
        Obtiene los form factors de motherboard disponibles
        
        Args:
            socket: Socket opcional para filtrar
            
        Returns:
            Lista de form factors
        """
        form_factors = set()
        for mb in self.datos.get('motherboard', []):
            if socket is None or mb.get('platform', {}).get('socket') == socket:
                if mb.get('form_factor'):
                    form_factors.add(mb['form_factor'])
        return sorted(list(form_factors))
    
    def filtrar_ram_por_motherboard(self, socket: str = None, form_factor: str = None) -> List[Dict]:
        """
        Filtra RAM compatible con las motherboards seleccionadas
        
        Args:
            socket: Socket de CPU
            form_factor: Form factor de motherboard
            
        Returns:
            Lista de RAM compatible y tipos soportados
        """
        # Primero obtener tipos de RAM soportados por las motherboards compatibles
        tipos_ram_soportados = set()
        motherboards_compatibles = self.datos.get('motherboard', [])
        
        if socket:
            motherboards_compatibles = [mb for mb in motherboards_compatibles 
                                      if mb.get('platform', {}).get('socket') == socket]
        
        if form_factor:
            motherboards_compatibles = [mb for mb in motherboards_compatibles 
                                      if mb.get('form_factor') == form_factor]
        
        for mb in motherboards_compatibles:
            if mb.get('memory', {}).get('type'):
                tipos_ram_soportados.add(mb['memory']['type'])
        
        # Filtrar RAM por tipos soportados
        ram_compatible = []
        for ram in self.datos.get('ram', []):
            ram_type = ram.get('memory_specs', {}).get('ram_type', {}).get('generation')
            if ram_type in tipos_ram_soportados:
                ram_compatible.append(ram)
        
        return ram_compatible, list(tipos_ram_soportados)
    
    def filtrar_cases_por_motherboard_form_factor(self, form_factor: str) -> List[Dict]:
        """
        Filtra gabinetes compatibles con el form factor de motherboard
        
        Args:
            form_factor: Form factor de motherboard (ATX, micro-ATX, mini-ITX)
            
        Returns:
            Lista de gabinetes compatibles
        """
        cases_compatibles = []
        for case in self.datos.get('case', []):
            motherboard_support = case.get('compatibility', {}).get('motherboard', '')
            
            # Lógica de compatibilidad de form factors
            if self._es_case_compatible_con_motherboard(motherboard_support, form_factor):
                cases_compatibles.append(case)
        
        return cases_compatibles
    
    def _es_case_compatible_con_motherboard(self, case_support: str, mb_form_factor: str) -> bool:
        """
        Determina si un gabinete es compatible con un form factor de motherboard
        
        Args:
            case_support: Soporte de motherboard del gabinete
            mb_form_factor: Form factor de la motherboard
            
        Returns:
            True si es compatible
        """
        # Verificar que los parámetros no sean None
        if not case_support or not mb_form_factor:
            return False
            
        # Jerarquía de form factors: un case que soporta un form factor más grande
        # puede acomodar form factors más pequeños
        form_factor_sizes = {
            'e-atx': 4,      # Más grande
            'xl-atx': 3,
            'atx': 2,
            'micro-atx': 1,
            'mini-itx': 0    # Más pequeño
        }
        
        # Normalizar nombres (case-insensitive y manejar variaciones)
        case_support_clean = case_support.strip().lower().replace('_', '-')
        mb_form_factor_clean = mb_form_factor.strip().lower().replace('_', '-')
        
        # Manejar variaciones de nombres
        name_variations = {
            'matx': 'micro-atx',
            'µatx': 'micro-atx',
            'uatx': 'micro-atx',
            'mitx': 'mini-itx',
            'itx': 'mini-itx'
        }
        
        case_support_clean = name_variations.get(case_support_clean, case_support_clean)
        mb_form_factor_clean = name_variations.get(mb_form_factor_clean, mb_form_factor_clean)
        
        # Si son exactamente iguales
        if case_support_clean == mb_form_factor_clean:
            return True
        
        # Verificar jerarquía: el case debe soportar un form factor >= que la motherboard
        case_size = form_factor_sizes.get(case_support_clean, -1)
        mb_size = form_factor_sizes.get(mb_form_factor_clean, -1)
        
        # Si alguno no se reconoce, intentar comparación exacta
        if case_size == -1 or mb_size == -1:
            return case_support_clean == mb_form_factor_clean
        
        # El case debe soportar un form factor mayor o igual que la motherboard
        return case_size >= mb_size
    
    def filtrar_psu_por_case_y_componentes(self, case_data: Dict = None, 
                                         componentes_seleccionados: Dict = None) -> List[Dict]:
        """
        Filtra PSU por compatibilidad con gabinete y requerimientos de potencia
        
        Args:
            case_data: Datos del gabinete seleccionado
            componentes_seleccionados: Componentes ya seleccionados para calcular potencia
            
        Returns:
            Lista de PSU compatibles
        """
        psus_compatibles = []
        
        # Determinar form factor compatible del PSU
        case_psu_support = None
        if case_data:
            case_psu_support = case_data.get('compatibility', {}).get('power_supply')
        
        # Calcular potencia requerida aproximada
        potencia_requerida = self._calcular_potencia_requerida(componentes_seleccionados)
        
        for psu in self.datos.get('psu', []):
            psu_form_factor = psu.get('form_factor')
            psu_wattage = psu.get('power', {}).get('wattage', {}).get('value', 0)
            
            # Verificar compatibilidad de form factor
            compatible_form_factor = True
            if case_psu_support and psu_form_factor:
                compatible_form_factor = (case_psu_support == psu_form_factor)
            
            # Verificar potencia suficiente (con margen de seguridad del 20%)
            potencia_suficiente = psu_wattage >= (potencia_requerida * 1.2)
            
            if compatible_form_factor and potencia_suficiente:
                psus_compatibles.append(psu)
        
        return psus_compatibles
    
    def _calcular_potencia_requerida(self, componentes: Dict = None) -> float:
        """
        Calcula la potencia aproximada requerida por los componentes seleccionados
        
        Args:
            componentes: Diccionario con componentes seleccionados
            
        Returns:
            Potencia total requerida en watts
        """
        if not componentes:
            return 300  # Estimación base
        
        potencia_total = 0
        
        # CPU TDP
        if 'cpu' in componentes:
            cpu_data = componentes['cpu']
            # Intentar múltiples formas de acceder al TDP
            cpu_tdp = None
            if isinstance(cpu_data.get('architecture'), dict):
                tdp_info = cpu_data['architecture'].get('tdp')
                if isinstance(tdp_info, dict):
                    cpu_tdp = tdp_info.get('value', 65)
                elif isinstance(tdp_info, (int, float)):
                    cpu_tdp = tdp_info
            
            # Fallback a otros campos posibles
            if cpu_tdp is None:
                cpu_tdp = cpu_data.get('tdp', 65)
                
            potencia_total += cpu_tdp if isinstance(cpu_tdp, (int, float)) else 65
        
        # GPU (estimación basada en categoría)
        if 'gpu' in componentes:
            gpu_data = componentes['gpu']
            gpu_category = 'mid_range'  # Default
            
            if isinstance(gpu_data.get('calculated_metrics'), dict):
                gpu_category = gpu_data['calculated_metrics'].get('gpu_category', 'mid_range')
            
            gpu_power_map = {
                'entry_level': 75,
                'budget': 120,
                'mid_range': 180,
                'high_end': 250,
                'enthusiast': 320,
                'flagship': 400
            }
            potencia_total += gpu_power_map.get(gpu_category, 180)
        
        # Motherboard y RAM (estimación fija)
        potencia_total += 50  # Motherboard, RAM, almacenamiento
        
        # Ventiladores y periféricos
        potencia_total += 30
        
        return max(potencia_total, 300)  # Mínimo 300W
    
    def verificar_compatibilidad_completa(self, configuracion: Dict) -> Dict[str, Any]:
        """
        Verifica la compatibilidad completa de una configuración
        
        Args:
            configuracion: Diccionario con todos los componentes seleccionados
            
        Returns:
            Diccionario con resultados de compatibilidad
        """
        resultados = {
            'compatible': True,
            'advertencias': [],
            'errores': [],
            'recomendaciones': []
        }
        
        # Verificar CPU y Motherboard
        if 'cpu' in configuracion and 'motherboard' in configuracion:
            cpu_socket = configuracion['cpu'].get('architecture', {}).get('socket')
            mb_socket = configuracion['motherboard'].get('platform', {}).get('socket')
            
            if cpu_socket != mb_socket:
                resultados['errores'].append(
                    f"Incompatibilidad de socket: CPU ({cpu_socket}) vs Motherboard ({mb_socket})"
                )
                resultados['compatible'] = False
        
        # Verificar RAM y Motherboard
        if 'ram' in configuracion and 'motherboard' in configuracion:
            ram_type = configuracion['ram'].get('memory_specs', {}).get('ram_type', {}).get('generation')
            mb_ram_type = configuracion['motherboard'].get('memory', {}).get('type')
            
            if ram_type != mb_ram_type:
                resultados['errores'].append(
                    f"Incompatibilidad de RAM: RAM ({ram_type}) vs Motherboard ({mb_ram_type})"
                )
                resultados['compatible'] = False
        
        # Verificar Case y Motherboard
        if 'case' in configuracion and 'motherboard' in configuracion:
            case_mb_support = configuracion['case'].get('compatibility', {}).get('motherboard')
            mb_form_factor = configuracion['motherboard'].get('form_factor')
            
            # Solo verificar si ambos valores están disponibles
            if case_mb_support and mb_form_factor:
                if not self._es_case_compatible_con_motherboard(case_mb_support, mb_form_factor):
                    resultados['errores'].append(
                        f"Incompatibilidad de form factor: Case ({case_mb_support}) vs Motherboard ({mb_form_factor})"
                    )
                    resultados['compatible'] = False
            elif not case_mb_support:
                resultados['advertencias'].append(
                    "Case seleccionado no especifica compatibilidad de motherboard"
                )
            elif not mb_form_factor:
                resultados['advertencias'].append(
                    "Motherboard seleccionada no especifica form factor"
                )
        
        # Verificar potencia PSU
        if 'psu' in configuracion:
            potencia_requerida = self._calcular_potencia_requerida(configuracion)
            
            # Extraer potencia de PSU con manejo robusto
            psu_data = configuracion['psu']
            psu_wattage = 0
            
            # Intentar diferentes formas de acceder a la potencia
            if 'power' in psu_data and isinstance(psu_data['power'], dict):
                power_info = psu_data['power']
                if 'wattage' in power_info and isinstance(power_info['wattage'], dict):
                    psu_wattage = power_info['wattage'].get('value', 0)
                elif 'wattage' in power_info:
                    psu_wattage = power_info.get('wattage', 0)
            
            # Fallback directo
            if psu_wattage == 0:
                psu_wattage = psu_data.get('wattage', 0)
            
            if psu_wattage > 0:  # Solo validar si tenemos datos de potencia
                if psu_wattage < potencia_requerida:
                    resultados['errores'].append(
                        f"PSU insuficiente: {int(psu_wattage)}W vs {int(potencia_requerida)}W requeridos"
                    )
                    resultados['compatible'] = False
                elif psu_wattage < potencia_requerida * 1.2:
                    resultados['advertencias'].append(
                        f"PSU con margen ajustado: {int(psu_wattage)}W vs {int(potencia_requerida)}W requeridos (recomendado: {int(potencia_requerida * 1.2)}W)"
                    )
            else:
                resultados['advertencias'].append(
                    "PSU seleccionado no especifica potencia"
                )
        
        return resultados
    
    def obtener_sugerencias_componentes(self, filtro: FiltroCompatibilidad) -> Dict[str, List[Dict]]:
        """
        Obtiene sugerencias de componentes basadas en los filtros actuales
        
        Args:
            filtro: Configuración de filtros actual
            
        Returns:
            Diccionario con sugerencias por tipo de componente
        """
        sugerencias = {}
        
        # CPUs
        if filtro.arquitectura:
            sugerencias['cpus'] = self.filtrar_cpus_por_arquitectura(filtro.arquitectura.value)
        
        # Motherboards
        if filtro.socket_cpu:
            sugerencias['motherboards'] = self.filtrar_motherboards_por_socket(filtro.socket_cpu)
        
        # RAM
        if filtro.socket_cpu or filtro.motherboard_form_factor:
            ram_compatible, tipos_soportados = self.filtrar_ram_por_motherboard(
                filtro.socket_cpu, filtro.motherboard_form_factor
            )
            sugerencias['ram'] = ram_compatible
            sugerencias['tipos_ram_soportados'] = tipos_soportados
        
        # Cases
        if filtro.motherboard_form_factor:
            sugerencias['cases'] = self.filtrar_cases_por_motherboard_form_factor(
                filtro.motherboard_form_factor
            )
        
        return sugerencias
    
    def obtener_estadisticas_filtros(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre los datos disponibles para filtros
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {}
        
        # Arquitecturas disponibles
        stats['arquitecturas'] = self.obtener_arquitecturas_disponibles()
        
        # Sockets por arquitectura
        stats['sockets_por_arquitectura'] = {}
        for arch in stats['arquitecturas']:
            stats['sockets_por_arquitectura'][arch] = self.obtener_sockets_por_arquitectura(arch)
        
        # Form factors de motherboards
        stats['form_factors_motherboard'] = self.obtener_form_factors_motherboard()
        
        # Tipos de RAM disponibles
        tipos_ram = set()
        for ram in self.datos.get('ram', []):
            ram_type = ram.get('memory_specs', {}).get('ram_type', {}).get('generation')
            if ram_type:
                tipos_ram.add(ram_type)
        stats['tipos_ram'] = sorted(list(tipos_ram))
        
        # Form factors de PSU
        form_factors_psu = set()
        for psu in self.datos.get('psu', []):
            if psu.get('form_factor'):
                form_factors_psu.add(psu['form_factor'])
        stats['form_factors_psu'] = sorted(list(form_factors_psu))
        
        return stats


class FiltroAvanzado:
    """Clase para filtros más específicos y avanzados"""
    
    def __init__(self, gestor_filtros: GestorFiltros):
        self.gestor = gestor_filtros
    
    def filtrar_por_precio(self, componentes: List[Dict], precio_min: float = None, 
                          precio_max: float = None) -> List[Dict]:
        """
        Filtra componentes por rango de precio (si está disponible)
        
        Args:
            componentes: Lista de componentes
            precio_min: Precio mínimo
            precio_max: Precio máximo
            
        Returns:
            Lista filtrada
        """
        if not precio_min and not precio_max:
            return componentes
        
        componentes_filtrados = []
        for comp in componentes:
            precio = comp.get('price', {}).get('value', 0)
            if precio == 0:  # Si no hay precio, incluir
                componentes_filtrados.append(comp)
                continue
                
            if precio_min and precio < precio_min:
                continue
            if precio_max and precio > precio_max:
                continue
            componentes_filtrados.append(comp)
        
        return componentes_filtrados
    
    def filtrar_cpus_por_rendimiento(self, cpus: List[Dict], 
                                   categoria: str = None,
                                   cores_min: int = None,
                                   threads_min: int = None,
                                   tdp_max: float = None) -> List[Dict]:
        """
        Filtra CPUs por características de rendimiento
        
        Args:
            cpus: Lista de CPUs
            categoria: Categoría de rendimiento
            cores_min: Número mínimo de cores
            threads_min: Número mínimo de threads
            tdp_max: TDP máximo
            
        Returns:
            Lista de CPUs filtradas
        """
        cpus_filtrados = []
        
        for cpu in cpus:
            arch = cpu.get('architecture', {})
            metrics = cpu.get('calculated_metrics', {})
            
            # Filtro por categoría
            if categoria and metrics.get('cpu_category') != categoria:
                continue
            
            # Filtro por cores
            if cores_min and arch.get('cores', 0) < cores_min:
                continue
            
            # Filtro por threads
            if threads_min and arch.get('threads', 0) < threads_min:
                continue
            
            # Filtro por TDP
            if tdp_max and arch.get('tdp', {}).get('value', 999) > tdp_max:
                continue
            
            cpus_filtrados.append(cpu)
        
        return cpus_filtrados
    
    def filtrar_ram_por_especificaciones(self, rams: List[Dict],
                                       capacidad_min: float = None,
                                       frecuencia_min: float = None,
                                       tipo_especifico: str = None) -> List[Dict]:
        """
        Filtra RAM por especificaciones técnicas
        
        Args:
            rams: Lista de módulos RAM
            capacidad_min: Capacidad mínima en GB
            frecuencia_min: Frecuencia mínima en MHz
            tipo_especifico: Tipo específico de RAM
            
        Returns:
            Lista de RAM filtrada
        """
        rams_filtradas = []
        
        for ram in rams:
            specs = ram.get('memory_specs', {})
            
            # Filtro por capacidad
            if capacidad_min:
                capacidad = specs.get('capacity', {}).get('value', 0)
                if capacidad < capacidad_min:
                    continue
            
            # Filtro por frecuencia
            if frecuencia_min:
                frecuencia = specs.get('frequency', {}).get('value', 0)
                if frecuencia < frecuencia_min:
                    continue
            
            # Filtro por tipo específico
            if tipo_especifico:
                tipo = specs.get('ram_type', {}).get('generation', '')
                if tipo != tipo_especifico:
                    continue
            
            rams_filtradas.append(ram)
        
        return rams_filtradas
    
    def filtrar_gpus_por_rendimiento(self, gpus: List[Dict],
                                   categoria: str = None,
                                   vram_min: float = None) -> List[Dict]:
        """
        Filtra GPUs por rendimiento y características
        
        Args:
            gpus: Lista de GPUs
            categoria: Categoría de rendimiento
            vram_min: VRAM mínima en GB
            
        Returns:
            Lista de GPUs filtradas
        """
        gpus_filtradas = []
        
        for gpu in gpus:
            metrics = gpu.get('calculated_metrics', {})
            memory = gpu.get('memory', {})
            
            # Filtro por categoría
            if categoria and metrics.get('gpu_category') != categoria:
                continue
            
            # Filtro por VRAM
            if vram_min:
                vram = memory.get('vram_size', {}).get('gb_equivalent', 0)
                if vram < vram_min:
                    continue
            
            gpus_filtradas.append(gpu)
        
        return gpus_filtradas
    
    def sugerir_configuraciones_balanceadas(self, presupuesto: float = None,
                                          uso_previsto: str = "gaming") -> List[Dict]:
        """
        Sugiere configuraciones completas balanceadas
        
        Args:
            presupuesto: Presupuesto total estimado
            uso_previsto: Tipo de uso (gaming, workstation, office, etc.)
            
        Returns:
            Lista de configuraciones sugeridas
        """
        configuraciones = []
        
        # Configuraciones predefinidas por uso
        if uso_previsto == "gaming":
            configuraciones.extend(self._generar_configs_gaming(presupuesto))
        elif uso_previsto == "workstation":
            configuraciones.extend(self._generar_configs_workstation(presupuesto))
        elif uso_previsto == "office":
            configuraciones.extend(self._generar_configs_office(presupuesto))
        
        return configuraciones
    
    def _generar_configs_gaming(self, presupuesto: float = None) -> List[Dict]:
        """Genera configuraciones optimizadas para gaming"""
        configs = []
        
        # Config gaming básica (AMD)
        config_basica = {
            'nombre': 'Gaming Básico AMD',
            'descripcion': 'Configuración de entrada para gaming 1080p',
            'filtros': {
                'arquitectura': 'AMD',
                'socket_sugerido': 'AM4',
                'cpu_categoria': 'budget_gaming',
                'gpu_categoria': 'budget',
                'ram_capacidad_min': 16,
                'ram_tipo': 'DDR4'
            }
        }
        configs.append(config_basica)
        
        # Config gaming media (AMD)
        config_media = {
            'nombre': 'Gaming Intermedio AMD',
            'descripcion': 'Configuración balanceada para gaming 1440p',
            'filtros': {
                'arquitectura': 'AMD',
                'socket_sugerido': 'AM4',
                'cpu_categoria': 'performance_standard',
                'gpu_categoria': 'mid_range',
                'ram_capacidad_min': 16,
                'ram_tipo': 'DDR4'
            }
        }
        configs.append(config_media)
        
        # Config gaming alta (Intel)
        config_alta = {
            'nombre': 'Gaming Alto Rendimiento Intel',
            'descripcion': 'Configuración para gaming 4K y alta tasa de frames',
            'filtros': {
                'arquitectura': 'Intel',
                'socket_sugerido': '1700',
                'cpu_categoria': 'high_performance',
                'gpu_categoria': 'high_end',
                'ram_capacidad_min': 32,
                'ram_tipo': 'DDR4'
            }
        }
        configs.append(config_alta)
        
        return configs
    
    def _generar_configs_workstation(self, presupuesto: float = None) -> List[Dict]:
        """Genera configuraciones optimizadas para workstation"""
        return [
            {
                'nombre': 'Workstation AMD Threadripper',
                'descripcion': 'Para renderizado y cálculos pesados',
                'filtros': {
                    'arquitectura': 'AMD',
                    'socket_sugerido': 'TRX40',
                    'cores_min': 12,
                    'ram_capacidad_min': 64,
                    'ram_tipo': 'DDR4'
                }
            }
        ]
    
    def _generar_configs_office(self, presupuesto: float = None) -> List[Dict]:
        """Genera configuraciones optimizadas para oficina"""
        return [
            {
                'nombre': 'Oficina Básica',
                'descripcion': 'Para tareas de oficina y navegación',
                'filtros': {
                    'arquitectura': 'AMD',
                    'socket_sugerido': 'AM4',
                    'cpu_categoria': 'budget',
                    'igpu_requerida': True,
                    'ram_capacidad_min': 8,
                    'ram_tipo': 'DDR4'
                }
            }
        ]


class ValidadorCompatibilidad:
    """Clase especializada en validación profunda de compatibilidad"""
    
    def __init__(self, gestor_filtros: GestorFiltros):
        self.gestor = gestor_filtros
    
    def validar_dimensiones_fisicas(self, configuracion: Dict) -> Dict[str, Any]:
        """
        Valida compatibilidad física entre componentes
        
        Args:
            configuracion: Configuración completa
            
        Returns:
            Resultado de validación
        """
        resultado = {
            'compatible': True,
            'advertencias': [],
            'errores': []
        }
        
        case = configuracion.get('case')
        gpu = configuracion.get('gpu')
        cpu_cooler = configuracion.get('cpu_cooler')
        
        # Verificar GPU vs Case
        if case and gpu:
            max_gpu_length = case.get('compatibility', {}).get('supported_gpu_length', {}).get('value', 0)
            gpu_length = gpu.get('dimensions', {}).get('length', {}).get('value', 0)
            
            if max_gpu_length > 0 and gpu_length > 0:
                if gpu_length > max_gpu_length:
                    resultado['errores'].append(
                        f"GPU muy larga: {gpu_length}mm vs {max_gpu_length}mm máximo del case"
                    )
                    resultado['compatible'] = False
                elif gpu_length > max_gpu_length * 0.9:  # Advertencia si está muy cerca
                    resultado['advertencias'].append(
                        f"GPU ajustada: {gpu_length}mm vs {max_gpu_length}mm máximo"
                    )
        
        # Verificar CPU Cooler vs Case
        if case and cpu_cooler:
            max_cooler_height = case.get('compatibility', {}).get('supported_cpu_cooler_height', {}).get('value', 0)
            cooler_height = cpu_cooler.get('dimensions', {}).get('height', {}).get('value', 0)
            
            if max_cooler_height > 0 and cooler_height > 0:
                if cooler_height > max_cooler_height:
                    resultado['errores'].append(
                        f"CPU Cooler muy alto: {cooler_height}mm vs {max_cooler_height}mm máximo"
                    )
                    resultado['compatible'] = False
        
        return resultado
    
    def validar_conectividad(self, configuracion: Dict) -> Dict[str, Any]:
        """
        Valida que haya suficientes conectores y puertos
        
        Args:
            configuracion: Configuración completa
            
        Returns:
            Resultado de validación
        """
        resultado = {
            'compatible': True,
            'advertencias': [],
            'errores': []
        }
        
        motherboard = configuracion.get('motherboard')
        ram_modules = configuracion.get('ram_modules', [])  # Lista de módulos RAM
        storage_devices = configuracion.get('storage_devices', [])  # Lista de almacenamiento
        
        # Verificar slots de RAM
        if motherboard and ram_modules:
            ram_slots_disponibles = motherboard.get('memory', {}).get('slots', 0)
            ram_modules_necesarios = sum(ram.get('memory_specs', {}).get('sticks', 1) for ram in ram_modules)
            
            if ram_modules_necesarios > ram_slots_disponibles:
                resultado['errores'].append(
                    f"No hay suficientes slots de RAM: {ram_modules_necesarios} necesarios vs {ram_slots_disponibles} disponibles"
                )
                resultado['compatible'] = False
        
        # Verificar puertos SATA para almacenamiento
        if motherboard and storage_devices:
            sata_ports = motherboard.get('connectivity', {}).get('sata_ports', 0)
            sata_devices = len([dev for dev in storage_devices if dev.get('interface') == 'SATA'])
            
            if sata_devices > sata_ports:
                resultado['errores'].append(
                    f"No hay suficientes puertos SATA: {sata_devices} necesarios vs {sata_ports} disponibles"
                )
                resultado['compatible'] = False
        
        return resultado
    
    def verificar_refrigeracion(self, configuracion: Dict) -> Dict[str, Any]:
        """
        Verifica que la refrigeración sea adecuada
        
        Args:
            configuracion: Configuración completa
            
        Returns:
            Resultado de verificación
        """
        resultado = {
            'adecuada': True,
            'advertencias': [],
            'recomendaciones': []
        }
        
        cpu = configuracion.get('cpu')
        cpu_cooler = configuracion.get('cpu_cooler')
        case = configuracion.get('case')
        
        # Verificar TDP vs capacidad del cooler
        if cpu and cpu_cooler:
            cpu_tdp = cpu.get('architecture', {}).get('tdp', {}).get('value', 0)
            cooler_tdp = cpu_cooler.get('cooling', {}).get('tdp_max', {}).get('value', 0)
            
            if cooler_tdp > 0 and cpu_tdp > 0:
                if cpu_tdp > cooler_tdp:
                    resultado['advertencias'].append(
                        f"Cooler insuficiente: CPU {cpu_tdp}W vs Cooler {cooler_tdp}W"
                    )
                    resultado['adecuada'] = False
                elif cpu_tdp > cooler_tdp * 0.8:
                    resultado['advertencias'].append(
                        f"Cooler ajustado: CPU {cpu_tdp}W vs Cooler {cooler_tdp}W"
                    )
        
        # Analizar ventilación del case
        if case:
            fan_slots = case.get('fan_support', {})
            total_intake = 0
            total_exhaust = 0
            
            for size, slots in fan_slots.items():
                if isinstance(slots, dict):
                    installed = slots.get('installed', 0)
                    maximum = slots.get('maximum', 0)
                    
                    # Estimación simplificada: los ventiladores frontales son intake,
                    # los traseros y superiores son exhaust
                    if 'front' in size.lower() or 'intake' in size.lower():
                        total_intake += installed
                    else:
                        total_exhaust += installed
            
            if total_intake < total_exhaust:
                resultado['recomendaciones'].append(
                    "Considere agregar más ventiladores de entrada para presión positiva"
                )
        
        return resultado


# Funciones de utilidad para la interfaz
def crear_filtro_desde_seleccion(seleccion: Dict[str, Any]) -> FiltroCompatibilidad:
    """
    Crea un objeto FiltroCompatibilidad a partir de una selección de usuario
    
    Args:
        seleccion: Diccionario con la selección del usuario
        
    Returns:
        Objeto FiltroCompatibilidad configurado
    """
    arquitectura = None
    if seleccion.get('arquitectura'):
        arquitectura = Arquitectura(seleccion['arquitectura'])
    
    return FiltroCompatibilidad(
        arquitectura=arquitectura,
        socket_cpu=seleccion.get('socket_cpu'),
        motherboard_form_factor=seleccion.get('motherboard_form_factor'),
        ram_type=seleccion.get('ram_type'),
        psu_form_factor=seleccion.get('psu_form_factor'),
        case_form_factor=seleccion.get('case_form_factor')
    )


def formatear_componente_para_ui(componente: Dict, tipo: str) -> Dict[str, Any]:
    """
    Formatea un componente para mostrar en la UI
    
    Args:
        componente: Datos del componente
        tipo: Tipo de componente
        
    Returns:
        Diccionario formateado para la UI
    """
    base_info = {
        'id': componente.get('mpn', componente.get('name', 'Unknown')),
        'nombre': componente.get('name', 'Sin nombre'),
        'fabricante': componente.get('producer', 'Sin fabricante'),
        'mpn': componente.get('mpn', ''),
        'tipo': tipo
    }
    
    # Información específica por tipo
    if tipo == 'cpu':
        base_info.update({
            'socket': componente.get('architecture', {}).get('socket', ''),
            'cores': componente.get('architecture', {}).get('cores', 0),
            'threads': componente.get('architecture', {}).get('threads', 0),
            'tdp': componente.get('architecture', {}).get('tdp', {}).get('value', 0),
            'base_clock': componente.get('performance', {}).get('base_clock', {}).get('value', 0),
        })
    
    elif tipo == 'motherboard':
        base_info.update({
            'socket': componente.get('platform', {}).get('socket', ''),
            'chipset': componente.get('platform', {}).get('chipset', ''),
            'form_factor': componente.get('form_factor', ''),
            'ram_type': componente.get('memory', {}).get('type', ''),
            'ram_slots': componente.get('memory', {}).get('slots', 0),
        })
    
    elif tipo == 'ram':
        base_info.update({
            'tipo': componente.get('memory_specs', {}).get('ram_type', {}).get('generation', ''),
            'capacidad': componente.get('memory_specs', {}).get('capacity', {}).get('value', 0),
            'capacidad_unit': componente.get('memory_specs', {}).get('capacity', {}).get('unit', 'GB'),
            'frecuencia': componente.get('memory_specs', {}).get('frequency', {}).get('value', 0),
            'sticks': componente.get('memory_specs', {}).get('sticks', 1),
            'timings': componente.get('memory_specs', {}).get('timings', {}).get('raw_value', ''),
        })
    
    elif tipo == 'case':
        base_info.update({
            'motherboard_support': componente.get('compatibility', {}).get('motherboard', ''),
            'psu_support': componente.get('compatibility', {}).get('power_supply', ''),
            'max_gpu_length': componente.get('compatibility', {}).get('supported_gpu_length', {}).get('value', 0),
        })
    
    elif tipo == 'psu':
        base_info.update({
            'wattage': componente.get('power', {}).get('wattage', {}).get('value', 0),
            'efficiency': componente.get('power', {}).get('efficiency', {}).get('full_rating', ''),
            'form_factor': componente.get('form_factor', ''),
        })
    
    elif tipo == 'gpu':
        base_info.update({
            'vram': componente.get('performance', {}).get('vram', {}).get('value', 0),
            'length': componente.get('physical', {}).get('length', {}).get('value', 0),
            'slots': componente.get('physical', {}).get('slots', 0),
            'tdp': componente.get('performance', {}).get('tdp', {}).get('value', 0),
            'boost_clock': componente.get('performance', {}).get('boost_clock', {}).get('value', 0),
        })
    
    elif tipo == 'ssd':
        base_info.update({
            'capacity': componente.get('storage_specs', {}).get('capacity', {}).get('value', 0),
            'capacity_unit': componente.get('storage_specs', {}).get('capacity', {}).get('unit', 'GB'),
            'form_factor': componente.get('storage_specs', {}).get('form_factor', ''),
            'protocol': componente.get('storage_specs', {}).get('protocol', ''),
            'nand_type': componente.get('technical_specs', {}).get('nand_type', ''),
        })
    
    elif tipo == 'hdd':
        # Manejar valores None de manera segura
        cache_value = componente.get('performance_specs', {}).get('cache', {}).get('value', 0)
        cache_value = cache_value if cache_value is not None else 0
        
        base_info.update({
            'capacity': componente.get('storage_specs', {}).get('capacity', {}).get('value', 0),
            'capacity_unit': componente.get('storage_specs', {}).get('capacity', {}).get('unit', 'GB'),
            'rpm': componente.get('performance_specs', {}).get('rpm', 0),
            'cache': cache_value,
            'cache_unit': componente.get('performance_specs', {}).get('cache', {}).get('unit', 'MB'),
        })
    
    elif tipo == 'cpu_cooler':
        # Manejar valores None de manera segura
        tdp_value = componente.get('specifications', {}).get('tdp', {}).get('value', 0)
        height_value = componente.get('specifications', {}).get('height', {}).get('value', 0)
        
        base_info.update({
            'tdp': tdp_value if tdp_value is not None else 0,
            'height': height_value if height_value is not None else 0,
            'supported_sockets': componente.get('specifications', {}).get('supported_sockets', {}).get('sockets', []),
            'socket_count': componente.get('specifications', {}).get('supported_sockets', {}).get('count', 0),
        })
    
    return base_info


# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar gestor de filtros
    ruta_datos = r"c:\Users\Neptuno.PC\Documents\0_PYTHON_PROGRAMAS\matev4\normalizadordataset\normalized_data"
    gestor = GestorFiltros(ruta_datos)
    
    # Mostrar estadísticas
    print("=== ESTADÍSTICAS DE FILTROS ===")
    stats = gestor.obtener_estadisticas_filtros()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Ejemplo de flujo de filtrado
    print("\n=== EJEMPLO DE FILTRADO ===")
    
    # 1. Seleccionar arquitectura AMD
    arquitectura = "AMD"
    print(f"1. Arquitectura seleccionada: {arquitectura}")
    
    # 2. Obtener sockets disponibles
    sockets = gestor.obtener_sockets_por_arquitectura(arquitectura)
    print(f"2. Sockets disponibles: {sockets}")
    
    # 3. Seleccionar socket AM4
    socket_seleccionado = "AM4"
    print(f"3. Socket seleccionado: {socket_seleccionado}")
    
    # 4. Obtener motherboards compatibles
    motherboards = gestor.filtrar_motherboards_por_socket(socket_seleccionado)
    print(f"4. Motherboards compatibles: {len(motherboards)} encontradas")
    
    # 5. Obtener form factors disponibles
    form_factors = gestor.obtener_form_factors_motherboard(socket_seleccionado)
    print(f"5. Form factors disponibles: {form_factors}")
    
    # 6. Ejemplo de verificación completa
    print("\n=== VERIFICACIÓN DE COMPATIBILIDAD ===")
    configuracion_ejemplo = {
        'cpu': motherboards[0] if motherboards else {},  # Esto sería un CPU real
        'motherboard': motherboards[0] if motherboards else {},
    }
    
    if motherboards:
        resultado = gestor.verificar_compatibilidad_completa(configuracion_ejemplo)
        print(f"Compatibilidad: {resultado}")


# Función de utilidad para crear un workflow completo
def crear_workflow_seleccion_componentes(ruta_datos: str) -> Dict[str, Any]:
    """
    Crea un workflow completo para la selección de componentes
    
    Args:
        ruta_datos: Ruta a los datos normalizados
        
    Returns:
        Diccionario con todas las herramientas necesarias
    """
    gestor = GestorFiltros(ruta_datos)
    filtro_avanzado = FiltroAvanzado(gestor)
    validador = ValidadorCompatibilidad(gestor)
    
    return {
        'gestor_filtros': gestor,
        'filtro_avanzado': filtro_avanzado,
        'validador': validador,
        'estadisticas': gestor.obtener_estadisticas_filtros()
    }


# Ejemplo de uso del workflow completo
if __name__ == "__main__":
    print("\n=== WORKFLOW COMPLETO ===")
    
    ruta_datos = r"c:\Users\Neptuno.PC\Documents\0_PYTHON_PROGRAMAS\matev4\normalizadordataset\normalized_data"
    workflow = crear_workflow_seleccion_componentes(ruta_datos)
    
    # Ejemplo: Obtener sugerencias para gaming
    filtro_avanzado = workflow['filtro_avanzado']
    configs_gaming = filtro_avanzado.sugerir_configuraciones_balanceadas(uso_previsto="gaming")
    
    print(f"Configuraciones de gaming sugeridas: {len(configs_gaming)}")
    for config in configs_gaming:
        print(f"- {config['nombre']}: {config['descripcion']}")
    
    # Ejemplo: Filtrar CPUs AMD para gaming
    gestor = workflow['gestor_filtros']
    cpus_amd = gestor.filtrar_cpus_por_arquitectura("AMD")
    
    # Aplicar filtros específicos
    cpus_gaming = filtro_avanzado.filtrar_cpus_por_rendimiento(
        cpus_amd, 
        cores_min=6, 
        tdp_max=150
    )
    
    print(f"\nCPUs AMD para gaming (6+ cores, ≤150W TDP): {len(cpus_gaming)}")
    
    # Mostrar algunos ejemplos
    for i, cpu in enumerate(cpus_gaming[:3]):
        cpu_formatted = formatear_componente_para_ui(cpu, 'cpu')
        print(f"{i+1}. {cpu_formatted['nombre']} - {cpu_formatted['cores']}C/{cpu_formatted['threads']}T - {cpu_formatted['tdp']}W")