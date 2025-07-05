import re
import json
import csv
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class Dimension:
    """Clase para representar dimensiones separando valor y unidad"""
    value: Optional[float] = None
    unit: Optional[str] = None
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, dimension_str: str) -> 'Dimension':
        """Convierte string como '230 mm' en objeto Dimension"""
        if not dimension_str or dimension_str.strip() == '':
            return cls(raw_value=dimension_str)
        
        # Patrón para extraer número y unidad
        pattern = r'^(\d+(?:\.\d+)?)\s*(\w+)$'
        match = re.match(pattern, dimension_str.strip())
        
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            return cls(value=value, unit=unit, raw_value=dimension_str)
        else:
            return cls(raw_value=dimension_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'value': self.value,
            'unit': self.unit,
            'raw_value': self.raw_value
        }


@dataclass
class FanSlots:
    """Clase para representar slots de ventiladores (formato: instalados/máximo)"""
    installed: Optional[int] = None
    maximum: Optional[int] = None
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, fan_str: str) -> 'FanSlots':
        """Convierte string como '2/6' en objeto FanSlots"""
        if not fan_str or fan_str.strip() == '':
            return cls(raw_value=fan_str)
        
        # Patrón para formato instalados/máximo
        pattern = r'^(\d+)/(\d+)$'
        match = re.match(pattern, fan_str.strip())
        
        if match:
            installed = int(match.group(1))
            maximum = int(match.group(2))
            return cls(installed=installed, maximum=maximum, raw_value=fan_str)
        else:
            return cls(raw_value=fan_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'installed': self.installed,
            'maximum': self.maximum,
            'raw_value': self.raw_value
        }


@dataclass
class Price:
    """Clase para representar precios separando valor y moneda"""
    value: Optional[float] = None
    currency: Optional[str] = None
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, price_str: str) -> 'Price':
        """Convierte string como '$87.03 USD' en objeto Price"""
        if not price_str or price_str.strip() == '':
            return cls(raw_value=price_str)
        
        # Patrón para extraer precio y moneda
        pattern = r'^\$?(\d+(?:\.\d+)?)\s*(\w+)?$'
        match = re.match(pattern, price_str.strip())
        
        if match:
            value = float(match.group(1))
            currency = match.group(2) if match.group(2) else 'USD'
            return cls(value=value, currency=currency, raw_value=price_str)
        else:
            return cls(raw_value=price_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'value': self.value,
            'currency': self.currency,
            'raw_value': self.raw_value
        }


class BaseNormalizer(ABC):
    """Clase base abstracta para normalizadores de componentes"""
    
    def __init__(self):
        self.normalized_data: List[Dict[str, Any]] = []
    
    @abstractmethod
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila del CSV"""
        pass
    
    def normalize_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Normaliza un archivo CSV completo"""
        self.normalized_data = []
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                normalized_row = self.normalize_row(row)
                self.normalized_data.append(normalized_row)
        
        return self.normalized_data
    
    def save_to_json(self, output_path: str, indent: int = 2) -> None:
        """Guarda los datos normalizados en formato JSON"""
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(self.normalized_data, file, indent=indent, ensure_ascii=False)
    
    def get_normalized_data(self) -> List[Dict[str, Any]]:
        """Retorna los datos normalizados"""
        return self.normalized_data


class CaseDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de gabinetes/cases"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de CaseData.csv"""
        normalized = {
            # Información básica (mantenemos tal como está excepto precio)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Dimensiones físicas (separamos valor y unidad)
            'dimensions': {
                'width': Dimension.from_string(row.get('Width', '')).to_dict(),
                'depth': Dimension.from_string(row.get('Depth', '')).to_dict(),
                'height': Dimension.from_string(row.get('Height', '')).to_dict()
            },
            
            # Compatibilidad de motherboard y PSU
            'compatibility': {
                'motherboard': row.get('Motherboard', '').strip(),
                'power_supply': row.get('Power Supply', '').strip(),
                'supported_gpu_length': Dimension.from_string(row.get('Supported GPU Length', '')).to_dict(),
                'supported_cpu_cooler_height': Dimension.from_string(row.get('Supported CPU Cooler Height', '')).to_dict()
            },
            
            # Soporte de ventiladores (separamos instalados/máximo)
            'fan_support': {
                '80mm': FanSlots.from_string(row.get('80mm Fans', '')).to_dict(),
                '120mm': FanSlots.from_string(row.get('120mm Fans', '')).to_dict(),
                '140mm': FanSlots.from_string(row.get('140mm Fans', '')).to_dict(),
                '200mm': FanSlots.from_string(row.get('200mm Fans', '')).to_dict()
            },
            
            # Soporte de radiadores (valores numéricos)
            'radiator_support': {
                '120mm': self._parse_int_or_empty(row.get('120mm Radiator Support', '')),
                '140mm': self._parse_int_or_empty(row.get('140mm Radiator Support', '')),
                '240mm': self._parse_int_or_empty(row.get('240mm Radiator Support', '')),
                '280mm': self._parse_int_or_empty(row.get('280mm Radiator Support', '')),
                '360mm': self._parse_int_or_empty(row.get('360mm Radiator Support', ''))
            },
            
            # Almacenamiento (cantidad de bahías)
            'storage_bays': {
                'disk_2_5_inch': self._parse_int_or_empty(row.get('Disk 2.5"', '')),
                'disk_3_5_inch': self._parse_int_or_empty(row.get('Disk 3.5"', '')),
                'disk_2_5_3_5_inch': self._parse_int_or_empty(row.get('Disk 2.5"/3.5"', '')),
                'disk_5_25_inch': self._parse_int_or_empty(row.get('Disk 5.25"', ''))
            },
            
            # Características estéticas y funcionales
            'features': {
                'primary_colors': self._parse_colors(row.get('Primary Color(s)', '')),
                'window': self._parse_boolean(row.get('Window', '')),
                'dust_filter': self._parse_boolean(row.get('Dust Filter', '')),
                'cable_management': self._parse_boolean(row.get('Cable Management', '')),
                'noise_isolation': self._parse_boolean(row.get('Noise Isolation', ''))
            }
            
            # Nota: Excluimos Price y Product Page como solicitado
        }
        
        return normalized
    
    def _parse_int_or_empty(self, value: str) -> Optional[int]:
        """Convierte string a int o None si está vacío"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None
    
    def _parse_boolean(self, value: str) -> Optional[bool]:
        """Convierte string a boolean"""
        if not value or value.strip() == '':
            return None
        value_lower = value.strip().lower()
        if value_lower in ['true', '1', 'yes', 'on']:
            return True
        elif value_lower in ['false', '0', 'no', 'off']:
            return False
        return None
    
    def _parse_colors(self, colors_str: str) -> List[str]:
        """Parsea colores separados por comas"""
        if not colors_str or colors_str.strip() == '':
            return []
        return [color.strip() for color in colors_str.split(',') if color.strip()]


@dataclass
class ThermalDesignPower:
    """Clase para representar TDP (Thermal Design Power) con valor y unidad"""
    value: Optional[float] = None
    unit: Optional[str] = None
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, tdp_str: str) -> 'ThermalDesignPower':
        """Convierte string como '200 W' en objeto ThermalDesignPower"""
        if not tdp_str or tdp_str.strip() == '':
            return cls(raw_value=tdp_str)
        
        # Patrón para extraer potencia y unidad
        pattern = r'^(\d+(?:\.\d+)?)\s*(\w+)$'
        match = re.match(pattern, tdp_str.strip())
        
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            return cls(value=value, unit=unit, raw_value=tdp_str)
        else:
            return cls(raw_value=tdp_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'value': self.value,
            'unit': self.unit,
            'raw_value': self.raw_value
        }


@dataclass
class SocketSupport:
    """Clase para representar sockets soportados"""
    sockets: List[str] = field(default_factory=list)
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, sockets_str: str) -> 'SocketSupport':
        """Convierte string de sockets separados por comas"""
        if not sockets_str or sockets_str.strip() == '':
            return cls(raw_value=sockets_str)
        
        # Limpiar y separar sockets
        sockets = []
        for socket in sockets_str.split(','):
            socket = socket.strip()
            if socket:
                sockets.append(socket)
        
        return cls(sockets=sockets, raw_value=sockets_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'sockets': self.sockets,
            'count': len(self.sockets),
            'raw_value': self.raw_value
        }
    
    def supports_socket(self, socket: str) -> bool:
        """Verifica si soporta un socket específico"""
        return socket in self.sockets
    
    def get_socket_families(self) -> Dict[str, List[str]]:
        """Agrupa sockets por familia (Intel/AMD)"""
        intel_sockets = []
        amd_sockets = []
        
        for socket in self.sockets:
            # Sockets Intel típicamente son números
            if socket.isdigit() or socket.startswith('LGA'):
                intel_sockets.append(socket)
            # Sockets AMD típicamente contienen letras
            elif any(x in socket.upper() for x in ['AM', 'FM', 'TR4', 'sTRX4']):
                amd_sockets.append(socket)
            else:
                # Si no podemos determinar, lo ponemos en ambos
                intel_sockets.append(socket)
                amd_sockets.append(socket)
        
        return {
            'intel': intel_sockets,
            'amd': amd_sockets
        }


class CPUCoolerDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de CPU Coolers"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de CPUCoolerData.csv"""
        normalized = {
            # Información básica (mantenemos tal como está excepto precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones térmicas y físicas
            'specifications': {
                'supported_sockets': SocketSupport.from_string(row.get('Supported Sockets', '')).to_dict(),
                'height': Dimension.from_string(row.get('Height', '')).to_dict(),
                'tdp': ThermalDesignPower.from_string(row.get('TDP', '')).to_dict()
            },
            
            # Configuración de ventiladores incluidos
            'included_fans': {
                '80mm': self._parse_int_or_empty(row.get('80mm Fans', '')),
                '92mm': self._parse_int_or_empty(row.get('92mm Fans', '')),
                '120mm': self._parse_int_or_empty(row.get('120mm Fans', '')),
                '140mm': self._parse_int_or_empty(row.get('140mm Fans', '')),
                '200mm': self._parse_int_or_empty(row.get('200mm Fans', ''))
            },
            
            # Características adicionales
            'features': {
                'additional_fan_support': self._parse_boolean(row.get('Additional Fan Support', '')),
                'total_fans': self._calculate_total_fans(row)
            },
            
            # Análisis de compatibilidad
            'compatibility_analysis': self._analyze_compatibility(row)
        }
        
        return normalized
    
    def _calculate_total_fans(self, row: Dict[str, str]) -> int:
        """Calcula el total de ventiladores incluidos"""
        total = 0
        fan_sizes = ['80mm Fans', '92mm Fans', '120mm Fans', '140mm Fans', '200mm Fans']
        
        for fan_size in fan_sizes:
            fan_count = self._parse_int_or_empty(row.get(fan_size, ''))
            if fan_count is not None:
                total += fan_count
        
        return total
    
    def _analyze_compatibility(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Analiza la compatibilidad del cooler"""
        socket_support = SocketSupport.from_string(row.get('Supported Sockets', ''))
        socket_families = socket_support.get_socket_families()
        
        # Determinar tipo de cooler basado en ventiladores
        cooler_type = self._determine_cooler_type(row)
        
        # Calcular factor forma térmico
        thermal_factor = self._calculate_thermal_factor(row)
        
        return {
            'socket_families': socket_families,
            'supports_intel': len(socket_families['intel']) > 0,
            'supports_amd': len(socket_families['amd']) > 0,
            'is_universal': len(socket_families['intel']) > 0 and len(socket_families['amd']) > 0,
            'cooler_type': cooler_type,
            'thermal_factor': thermal_factor
        }
    
    def _determine_cooler_type(self, row: Dict[str, str]) -> str:
        """Determina el tipo de cooler basado en características"""
        name = row.get('Name', '').lower()
        total_fans = self._calculate_total_fans(row)
        height = Dimension.from_string(row.get('Height', '')).value
        
        if 'liquid' in name or 'aio' in name:
            return 'liquid'
        elif height and height == 0:
            return 'liquid'  # Altura 0 típicamente indica AIO
        elif total_fans == 0:
            return 'passive'
        elif total_fans == 1:
            return 'single_fan'
        elif total_fans == 2:
            return 'dual_fan'
        elif total_fans > 2:
            return 'multi_fan'
        else:
            return 'air_tower'  # Valor por defecto
    
    def _calculate_thermal_factor(self, row: Dict[str, str]) -> Optional[float]:
        """Calcula un factor térmico basado en TDP y ventiladores"""
        tdp = ThermalDesignPower.from_string(row.get('TDP', '')).value
        total_fans = self._calculate_total_fans(row)
        height = Dimension.from_string(row.get('Height', '')).value
        
        if not tdp:
            return None
        
        # Factor básico: TDP por ventilador
        base_factor = tdp / max(total_fans, 1) if total_fans > 0 else tdp
        
        # Ajuste por altura (más altura = mejor disipación)
        if height and height > 0:
            height_factor = min(height / 150, 2.0)  # Normalizar a 150mm, máximo 2x
            return base_factor / height_factor
        
        return base_factor
    
    def _parse_int_or_empty(self, value: str) -> Optional[int]:
        """Convierte string a int o None si está vacío"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None
    
    def _parse_boolean(self, value: str) -> Optional[bool]:
        """Convierte string a boolean"""
        if not value or value.strip() == '':
            return None
        value_lower = value.strip().lower()
        if value_lower in ['true', '1', 'yes', 'on']:
            return True
        elif value_lower in ['false', '0', 'no', 'off']:
            return False
        return None


@dataclass
class Frequency:
    """Clase para representar frecuencias de CPU con valor y unidad"""
    value: Optional[float] = None
    unit: Optional[str] = None
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, freq_str: str) -> 'Frequency':
        """Convierte string como '3.7 GHz' en objeto Frequency"""
        if not freq_str or freq_str.strip() == '':
            return cls(raw_value=freq_str)
        
        # Patrón para extraer frecuencia y unidad
        pattern = r'^(\d+(?:\.\d+)?)\s*(\w+)$'
        match = re.match(pattern, freq_str.strip())
        
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            return cls(value=value, unit=unit, raw_value=freq_str)
        else:
            return cls(raw_value=freq_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'value': self.value,
            'unit': self.unit,
            'raw_value': self.raw_value
        }
    
    def to_mhz(self) -> Optional[float]:
        """Convierte frecuencia a MHz para comparaciones"""
        if not self.value or not self.unit:
            return None
        
        unit_lower = self.unit.lower()
        if unit_lower == 'ghz':
            return self.value * 1000
        elif unit_lower == 'mhz':
            return self.value
        elif unit_lower == 'khz':
            return self.value / 1000
        
        return None


@dataclass
class IntegratedGPU:
    """Clase para representar GPU integrada"""
    has_igpu: bool = False
    gpu_model: Optional[str] = None
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, igpu_str: str) -> 'IntegratedGPU':
        """Parsea información de GPU integrada"""
        if not igpu_str or igpu_str.strip() == '':
            return cls(raw_value=igpu_str)
        
        igpu_lower = igpu_str.strip().lower()
        
        if igpu_lower in ['false', 'no', '0']:
            return cls(has_igpu=False, raw_value=igpu_str)
        elif igpu_lower in ['true', 'yes', '1']:
            return cls(has_igpu=True, raw_value=igpu_str)
        else:
            # Si contiene texto, es el modelo de la GPU
            return cls(has_igpu=True, gpu_model=igpu_str.strip(), raw_value=igpu_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'has_igpu': self.has_igpu,
            'gpu_model': self.gpu_model,
            'raw_value': self.raw_value
        }


class CPUDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de CPUs"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de CPUData.csv"""
        normalized = {
            # Información básica (excluimos precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones de rendimiento
            'performance': {
                'base_clock': Frequency.from_string(row.get('Base Clock', '')).to_dict(),
                'turbo_clock': Frequency.from_string(row.get('Turbo Clock', '')).to_dict(),
                'unlocked_multiplier': self._parse_boolean(row.get('Unlocked Multiplier', ''))
            },
            
            # Arquitectura del procesador
            'architecture': {
                'cores': self._parse_int_or_empty(row.get('Cores', '')),
                'threads': self._parse_int_or_empty(row.get('Threads', '')),
                'tdp': ThermalDesignPower.from_string(row.get('TDP', '')).to_dict(),
                'socket': row.get('Socket', '').strip()
            },
            
            # GPU integrada
            'integrated_graphics': IntegratedGPU.from_string(row.get('Integrated GPU', '')).to_dict(),
            
            # Análisis calculado
            'calculated_metrics': self._calculate_metrics(row)
        }
        
        return normalized
    
    def _calculate_metrics(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Calcula métricas adicionales basadas en especificaciones"""
        metrics = {
            'threads_per_core': None,
            'frequency_boost_ratio': None,
            'performance_score': None,
            'efficiency_score': None,
            'cpu_category': None
        }
        
        # Calcular threads por core
        cores = self._parse_int_or_empty(row.get('Cores', ''))
        threads = self._parse_int_or_empty(row.get('Threads', ''))
        if cores and threads and cores > 0:
            metrics['threads_per_core'] = threads / cores
        
        # Calcular ratio de boost de frecuencia
        base_freq = Frequency.from_string(row.get('Base Clock', ''))
        turbo_freq = Frequency.from_string(row.get('Turbo Clock', ''))
        
        if base_freq.value and turbo_freq.value:
            base_mhz = base_freq.to_mhz()
            turbo_mhz = turbo_freq.to_mhz()
            if base_mhz and turbo_mhz and base_mhz > 0:
                metrics['frequency_boost_ratio'] = turbo_mhz / base_mhz
        
        # Calcular puntuación de rendimiento (threads × frecuencia base)
        if threads and base_freq.value:
            base_mhz = base_freq.to_mhz()
            if base_mhz:
                metrics['performance_score'] = threads * base_mhz
        
        # Calcular eficiencia (performance score / TDP)
        tdp = ThermalDesignPower.from_string(row.get('TDP', ''))
        if metrics['performance_score'] and tdp.value and tdp.value > 0:
            metrics['efficiency_score'] = metrics['performance_score'] / tdp.value
        
        # Categorizar CPU
        metrics['cpu_category'] = self._categorize_cpu(row)
        
        return metrics
    
    def _categorize_cpu(self, row: Dict[str, str]) -> str:
        """Categoriza el CPU basado en especificaciones"""
        cores = self._parse_int_or_empty(row.get('Cores', ''))
        threads = self._parse_int_or_empty(row.get('Threads', ''))
        tdp = ThermalDesignPower.from_string(row.get('TDP', ''))
        name = row.get('Name', '').lower()
        
        # Categorías por núcleos
        if cores:
            if cores <= 2:
                base_category = 'entry_level'
            elif cores <= 4:
                base_category = 'mainstream'
            elif cores <= 8:
                base_category = 'performance'
            else:
                base_category = 'high_end'
        else:
            base_category = 'unknown'
        
        # Modificadores por TDP
        if tdp.value:
            if tdp.value <= 35:
                power_modifier = '_low_power'
            elif tdp.value <= 65:
                power_modifier = '_standard'
            elif tdp.value <= 125:
                power_modifier = '_high_performance'
            else:
                power_modifier = '_extreme'
        else:
            power_modifier = ''
        
        # Modificadores especiales
        if any(keyword in name for keyword in ['athlon', 'pentium', 'celeron']):
            return 'budget' + power_modifier
        elif any(keyword in name for keyword in ['threadripper', 'xeon', 'epyc']):
            return 'workstation' + power_modifier
        elif 'apu' in name or 'g' in name.split()[-1]:  # CPUs con gráficos integrados potentes
            return base_category + '_apu' + power_modifier
        
        return base_category + power_modifier
    
    def _parse_int_or_empty(self, value: str) -> Optional[int]:
        """Convierte string a int o None si está vacío"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None
    
    def _parse_boolean(self, value: str) -> Optional[bool]:
        """Convierte string a boolean"""
        if not value or value.strip() == '':
            return None
        value_lower = value.strip().lower()
        if value_lower in ['true', '1', 'yes', 'on']:
            return True
        elif value_lower in ['false', '0', 'no', 'off']:
            return False
        return None


@dataclass
class VideoMemory:
    """Clase para representar memoria de video con valor y unidad"""
    value: Optional[float] = None
    unit: Optional[str] = None
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, vram_str: str) -> 'VideoMemory':
        """Convierte string como '8 GB' en objeto VideoMemory"""
        if not vram_str or vram_str.strip() == '':
            return cls(raw_value=vram_str)
        
        # Patrón para extraer capacidad y unidad
        pattern = r'^(\d+(?:\.\d+)?)\s*(\w+)$'
        match = re.match(pattern, vram_str.strip())
        
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            return cls(value=value, unit=unit, raw_value=vram_str)
        else:
            return cls(raw_value=vram_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'value': self.value,
            'unit': self.unit,
            'raw_value': self.raw_value
        }
    
    def to_mb(self) -> Optional[float]:
        """Convierte a MB para comparaciones"""
        if not self.value or not self.unit:
            return None
        
        unit_lower = self.unit.lower()
        if unit_lower == 'gb':
            return self.value * 1024
        elif unit_lower == 'mb':
            return self.value
        elif unit_lower == 'tb':
            return self.value * 1024 * 1024
        
        return None


@dataclass
class DisplayConnectors:
    """Clase para representar conectores de salida de video"""
    hdmi: int = 0
    displayport: int = 0
    dvi: int = 0
    vga: int = 0
    
    @classmethod
    def from_row(cls, row: Dict[str, str]) -> 'DisplayConnectors':
        """Crea objeto desde fila de datos"""
        return cls(
            hdmi=cls._parse_int_or_zero(row.get('HDMI', '')),
            displayport=cls._parse_int_or_zero(row.get('DisplayPort', '')),
            dvi=cls._parse_int_or_zero(row.get('DVI', '')),
            vga=cls._parse_int_or_zero(row.get('VGA', ''))
        )
    
    @staticmethod
    def _parse_int_or_zero(value: str) -> int:
        """Convierte string a int o 0 si está vacío/inválido"""
        if not value or value.strip() == '':
            return 0
        try:
            return int(value.strip())
        except ValueError:
            return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'hdmi': self.hdmi,
            'displayport': self.displayport,
            'dvi': self.dvi,
            'vga': self.vga,
            'total_outputs': self.hdmi + self.displayport + self.dvi + self.vga
        }


@dataclass
class PowerConnectors:
    """Clase para representar conectores de alimentación"""
    eight_pin: int = 0
    six_pin: int = 0
    
    @classmethod
    def from_row(cls, row: Dict[str, str]) -> 'PowerConnectors':
        """Crea objeto desde fila de datos"""
        return cls(
            eight_pin=cls._parse_int_or_zero(row.get('8-Pin Connectors', '')),
            six_pin=cls._parse_int_or_zero(row.get('6-Pin Connectors', ''))
        )
    
    @staticmethod
    def _parse_int_or_zero(value: str) -> int:
        """Convierte string a int o 0 si está vacío/inválido"""
        if not value or value.strip() == '':
            return 0
        try:
            return int(value.strip())
        except ValueError:
            return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        total_pins = (self.eight_pin * 8) + (self.six_pin * 6)
        return {
            'eight_pin_connectors': self.eight_pin,
            'six_pin_connectors': self.six_pin,
            'total_connectors': self.eight_pin + self.six_pin,
            'total_pins': total_pins
        }


class GPUDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de GPUs"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de GPUData.csv"""
        normalized = {
            # Información básica (excluimos precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones físicas
            'physical': {
                'length': Dimension.from_string(row.get('Length', '')).to_dict(),
                'slots': self._parse_float_or_empty(row.get('Slots', ''))
            },
            
            # Especificaciones de rendimiento
            'performance': {
                'boost_clock': Frequency.from_string(row.get('Boost Clock', '')).to_dict(),
                'vram': VideoMemory.from_string(row.get('Vram', '')).to_dict(),
                'memory_clock': Frequency.from_string(row.get('Memory Clock', '')).to_dict(),
                'tdp': ThermalDesignPower.from_string(row.get('TDP', '')).to_dict()
            },
            
            # Conectores de alimentación
            'power': PowerConnectors.from_row(row).to_dict(),
            
            # Conectores de salida
            'display_outputs': DisplayConnectors.from_row(row).to_dict(),
            
            # Análisis calculado
            'calculated_metrics': self._calculate_metrics(row)
        }
        
        return normalized
    
    def _calculate_metrics(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Calcula métricas adicionales basadas en especificaciones"""
        metrics = {
            'performance_score': None,
            'power_efficiency': None,
            'memory_bandwidth_estimate': None,
            'gpu_category': None,
            'form_factor': None,
            'power_requirement_category': None
        }
        
        # Calcular puntuación de rendimiento estimada (boost clock × VRAM)
        boost_freq = Frequency.from_string(row.get('Boost Clock', ''))
        vram = VideoMemory.from_string(row.get('Vram', ''))
        
        if boost_freq.value and vram.value:
            boost_mhz = boost_freq.to_mhz()
            vram_mb = vram.to_mb()
            if boost_mhz and vram_mb:
                metrics['performance_score'] = (boost_mhz * vram_mb) / 1000  # Normalizado
        
        # Calcular eficiencia energética (performance score / TDP)
        tdp = ThermalDesignPower.from_string(row.get('TDP', ''))
        if metrics['performance_score'] and tdp.value and tdp.value > 0:
            metrics['power_efficiency'] = metrics['performance_score'] / tdp.value
        
        # Estimar ancho de banda de memoria (simplificado)
        memory_freq = Frequency.from_string(row.get('Memory Clock', ''))
        if memory_freq.value and vram.value:
            memory_mhz = memory_freq.to_mhz()
            if memory_mhz:
                # Estimación muy simplificada: bus típico de 256-bit para GPUs modernas
                metrics['memory_bandwidth_estimate'] = (memory_mhz * 256) / 8  # GB/s estimado
        
        # Categorizar GPU
        metrics['gpu_category'] = self._categorize_gpu(row)
        
        # Determinar factor forma
        metrics['form_factor'] = self._determine_form_factor(row)
        
        # Categorizar requerimientos de alimentación
        metrics['power_requirement_category'] = self._categorize_power_requirements(row)
        
        return metrics
    
    def _categorize_gpu(self, row: Dict[str, str]) -> str:
        """Categoriza la GPU basada en especificaciones"""
        name = row.get('Name', '').lower()
        vram = VideoMemory.from_string(row.get('Vram', ''))
        tdp = ThermalDesignPower.from_string(row.get('TDP', ''))
        
        # Detectar serie/generación por nombre
        if any(keyword in name for keyword in ['gt 1030', 'gt 730', 'rx 6400', 'rx 6500']):
            return 'entry_level'
        elif any(keyword in name for keyword in ['gtx 1650', 'gtx 1660', 'rx 6600', 'rx 7600']):
            return 'budget'
        elif any(keyword in name for keyword in ['rtx 3060', 'rtx 4060', 'rx 6700', 'rx 7700']):
            return 'mainstream'
        elif any(keyword in name for keyword in ['rtx 3070', 'rtx 4070', 'rx 6800', 'rx 7800']):
            return 'performance'
        elif any(keyword in name for keyword in ['rtx 3080', 'rtx 4080', 'rx 6900', 'rx 7900']):
            return 'high_end'
        elif any(keyword in name for keyword in ['rtx 3090', 'rtx 4090', 'titan', 'rx 7900 xtx']):
            return 'enthusiast'
        
        # Fallback por VRAM y TDP
        if vram.value and tdp.value:
            if vram.value <= 4 and tdp.value <= 100:
                return 'entry_level'
            elif vram.value <= 8 and tdp.value <= 180:
                return 'mainstream'
            elif vram.value <= 12 and tdp.value <= 250:
                return 'performance'
            else:
                return 'high_end'
        
        return 'unknown'
    
    def _determine_form_factor(self, row: Dict[str, str]) -> str:
        """Determina el factor forma basado en slots y longitud"""
        slots = self._parse_float_or_empty(row.get('Slots', ''))
        length = Dimension.from_string(row.get('Length', '')).value
        
        if slots and length:
            if slots <= 1.5 and length <= 170:
                return 'low_profile'
            elif slots <= 2.0 and length <= 200:
                return 'compact'
            elif slots <= 2.5 and length <= 280:
                return 'standard'
            elif slots <= 3.0 and length <= 320:
                return 'large'
            else:
                return 'oversized'
        
        return 'unknown'
    
    def _categorize_power_requirements(self, row: Dict[str, str]) -> str:
        """Categoriza requerimientos de alimentación"""
        power_connectors = PowerConnectors.from_row(row)
        tdp = ThermalDesignPower.from_string(row.get('TDP', ''))
        
        total_connectors = power_connectors.eight_pin + power_connectors.six_pin
        
        if total_connectors == 0:
            return 'pcie_only'  # Solo alimentación por PCIe
        elif total_connectors == 1:
            if power_connectors.six_pin > 0:
                return 'single_6pin'
            else:
                return 'single_8pin'
        elif total_connectors == 2:
            return 'dual_connector'
        elif total_connectors >= 3:
            return 'high_power'
        
        return 'unknown'
    
    def _parse_float_or_empty(self, value: str) -> Optional[float]:
        """Convierte string a float o None si está vacío"""
        if not value or value.strip() == '':
            return None
        try:
            return float(value.strip())
        except ValueError:
            return None


class MemoryCapacity:
    """Clase para manejar capacidad de memoria con unidades"""
    
    def __init__(self, value: Optional[float] = None, unit: str = 'GB'):
        self.value = value
        self.unit = unit
    
    @classmethod
    def from_string(cls, text: str) -> 'MemoryCapacity':
        """Crea MemoryCapacity desde string como '128 GB', '64GB', etc."""
        if not text or text.strip() == '':
            return cls(None, 'GB')
        
        text = text.strip()
        
        # Patrones para extraer valor y unidad
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB|TB|gb|mb|tb)', text, re.IGNORECASE)
        
        if match:
            value = float(match.group(1))
            unit = match.group(2).upper()
            return cls(value, unit)
        
        # Si solo hay número, asumir GB
        try:
            value = float(text)
            return cls(value, 'GB')
        except ValueError:
            return cls(None, 'GB')
    
    def to_gb(self) -> Optional[float]:
        """Convierte a GB"""
        if not self.value:
            return None
        
        if self.unit == 'GB':
            return self.value
        elif self.unit == 'MB':
            return self.value / 1024
        elif self.unit == 'TB':
            return self.value * 1024
        
        return self.value  # fallback
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'value': self.value,
            'unit': self.unit,
            'gb_equivalent': self.to_gb()
        }


class MotherboardConnectivity:
    """Clase para manejar conectividad de motherboard"""
    
    def __init__(self, sata: int = 0, vga: int = 0, dvi: int = 0, 
                 displayport: int = 0, hdmi: int = 0):
        self.sata_ports = sata
        self.vga_outputs = vga
        self.dvi_outputs = dvi
        self.displayport_outputs = displayport
        self.hdmi_outputs = hdmi
    
    @classmethod
    def from_row(cls, row: Dict[str, str]) -> 'MotherboardConnectivity':
        """Crea desde fila de CSV"""
        def parse_int_safe(value: str) -> int:
            try:
                return int(value.strip()) if value.strip() else 0
            except ValueError:
                return 0
        
        return cls(
            sata=parse_int_safe(row.get('SATA', '0')),
            vga=parse_int_safe(row.get('VGA', '0')),
            dvi=parse_int_safe(row.get('DVI', '0')),
            displayport=parse_int_safe(row.get('Display Port', '0')),
            hdmi=parse_int_safe(row.get('HDMI', '0'))
        )
    
    def total_video_outputs(self) -> int:
        """Calcula total de salidas de video"""
        return self.vga_outputs + self.dvi_outputs + self.displayport_outputs + self.hdmi_outputs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'sata_ports': self.sata_ports,
            'video_outputs': {
                'vga': self.vga_outputs,
                'dvi': self.dvi_outputs,
                'displayport': self.displayport_outputs,
                'hdmi': self.hdmi_outputs,
                'total': self.total_video_outputs()
            }
        }


class MotherboardDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de Motherboards"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de MotherboardData.csv"""
        normalized = {
            # Información básica (excluimos precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones de CPU y plataforma
            'platform': {
                'socket': row.get('Socket', '').strip(),
                'chipset': row.get('Chipset', '').strip(),
                'unlocked': self._parse_boolean(row.get('Unlocked', '')),
                'integrated_graphics': self._parse_boolean(row.get('Integrated Graphics', ''))
            },
            
            # Factor forma
            'form_factor': row.get('Form Factor', '').strip(),
            
            # Especificaciones de memoria
            'memory': {
                'type': row.get('Memory Type', '').strip(),
                'capacity': MemoryCapacity.from_string(row.get('Memory Capacity', '')).to_dict(),
                'slots': self._parse_int_or_empty(row.get('RAM Slots', ''))
            },
            
            # Conectividad
            'connectivity': MotherboardConnectivity.from_row(row).to_dict(),
            
            # Características inalámbricas
            'wireless': {
                'wifi': self._parse_boolean(row.get('WiFi', ''))
            },
            
            # Análisis calculado
            'calculated_metrics': self._calculate_metrics(row)
        }
        
        return normalized
    
    def _calculate_metrics(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Calcula métricas adicionales basadas en especificaciones"""
        metrics = {
            'motherboard_category': None,
            'memory_support_score': None,
            'connectivity_score': None,
            'platform_generation': None,
            'target_market': None,
            'expansion_capability': None
        }
        
        # Categorizar motherboard por chipset y socket
        metrics['motherboard_category'] = self._categorize_motherboard(row)
        
        # Calcular puntuación de soporte de memoria
        metrics['memory_support_score'] = self._calculate_memory_score(row)
        
        # Calcular puntuación de conectividad
        metrics['connectivity_score'] = self._calculate_connectivity_score(row)
        
        # Determinar generación de plataforma
        metrics['platform_generation'] = self._determine_platform_generation(row)
        
        # Determinar mercado objetivo
        metrics['target_market'] = self._determine_target_market(row)
        
        # Evaluar capacidad de expansión
        metrics['expansion_capability'] = self._evaluate_expansion_capability(row)
        
        return metrics
    
    def _categorize_motherboard(self, row: Dict[str, str]) -> str:
        """Categoriza la motherboard basada en chipset y características"""
        chipset = row.get('Chipset', '').upper()
        socket = row.get('Socket', '').upper()
        unlocked = self._parse_boolean(row.get('Unlocked', ''))
        
        # Intel categorization
        if any(socket.startswith(prefix) for prefix in ['115', '116', '117', '118', '120']):
            if chipset.startswith('Z'):
                return 'intel_enthusiast'
            elif chipset.startswith('H') and ('97' in chipset or '10' in chipset or '11' in chipset):
                return 'intel_mainstream'
            elif chipset.startswith('B'):
                return 'intel_budget'
            else:
                return 'intel_entry'
        
        # AMD categorization
        elif socket in ['AM4', 'AM5']:
            if chipset.startswith('X'):
                return 'amd_enthusiast'
            elif chipset.startswith('B') and ('550' in chipset or '650' in chipset):
                return 'amd_mainstream'
            elif chipset.startswith('A'):
                return 'amd_budget'
            else:
                return 'amd_entry'
        
        # HEDT/Workstation
        elif socket in ['TR4', 'TRX4', '2011-V3', '2066']:
            return 'workstation'
        
        # Older platforms
        elif socket in ['AM3+', 'FM2+']:
            return 'legacy'
        
        return 'unknown'
    
    def _calculate_memory_score(self, row: Dict[str, str]) -> Optional[int]:
        """Calcula puntuación de soporte de memoria"""
        memory_cap = MemoryCapacity.from_string(row.get('Memory Capacity', ''))
        ram_slots = self._parse_int_or_empty(row.get('RAM Slots', ''))
        memory_type = row.get('Memory Type', '').upper()
        
        score = 0
        
        # Puntos por capacidad máxima
        if memory_cap.value:
            if memory_cap.value >= 128:
                score += 50
            elif memory_cap.value >= 64:
                score += 30
            elif memory_cap.value >= 32:
                score += 20
            else:
                score += 10
        
        # Puntos por número de slots
        if ram_slots:
            score += ram_slots * 5
        
        # Puntos por tipo de memoria
        if 'DDR5' in memory_type:
            score += 20
        elif 'DDR4' in memory_type:
            score += 15
        elif 'DDR3' in memory_type:
            score += 5
        
        return score if score > 0 else None
    
    def _calculate_connectivity_score(self, row: Dict[str, str]) -> Optional[int]:
        """Calcula puntuación de conectividad"""
        connectivity = MotherboardConnectivity.from_row(row)
        wifi = self._parse_boolean(row.get('WiFi', ''))
        
        score = 0
        
        # Puntos por puertos SATA
        score += connectivity.sata_ports * 3
        
        # Puntos por salidas de video
        score += connectivity.total_video_outputs() * 5
        
        # Puntos por WiFi
        if wifi:
            score += 15
        
        return score if score > 0 else None
    
    def _determine_platform_generation(self, row: Dict[str, str]) -> str:
        """Determina la generación de la plataforma"""
        socket = row.get('Socket', '').upper()
        chipset = row.get('Chipset', '').upper()
        memory_type = row.get('Memory Type', '').upper()
        
        # AMD modern platforms
        if socket == 'AM5':
            return 'amd_latest'  # Ryzen 7000+
        elif socket == 'AM4':
            return 'amd_current'  # Ryzen 1000-5000
        elif socket in ['AM3+', 'FM2+']:
            return 'amd_legacy'
        
        # Intel modern platforms
        elif socket.startswith('120'):
            return 'intel_latest'  # 12th gen+
        elif socket.startswith('115'):
            if any(series in chipset for series in ['Z490', 'Z590', 'B460', 'B560']):
                return 'intel_recent'  # 10th-11th gen
            else:
                return 'intel_older'  # 6th-9th gen
        
        # HEDT
        elif socket in ['TR4', 'TRX4']:
            return 'amd_hedt'
        elif socket in ['2011-V3', '2066']:
            return 'intel_hedt'
        
        # DDR5 indicates newer platform
        if 'DDR5' in memory_type:
            return 'latest_generation'
        elif 'DDR4' in memory_type:
            return 'current_generation'
        else:
            return 'legacy_generation'
    
    def _determine_target_market(self, row: Dict[str, str]) -> str:
        """Determina el mercado objetivo"""
        form_factor = row.get('Form Factor', '').upper()
        chipset = row.get('Chipset', '').upper()
        unlocked = self._parse_boolean(row.get('Unlocked', ''))
        connectivity = MotherboardConnectivity.from_row(row)
        
        # Gaming/Enthusiast
        if unlocked and chipset.startswith('Z'):
            return 'gaming_enthusiast'
        elif unlocked and chipset.startswith('X'):
            return 'amd_enthusiast'
        
        # Workstation/Professional
        elif connectivity.sata_ports >= 8 or row.get('Socket', '') in ['TR4', 'TRX4', '2011-V3', '2066']:
            return 'workstation'
        
        # Small Form Factor
        elif 'MINI-ITX' in form_factor or 'ITX' in form_factor:
            return 'compact_build'
        
        # Budget/Office
        elif chipset.startswith('H') or chipset.startswith('A') or chipset.startswith('B'):
            if 'MICRO' in form_factor:
                return 'budget_compact'
            else:
                return 'mainstream'
        
        return 'general_purpose'
    
    def _evaluate_expansion_capability(self, row: Dict[str, str]) -> str:
        """Evalúa la capacidad de expansión"""
        form_factor = row.get('Form Factor', '').upper()
        ram_slots = self._parse_int_or_empty(row.get('RAM Slots', ''))
        connectivity = MotherboardConnectivity.from_row(row)
        
        score = 0
        
        # Factor forma (más grande = más expansión)
        if 'ATX' in form_factor and 'MICRO' not in form_factor and 'MINI' not in form_factor:
            score += 30  # Full ATX
        elif 'MICRO-ATX' in form_factor:
            score += 20  # Micro ATX
        elif 'MINI-ITX' in form_factor or 'ITX' in form_factor:
            score += 10  # Mini ITX
        
        # Slots de RAM
        if ram_slots:
            score += ram_slots * 5
        
        # Conectividad
        score += connectivity.sata_ports * 2
        
        if score >= 50:
            return 'high_expansion'
        elif score >= 30:
            return 'moderate_expansion'
        elif score >= 15:
            return 'limited_expansion'
        else:
            return 'minimal_expansion'
    
    def _parse_boolean(self, value: str) -> bool:
        """Convierte string a booleano"""
        if not value:
            return False
        value_lower = value.strip().lower()
        return value_lower in ['true', '1', 'yes', 'on']
    
    def _parse_int_or_empty(self, value: str) -> Optional[int]:
        """Convierte string a int o None si está vacío"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None


class PowerWattage:
    """Clase para manejar potencia con unidades"""
    
    def __init__(self, value: Optional[float] = None, unit: str = 'W'):
        self.value = value
        self.unit = unit
    
    @classmethod
    def from_string(cls, text: str) -> 'PowerWattage':
        """Crea PowerWattage desde string como '650 W', '750W', etc."""
        if not text or text.strip() == '':
            return cls(None, 'W')
        
        text = text.strip()
        
        # Patrones para extraer valor y unidad
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*(W|WATT|WATTS|w|watt|watts)', text, re.IGNORECASE)
        
        if match:
            value = float(match.group(1))
            unit = 'W'  # Normalizar a W
            return cls(value, unit)
        
        # Si solo hay número, asumir W
        try:
            value = float(text)
            return cls(value, 'W')
        except ValueError:
            return cls(None, 'W')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'value': self.value,
            'unit': self.unit
        }


class EfficiencyRating:
    """Clase para manejar certificaciones de eficiencia"""
    
    def __init__(self, rating: str = '', level: str = ''):
        self.rating = rating.strip()
        self.level = level.strip()
    
    @classmethod
    def from_string(cls, text: str) -> 'EfficiencyRating':
        """Crea EfficiencyRating desde string como '80 PLUS Gold', '80 Plus Platinum', etc."""
        if not text or text.strip() == '':
            return cls('', '')
        
        text = text.strip().upper()
        
        # Extraer nivel de certificación
        if '80 PLUS' in text or '80PLUS' in text:
            rating = '80 PLUS'
            
            # Determinar nivel
            if 'TITANIUM' in text:
                level = 'Titanium'
            elif 'PLATINUM' in text:
                level = 'Platinum'
            elif 'GOLD' in text:
                level = 'Gold'
            elif 'SILVER' in text:
                level = 'Silver'
            elif 'BRONZE' in text:
                level = 'Bronze'
            elif 'WHITE' in text:
                level = 'White'
            else:
                level = 'Standard'
            
            return cls(rating, level)
        else:
            # Otros estándares de eficiencia
            return cls(text, '')
    
    def get_efficiency_score(self) -> int:
        """Obtiene puntuación numérica de eficiencia (mayor es mejor)"""
        if self.rating == '80 PLUS':
            efficiency_scores = {
                'Titanium': 100,
                'Platinum': 90,
                'Gold': 80,
                'Silver': 70,
                'Bronze': 60,
                'White': 50,
                'Standard': 40
            }
            return efficiency_scores.get(self.level, 0)
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'rating': self.rating,
            'level': self.level,
            'full_rating': f"{self.rating} {self.level}".strip(),
            'efficiency_score': self.get_efficiency_score()
        }


class PSUDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de PSUs (Fuentes de Alimentación)"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de PSUData.csv"""
        normalized = {
            # Información básica (excluimos precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones de potencia
            'power': {
                'wattage': PowerWattage.from_string(row.get('Watt', '')).to_dict(),
                'efficiency': EfficiencyRating.from_string(row.get('Efficiency Rating', '')).to_dict()
            },
            
            # Factor forma
            'form_factor': row.get('Size', '').strip(),
            
            # Análisis calculado
            'calculated_metrics': self._calculate_metrics(row)
        }
        
        return normalized
    
    def _calculate_metrics(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Calcula métricas adicionales basadas en especificaciones"""
        metrics = {
            'psu_category': None,
            'power_efficiency_score': None,
            'form_factor_category': None,
            'target_market': None,
            'power_per_efficiency_ratio': None,
            'recommended_system_wattage': None
        }
        
        # Categorizar PSU por potencia
        metrics['psu_category'] = self._categorize_psu_by_power(row)
        
        # Calcular puntuación de eficiencia energética
        metrics['power_efficiency_score'] = self._calculate_power_efficiency_score(row)
        
        # Categorizar factor forma
        metrics['form_factor_category'] = self._categorize_form_factor(row)
        
        # Determinar mercado objetivo
        metrics['target_market'] = self._determine_target_market(row)
        
        # Calcular ratio potencia/eficiencia
        metrics['power_per_efficiency_ratio'] = self._calculate_power_efficiency_ratio(row)
        
        # Calcular potencia recomendada del sistema
        metrics['recommended_system_wattage'] = self._calculate_recommended_system_wattage(row)
        
        return metrics
    
    def _categorize_psu_by_power(self, row: Dict[str, str]) -> str:
        """Categoriza la PSU basada en potencia"""
        wattage = PowerWattage.from_string(row.get('Watt', ''))
        
        if not wattage.value:
            return 'unknown'
        
        power = wattage.value
        
        if power <= 400:
            return 'low_power'       # Sistemas básicos, office
        elif power <= 650:
            return 'mainstream'      # Gaming mainstream, workstations básicas
        elif power <= 850:
            return 'high_performance' # Gaming alto rendimiento
        elif power <= 1200:
            return 'enthusiast'      # Multi-GPU, workstations
        else:
            return 'extreme'         # Servidores, sistemas extremos
    
    def _calculate_power_efficiency_score(self, row: Dict[str, str]) -> Optional[int]:
        """Calcula puntuación combinada de potencia y eficiencia"""
        wattage = PowerWattage.from_string(row.get('Watt', ''))
        efficiency = EfficiencyRating.from_string(row.get('Efficiency Rating', ''))
        
        if not wattage.value:
            return None
        
        # Puntuación base por potencia (escalada)
        power_score = min(wattage.value / 10, 100)  # Máximo 100 puntos
        
        # Puntuación por eficiencia
        efficiency_score = efficiency.get_efficiency_score()
        
        # Combinar ambas puntuaciones
        total_score = int((power_score * 0.6) + (efficiency_score * 0.4))
        
        return total_score
    
    def _categorize_form_factor(self, row: Dict[str, str]) -> str:
        """Categoriza el factor forma"""
        form_factor = row.get('Size', '').upper().strip()
        
        if 'ATX' in form_factor and 'MICRO' not in form_factor and 'MINI' not in form_factor:
            return 'standard_atx'
        elif 'MICRO-ATX' in form_factor or 'MATX' in form_factor:
            return 'micro_atx'
        elif 'SFX' in form_factor:
            if 'SFX-L' in form_factor:
                return 'sfx_l'
            else:
                return 'sfx'
        elif 'TFX' in form_factor:
            return 'tfx'
        elif 'FLEX' in form_factor:
            return 'flex_atx'
        else:
            return 'other'
    
    def _determine_target_market(self, row: Dict[str, str]) -> str:
        """Determina el mercado objetivo"""
        wattage = PowerWattage.from_string(row.get('Watt', ''))
        efficiency = EfficiencyRating.from_string(row.get('Efficiency Rating', ''))
        form_factor = row.get('Size', '').upper()
        name = row.get('Name', '').lower()
        
        if not wattage.value:
            return 'unknown'
        
        power = wattage.value
        efficiency_level = efficiency.level.upper()
        
        # Gaming/Enthusiast
        if power >= 750 and efficiency_level in ['GOLD', 'PLATINUM', 'TITANIUM']:
            if power >= 1000:
                return 'enthusiast_gaming'
            else:
                return 'high_end_gaming'
        
        # Compact/SFF
        elif 'SFX' in form_factor or 'TFX' in form_factor:
            return 'small_form_factor'
        
        # Budget gaming
        elif 500 <= power <= 700 and efficiency_level in ['BRONZE', 'GOLD']:
            return 'budget_gaming'
        
        # Office/Basic
        elif power <= 500:
            return 'office_basic'
        
        # Workstation
        elif power >= 650 and efficiency_level in ['PLATINUM', 'TITANIUM']:
            if 'modular' in name:
                return 'workstation_professional'
            else:
                return 'workstation'
        
        return 'general_purpose'
    
    def _calculate_power_efficiency_ratio(self, row: Dict[str, str]) -> Optional[float]:
        """Calcula ratio de potencia por eficiencia"""
        wattage = PowerWattage.from_string(row.get('Watt', ''))
        efficiency = EfficiencyRating.from_string(row.get('Efficiency Rating', ''))
        
        if not wattage.value or efficiency.get_efficiency_score() == 0:
            return None
        
        # Ratio: Watts por punto de eficiencia
        ratio = wattage.value / efficiency.get_efficiency_score()
        return round(ratio, 2)
    
    def _calculate_recommended_system_wattage(self, row: Dict[str, str]) -> Optional[int]:
        """Calcula potencia recomendada del sistema (regla 80%)"""
        wattage = PowerWattage.from_string(row.get('Watt', ''))
        
        if not wattage.value:
            return None
        
        # Regla general: usar máximo 80% de la capacidad de la PSU
        recommended = int(wattage.value * 0.8)
        return recommended


class StorageCapacity:
    """Clase para manejar capacidad de almacenamiento con unidades"""
    
    def __init__(self, value: Optional[float] = None, unit: str = 'GB'):
        self.value = value
        self.unit = unit
    
    @classmethod
    def from_string(cls, text: str) -> 'StorageCapacity':
        """Crea StorageCapacity desde string como '1000 GB', '2 TB', '512GB', etc."""
        if not text or text.strip() == '':
            return cls(None, 'GB')
        
        text = text.strip()
        
        # Patrones para extraer valor y unidad
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*(TB|GB|MB|tb|gb|mb)', text, re.IGNORECASE)
        
        if match:
            value = float(match.group(1))
            unit = match.group(2).upper()
            return cls(value, unit)
        
        # Si solo hay número, asumir GB
        try:
            value = float(text)
            return cls(value, 'GB')
        except ValueError:
            return cls(None, 'GB')
    
    def to_gb(self) -> Optional[float]:
        """Convierte a GB para comparaciones"""
        if not self.value:
            return None
        
        if self.unit == 'GB':
            return self.value
        elif self.unit == 'TB':
            return self.value * 1024
        elif self.unit == 'MB':
            return self.value / 1024
        
        return self.value  # fallback
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'value': self.value,
            'unit': self.unit,
            'gb_equivalent': self.to_gb()
        }


class SSDDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de SSDs"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de SSDData.csv"""
        normalized = {
            # Información básica (excluimos precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones de almacenamiento
            'storage_specs': {
                'capacity': StorageCapacity.from_string(row.get('Size', '')).to_dict(),
                'form_factor': row.get('Form Factor', '').strip(),
                'protocol': row.get('Protocol', '').strip()
            },
            
            # Especificaciones técnicas
            'technical_specs': {
                'nand_type': row.get('NAND', '').strip(),
                'controller': row.get('Controller', '').strip()
            },
            
            # Análisis calculado
            'calculated_metrics': self._calculate_metrics(row)
        }
        
        return normalized
    
    def _calculate_metrics(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Calcula métricas adicionales basadas en especificaciones"""
        metrics = {
            'ssd_category': None,
            'performance_tier': None,
            'target_market': None,
            'endurance_category': None,
            'form_factor_category': None,
            'capacity_category': None
        }
        
        # Categorizar SSD
        metrics['ssd_category'] = self._categorize_ssd(row)
        
        # Determinar tier de rendimiento
        metrics['performance_tier'] = self._determine_performance_tier(row)
        
        # Determinar mercado objetivo
        metrics['target_market'] = self._determine_target_market(row)
        
        # Categorizar durabilidad estimada
        metrics['endurance_category'] = self._categorize_endurance(row)
        
        # Categorizar factor forma
        metrics['form_factor_category'] = self._categorize_form_factor(row)
        
        # Categorizar capacidad
        metrics['capacity_category'] = self._categorize_capacity(row)
        
        return metrics
    
    def _categorize_ssd(self, row: Dict[str, str]) -> str:
        """Categoriza el SSD basado en especificaciones"""
        protocol = row.get('Protocol', '').upper()
        form_factor = row.get('Form Factor', '').upper()
        nand = row.get('NAND', '').upper()
        
        if protocol == 'NVM' or 'NVME' in protocol:
            if 'TLC' in nand:
                return 'nvme_mainstream'
            elif 'QLC' in nand:
                return 'nvme_budget'
            elif 'MLC' in nand or 'SLC' in nand:
                return 'nvme_high_performance'
            else:
                return 'nvme_standard'
        elif protocol == 'SATA':
            return 'sata_standard'
        else:
            return 'unknown'
    
    def _determine_performance_tier(self, row: Dict[str, str]) -> str:
        """Determina el tier de rendimiento"""
        protocol = row.get('Protocol', '').upper()
        nand = row.get('NAND', '').upper()
        controller = row.get('Controller', '').lower()
        
        # NVMe tiers
        if protocol == 'NVM' or 'NVME' in protocol:
            if 'phison ps5016' in controller or 'sm2262' in controller:
                return 'high_performance'
            elif 'ps5013' in controller or 'ps5012' in controller:
                return 'mainstream'
            elif 'MLC' in nand or 'SLC' in nand:
                return 'premium'
            elif 'QLC' in nand:
                return 'budget'
            else:
                return 'standard'
        
        # SATA
        elif protocol == 'SATA':
            return 'sata_standard'
        
        return 'unknown'
    
    def _determine_target_market(self, row: Dict[str, str]) -> str:
        """Determina el mercado objetivo"""
        capacity = StorageCapacity.from_string(row.get('Size', ''))
        protocol = row.get('Protocol', '').upper()
        nand = row.get('NAND', '').upper()
        form_factor = row.get('Form Factor', '').upper()
        
        # Gaming/Enthusiast
        if (protocol == 'NVM' and capacity.value and capacity.value >= 1000 and 
            'TLC' in nand):
            return 'gaming_enthusiast'
        
        # Professional/Workstation
        elif (capacity.value and capacity.value >= 2000 and 
              ('MLC' in nand or 'SLC' in nand)):
            return 'professional'
        
        # Budget gaming
        elif (protocol == 'NVM' and capacity.value and 
              240 <= capacity.value <= 1000):
            return 'budget_gaming'
        
        # Budget storage
        elif 'QLC' in nand or protocol == 'SATA':
            return 'budget_storage'
        
        # Mainstream
        else:
            return 'mainstream'
    
    def _categorize_endurance(self, row: Dict[str, str]) -> str:
        """Categoriza durabilidad estimada por tipo NAND"""
        nand = row.get('NAND', '').upper()
        
        if 'SLC' in nand:
            return 'enterprise_grade'
        elif 'MLC' in nand:
            return 'high_endurance'
        elif 'TLC' in nand:
            return 'standard_endurance'
        elif 'QLC' in nand:
            return 'budget_endurance'
        else:
            return 'unknown'
    
    def _categorize_form_factor(self, row: Dict[str, str]) -> str:
        """Categoriza el factor forma"""
        form_factor = row.get('Form Factor', '').upper()
        
        if 'M.2' in form_factor:
            return 'compact_modern'
        elif 'SATA' in form_factor or '2.5' in form_factor:
            return 'standard_drive'
        elif 'PCIe' in form_factor:
            return 'expansion_card'
        else:
            return 'other'
    
    def _categorize_capacity(self, row: Dict[str, str]) -> str:
        """Categoriza por capacidad"""
        capacity = StorageCapacity.from_string(row.get('Size', ''))
        
        if not capacity.value:
            return 'unknown'
        
        gb_capacity = capacity.to_gb()
        if not gb_capacity:
            return 'unknown'
        
        if gb_capacity <= 256:
            return 'small_capacity'
        elif gb_capacity <= 1024:
            return 'medium_capacity'
        elif gb_capacity <= 2048:
            return 'large_capacity'
        else:
            return 'extra_large_capacity'


class HDDDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de HDDs"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de HDDData.csv"""
        normalized = {
            # Información básica (excluimos precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones de almacenamiento
            'storage_specs': {
                'capacity': StorageCapacity.from_string(row.get('Size', '')).to_dict(),
                'form_factor': row.get('Form Factor', '').strip()
            },
            
            # Especificaciones de rendimiento
            'performance_specs': {
                'rpm': self._parse_int_or_empty(row.get('RPM', '')),
                'cache': self._parse_cache(row.get('Cache', ''))
            },
            
            # Análisis calculado
            'calculated_metrics': self._calculate_metrics(row)
        }
        
        return normalized
    
    def _parse_cache(self, cache_str: str) -> Dict[str, Any]:
        """Parsea la información de caché"""
        if not cache_str or cache_str.strip() == '':
            return {'value': None, 'unit': 'MB'}
        
        cache_str = cache_str.strip()
        
        # Extraer número (asumir MB si no hay unidad)
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|GB|mb|gb)?', cache_str)
        
        if match:
            value = float(match.group(1))
            unit = match.group(2).upper() if match.group(2) else 'MB'
            return {'value': value, 'unit': unit}
        
        try:
            value = float(cache_str)
            return {'value': value, 'unit': 'MB'}
        except ValueError:
            return {'value': None, 'unit': 'MB'}
    
    def _calculate_metrics(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Calcula métricas adicionales basadas en especificaciones"""
        metrics = {
            'hdd_category': None,
            'performance_class': None,
            'target_market': None,
            'capacity_per_rpm_ratio': None,
            'storage_density': None,
            'reliability_class': None
        }
        
        # Categorizar HDD
        metrics['hdd_category'] = self._categorize_hdd(row)
        
        # Determinar clase de rendimiento
        metrics['performance_class'] = self._determine_performance_class(row)
        
        # Determinar mercado objetivo
        metrics['target_market'] = self._determine_target_market(row)
        
        # Calcular ratio capacidad/RPM
        metrics['capacity_per_rpm_ratio'] = self._calculate_capacity_rpm_ratio(row)
        
        # Categorizar densidad de almacenamiento
        metrics['storage_density'] = self._categorize_storage_density(row)
        
        # Determinar clase de confiabilidad
        metrics['reliability_class'] = self._determine_reliability_class(row)
        
        return metrics
    
    def _categorize_hdd(self, row: Dict[str, str]) -> str:
        """Categoriza el HDD basado en especificaciones"""
        rpm = self._parse_int_or_empty(row.get('RPM', ''))
        capacity = StorageCapacity.from_string(row.get('Size', ''))
        name = row.get('Name', '').lower()
        
        # Por RPM y uso
        if 'nas' in name or 'enterprise' in name:
            return 'nas_enterprise'
        elif 'archive' in name:
            return 'archive_storage'
        elif rpm and rpm >= 7200:
            return 'performance_desktop'
        elif rpm and rpm <= 5400:
            return 'green_storage'
        elif 'travelstar' in name or '2.5' in name:
            return 'mobile_laptop'
        else:
            return 'standard_desktop'
    
    def _determine_performance_class(self, row: Dict[str, str]) -> str:
        """Determina la clase de rendimiento"""
        rpm = self._parse_int_or_empty(row.get('RPM', ''))
        cache = self._parse_cache(row.get('Cache', ''))
        
        if not rpm:
            return 'unknown'
        
        # Clasificar por RPM
        if rpm >= 10000:
            return 'enterprise_high_speed'
        elif rpm >= 7200:
            if cache.get('value') and cache.get('value') >= 64:
                return 'high_performance'
            else:
                return 'standard_performance'
        elif rpm >= 5900:
            return 'balanced_performance'
        elif rpm <= 5400:
            return 'power_efficient'
        else:
            return 'standard'
    
    def _determine_target_market(self, row: Dict[str, str]) -> str:
        """Determina el mercado objetivo"""
        name = row.get('Name', '').lower()
        capacity = StorageCapacity.from_string(row.get('Size', ''))
        rpm = self._parse_int_or_empty(row.get('RPM', ''))
        
        # Enterprise/NAS
        if any(keyword in name for keyword in ['nas', 'enterprise', 'ultrastar', 'deskstar']):
            return 'enterprise_nas'
        
        # Archive/Cold storage
        elif 'archive' in name or (rpm and rpm <= 5900):
            return 'archive_backup'
        
        # Mobile/Laptop
        elif 'travelstar' in name or any(keyword in name for keyword in ['mobile', 'laptop']):
            return 'mobile_laptop'
        
        # Gaming/Performance
        elif rpm and rpm >= 7200 and capacity.value and capacity.value <= 2048:
            return 'gaming_performance'
        
        # Bulk storage
        elif capacity.value and capacity.value >= 4096:
            return 'bulk_storage'
        
        # General desktop
        else:
            return 'desktop_general'
    
    def _calculate_capacity_rpm_ratio(self, row: Dict[str, str]) -> Optional[float]:
        """Calcula ratio de capacidad por RPM"""
        capacity = StorageCapacity.from_string(row.get('Size', ''))
        rpm = self._parse_int_or_empty(row.get('RPM', ''))
        
        if capacity.value and rpm and rpm > 0:
            gb_capacity = capacity.to_gb()
            if gb_capacity:
                return round(gb_capacity / rpm, 4)
        
        return None
    
    def _categorize_storage_density(self, row: Dict[str, str]) -> str:
        """Categoriza densidad de almacenamiento"""
        capacity = StorageCapacity.from_string(row.get('Size', ''))
        
        if not capacity.value:
            return 'unknown'
        
        gb_capacity = capacity.to_gb()
        if not gb_capacity:
            return 'unknown'
        
        if gb_capacity <= 1024:
            return 'low_density'
        elif gb_capacity <= 4096:
            return 'medium_density'
        elif gb_capacity <= 8192:
            return 'high_density'
        else:
            return 'ultra_high_density'
    
    def _determine_reliability_class(self, row: Dict[str, str]) -> str:
        """Determina clase de confiabilidad estimada"""
        name = row.get('Name', '').lower()
        producer = row.get('Producer', '').lower()
        
        # Enterprise grade
        if any(keyword in name for keyword in ['enterprise', 'ultrastar', 'nas']):
            return 'enterprise_grade'
        
        # Consumer reliable
        elif any(brand in producer for brand in ['western digital', 'seagate', 'hgst']):
            if 'archive' in name:
                return 'archive_optimized'
            else:
                return 'consumer_reliable'
        
        # Standard
        else:
            return 'standard_consumer'
    
    def _parse_int_or_empty(self, value: str) -> Optional[int]:
        """Convierte string a int o None si está vacío"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None


@dataclass
class RAMType:
    """Clase para representar el tipo de RAM (DDR4, DDR5, etc.)"""
    generation: str = ''
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, ram_type_str: str) -> 'RAMType':
        """Convierte string como 'DDR4' o 'DDR5' en objeto RAMType"""
        if not ram_type_str or ram_type_str.strip() == '':
            return cls(raw_value=ram_type_str)
        
        ram_type_str = ram_type_str.strip().upper()
        
        if 'DDR5' in ram_type_str:
            return cls(generation='DDR5', raw_value=ram_type_str)
        elif 'DDR4' in ram_type_str:
            return cls(generation='DDR4', raw_value=ram_type_str)
        elif 'DDR3' in ram_type_str:
            return cls(generation='DDR3', raw_value=ram_type_str)
        else:
            return cls(raw_value=ram_type_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'generation': self.generation,
            'raw_value': self.raw_value
        }
    
    def get_generation_score(self) -> int:
        """Obtiene puntuación por generación de RAM"""
        if self.generation == 'DDR5':
            return 50
        elif self.generation == 'DDR4':
            return 30
        elif self.generation == 'DDR3':
            return 10
        else:
            return 0


@dataclass
class RAMTimings:
    """Clase para representar los timings de la RAM (ej. 16-18-18)"""
    primary: List[int] = field(default_factory=list)
    secondary: List[int] = field(default_factory=list)
    raw_value: Optional[str] = None
    
    @classmethod
    def from_string(cls, timings_str: str) -> 'RAMTimings':
        """Convierte string como '16-18-18' en objeto RAMTimings"""
        if not timings_str or timings_str.strip() == '':
            return cls(raw_value=timings_str)
        
        timings_str = timings_str.strip()
        
        # Suponemos formato común: tCL-tRCD-tRP
        primary_timings = []
        secondary_timings = []
        
        # Separar por comas en caso de múltiples entradas (ej. "16-18-18, 40-42-42")
        for timing_set in timings_str.split(','):
            timing_set = timing_set.strip()
            if timing_set:
                # Separar por guiones
                timings_parts = timing_set.split('-')
                
                # Convertir a enteros y clasificar en primarios/secundarios
                if len(timings_parts) >= 3:
                    primary_timings = [int(x) for x in timings_parts[:3] if x.isdigit()]
                    if len(timings_parts) > 3:
                        secondary_timings = [int(x) for x in timings_parts[3:] if x.isdigit()]
        
        return cls(primary=primary_timings, secondary=secondary_timings, raw_value=timings_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        return {
            'primary': self.primary,
            'secondary': self.secondary,
            'raw_value': self.raw_value
        }
    
    def calculate_latency_score(self, frequency_mhz: Optional[float]) -> Optional[float]:
        """Calcula la puntuación de latencia real basada en los timings y frecuencia"""
        if not frequency_mhz or frequency_mhz <= 0:
            return None
        
        # Latencia CAS (tCL) en nanosegundos
        cas_latency_ns = (self.primary[0] / frequency_mhz) * 2000 if len(self.primary) > 0 else 0
        
        # Puntuación inversamente proporcional a la latencia CAS
        return max(0, 100 - cas_latency_ns)
    

class RAMDataNormalizer(BaseNormalizer):
    """Normalizador específico para datos de RAM"""
    
    def normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normaliza una fila de RAMData.csv"""
        normalized = {
            # Información básica (excluimos precio y product page)
            'name': row.get('Name', '').strip(),
            'producer': row.get('Producer', '').strip(),
            'mpn': row.get('MPN', '').strip(),
            'ean': row.get('EAN', '').strip(),
            'upc': row.get('UPC', '').strip(),
            
            # Especificaciones de memoria
            'memory_specs': {
                'ram_type': RAMType.from_string(row.get('Ram Type', '')).to_dict(),
                'capacity': MemoryCapacity.from_string(row.get('Size', '')).to_dict(),
                'frequency': Frequency.from_string(row.get('Clock', '') + ' MHz').to_dict(),
                'timings': RAMTimings.from_string(row.get('Timings', '')).to_dict(),
                'sticks': self._parse_int_or_empty(row.get('Sticks', ''))
            },
            
            # Análisis calculado
            'calculated_metrics': self._calculate_metrics(row)
        }
        
        return normalized
    
    def _calculate_metrics(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Calcula métricas adicionales basadas en especificaciones"""
        metrics = {
            'ram_category': None,
            'performance_score': None,
            'capacity_per_stick': None,
            'speed_category': None,
            'target_market': None,
            'price_performance_category': None,
            'latency_score': None
        }
        
        # Categorizar RAM
        metrics['ram_category'] = self._categorize_ram(row)
        
        # Calcular puntuación de rendimiento
        metrics['performance_score'] = self._calculate_performance_score(row)
        
        # Calcular capacidad por stick
        metrics['capacity_per_stick'] = self._calculate_capacity_per_stick(row)
        
        # Categorizar por velocidad
        metrics['speed_category'] = self._categorize_speed(row)
        
        # Determinar mercado objetivo
        metrics['target_market'] = self._determine_target_market(row)
        
        # Categorizar precio/rendimiento
        metrics['price_performance_category'] = self._categorize_price_performance(row)
        
        # Calcular puntuación de latencia
        metrics['latency_score'] = self._calculate_latency_score(row)
        
        return metrics
    
    def _categorize_ram(self, row: Dict[str, str]) -> str:
        """Categoriza la RAM basada en generación y especificaciones"""
        ram_type = RAMType.from_string(row.get('Ram Type', ''))
        capacity = MemoryCapacity.from_string(row.get('Size', ''))
        frequency = self._parse_int_or_empty(row.get('Clock', ''))
        
        # Por generación
        if ram_type.generation == 'DDR5':
            if frequency and frequency >= 5600:
                return 'ddr5_high_speed'
            elif frequency and frequency >= 5000:
                return 'ddr5_standard'
            else:
                return 'ddr5_entry'
        elif ram_type.generation == 'DDR4':
            if frequency and frequency >= 3600:
                return 'ddr4_high_speed'
            elif frequency and frequency >= 3200:
                return 'ddr4_standard'
            else:
                return 'ddr4_entry'
        elif ram_type.generation == 'DDR3':
            return 'ddr3_legacy'
        
        return 'unknown'
    
    def _calculate_performance_score(self, row: Dict[str, str]) -> Optional[int]:
        """Calcula puntuación de rendimiento combinada"""
        ram_type = RAMType.from_string(row.get('Ram Type', ''))
        capacity = MemoryCapacity.from_string(row.get('Size', ''))
        frequency = self._parse_int_or_empty(row.get('Clock', ''))
        
        if not frequency or not capacity.value:
            return None
        
        score = 0
        
        # Puntos por generación
        score += ram_type.get_generation_score()
        
        # Puntos por frecuencia (normalizado)
        score += min(frequency / 100, 50)  # Máximo 50 puntos
        
        # Puntos por capacidad
        if capacity.value >= 32:
            score += 30
        elif capacity.value >= 16:
            score += 20
        elif capacity.value >= 8:
            score += 10
        
        return int(score)
    
    def _calculate_capacity_per_stick(self, row: Dict[str, str]) -> Optional[float]:
        """Calcula capacidad por stick individual"""
        capacity = MemoryCapacity.from_string(row.get('Size', ''))
        sticks = self._parse_int_or_empty(row.get('Sticks', ''))
        
        if capacity.value and sticks and sticks > 0:
            return round(capacity.value / sticks, 2)
        
        return None
    
    def _categorize_speed(self, row: Dict[str, str]) -> str:
        """Categoriza por velocidad"""
        frequency = self._parse_int_or_empty(row.get('Clock', ''))
        ram_type = RAMType.from_string(row.get('Ram Type', ''))
        
        if not frequency:
            return 'unknown'
        
        if ram_type.generation == 'DDR5':
            if frequency >= 6000:
                return 'extreme_speed'
            elif frequency >= 5600:
                return 'high_speed'
            elif frequency >= 5000:
                return 'standard_speed'
            else:
                return 'entry_speed'
        elif ram_type.generation == 'DDR4':
            if frequency >= 4000:
                return 'extreme_speed'
            elif frequency >= 3600:
                return 'high_speed'
            elif frequency >= 3200:
                return 'standard_speed'
            else:
                return 'entry_speed'
        else:
            return 'legacy_speed'
    
    def _determine_target_market(self, row: Dict[str, str]) -> str:
        """Determina el mercado objetivo"""
        ram_type = RAMType.from_string(row.get('Ram Type', ''))
        capacity = MemoryCapacity.from_string(row.get('Size', ''))
        frequency = self._parse_int_or_empty(row.get('Clock', ''))
        sticks = self._parse_int_or_empty(row.get('Sticks', ''))
        
        # Gaming enthusiast
        if (ram_type.generation in ['DDR4', 'DDR5'] and 
            frequency and frequency >= 3600 and 
            capacity.value and capacity.value >= 16):
            return 'gaming_enthusiast'
        
        # Workstation/Content Creation
        elif capacity.value and capacity.value >= 32:
            return 'workstation'
        
        # Budget gaming
        elif (ram_type.generation == 'DDR4' and 
              frequency and 3000 <= frequency < 3600 and
              capacity.value and capacity.value >= 16):
            return 'budget_gaming'
        
        # Office/Basic
        elif capacity.value and capacity.value <= 8:
            return 'office_basic'
        
        # Mainstream
        else:
            return 'mainstream'
    
    def _categorize_price_performance(self, row: Dict[str, str]) -> str:
        """Categoriza relación precio/rendimiento estimada"""
        ram_type = RAMType.from_string(row.get('Ram Type', ''))
        frequency = self._parse_int_or_empty(row.get('Clock', ''))
        capacity = MemoryCapacity.from_string(row.get('Size', ''))
        
        # Estimación básica basada en especificaciones
        if ram_type.generation == 'DDR5':
            if frequency and frequency >= 5600:
                return 'premium'
            else:
                return 'high_value'
        elif ram_type.generation == 'DDR4':
            if frequency and frequency >= 3600:
                return 'performance'
            else:
                return 'budget_friendly'
        else:
            return 'economy'
    
    def _calculate_latency_score(self, row: Dict[str, str]) -> Optional[float]:
        """Calcula puntuación de latencia real"""
        timings = RAMTimings.from_string(row.get('Timings', ''))
        frequency = self._parse_int_or_empty(row.get('Clock', ''))
        
        return timings.calculate_latency_score(frequency)
    
    def _parse_int_or_empty(self, value: str) -> Optional[int]:
        """Convierte string a int o None si está vacío"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None