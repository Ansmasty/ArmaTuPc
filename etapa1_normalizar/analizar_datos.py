#!/usr/bin/env python3
"""
Analizador de Datos Normalizados
================================

Script para analizar los datos normalizados y demostrar las ventajas
de tener los valores separados de sus unidades de medida.
"""

import json
import statistics
from pathlib import Path
from collections import Counter


def load_normalized_data(file_path: str) -> list:
    """Carga los datos normalizados desde JSON"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def analyze_dimensions(data: list) -> dict:
    """Analiza las dimensiones de los gabinetes"""
    widths = []
    depths = []
    heights = []
    volumes = []
    
    for case in data:
        dims = case['dimensions']
        
        # Extraer valores numéricos si están disponibles
        if dims['width']['value'] is not None:
            widths.append(dims['width']['value'])
        if dims['depth']['value'] is not None:
            depths.append(dims['depth']['value'])
        if dims['height']['value'] is not None:
            heights.append(dims['height']['value'])
        
        # Calcular volumen si todas las dimensiones están disponibles
        if (dims['width']['value'] and dims['depth']['value'] and dims['height']['value']):
            volume = dims['width']['value'] * dims['depth']['value'] * dims['height']['value']
            volumes.append(volume / 1000000)  # Convertir a litros (mm³ a dm³)
    
    return {
        'width_stats': {
            'min': min(widths) if widths else None,
            'max': max(widths) if widths else None,
            'mean': statistics.mean(widths) if widths else None,
            'median': statistics.median(widths) if widths else None
        },
        'depth_stats': {
            'min': min(depths) if depths else None,
            'max': max(depths) if depths else None,
            'mean': statistics.mean(depths) if depths else None,
            'median': statistics.median(depths) if depths else None
        },
        'height_stats': {
            'min': min(heights) if heights else None,
            'max': max(heights) if heights else None,
            'mean': statistics.mean(heights) if heights else None,
            'median': statistics.median(heights) if heights else None
        },
        'volume_stats': {
            'min': min(volumes) if volumes else None,
            'max': max(volumes) if volumes else None,
            'mean': statistics.mean(volumes) if volumes else None,
            'median': statistics.median(volumes) if volumes else None,
            'count': len(volumes)
        }
    }


def analyze_fan_support(data: list) -> dict:
    """Analiza el soporte de ventiladores"""
    fan_sizes = ['80mm', '120mm', '140mm', '200mm']
    fan_analysis = {}
    
    for size in fan_sizes:
        max_fans = []
        installed_fans = []
        
        for case in data:
            fan_data = case['fan_support'][size]
            if fan_data['maximum'] is not None:
                max_fans.append(fan_data['maximum'])
            if fan_data['installed'] is not None:
                installed_fans.append(fan_data['installed'])
        
        fan_analysis[size] = {
            'max_slots_stats': {
                'min': min(max_fans) if max_fans else None,
                'max': max(max_fans) if max_fans else None,
                'mean': statistics.mean(max_fans) if max_fans else None,
                'common_values': Counter(max_fans).most_common(5) if max_fans else []
            },
            'pre_installed_stats': {
                'min': min(installed_fans) if installed_fans else None,
                'max': max(installed_fans) if installed_fans else None,
                'mean': statistics.mean(installed_fans) if installed_fans else None,
                'common_values': Counter(installed_fans).most_common(5) if installed_fans else []
            }
        }
    
    return fan_analysis


def analyze_compatibility(data: list) -> dict:
    """Analiza la compatibilidad de motherboards y otros componentes"""
    motherboard_support = Counter()
    psu_support = Counter()
    gpu_lengths = []
    cpu_cooler_heights = []
    
    for case in data:
        # Contar tipos de motherboard soportados
        mb_support = case['compatibility']['motherboard']
        if mb_support:
            motherboard_support[mb_support] += 1
        
        # Contar tipos de PSU soportados
        psu_support_type = case['compatibility']['power_supply']
        if psu_support_type:
            psu_support[psu_support_type] += 1
        
        # Recopilar longitudes de GPU soportadas
        gpu_length = case['compatibility']['supported_gpu_length']['value']
        if gpu_length:
            gpu_lengths.append(gpu_length)
        
        # Recopilar alturas de CPU cooler soportadas
        cooler_height = case['compatibility']['supported_cpu_cooler_height']['value']
        if cooler_height:
            cpu_cooler_heights.append(cooler_height)
    
    return {
        'motherboard_support': dict(motherboard_support.most_common()),
        'psu_support': dict(psu_support.most_common()),
        'gpu_length_stats': {
            'min': min(gpu_lengths) if gpu_lengths else None,
            'max': max(gpu_lengths) if gpu_lengths else None,
            'mean': statistics.mean(gpu_lengths) if gpu_lengths else None,
            'median': statistics.median(gpu_lengths) if gpu_lengths else None
        },
        'cpu_cooler_height_stats': {
            'min': min(cpu_cooler_heights) if cpu_cooler_heights else None,
            'max': max(cpu_cooler_heights) if cpu_cooler_heights else None,
            'mean': statistics.mean(cpu_cooler_heights) if cpu_cooler_heights else None,
            'median': statistics.median(cpu_cooler_heights) if cpu_cooler_heights else None
        }
    }


def main():
    """Función principal del analizador"""
    print("📊 Analizador de Datos Normalizados")
    print("=" * 50)
    
    # Cargar datos
    base_path = Path(__file__).parent.parent
    data_file = base_path / 'normalized_data' / 'CaseData_normalized.json'
    
    if not data_file.exists():
        print(f"❌ Error: No se encontró {data_file}")
        print("Primero ejecuta el normalizador para generar los datos.")
        return
    
    print(f"📁 Cargando datos desde: {data_file}")
    data = load_normalized_data(str(data_file))
    print(f"📦 Total de gabinetes cargados: {len(data)}")
    
    # Análisis de dimensiones
    print("\n🔧 Análisis de Dimensiones")
    print("-" * 30)
    dim_analysis = analyze_dimensions(data)
    
    print(f"Ancho (mm):")
    print(f"  Min: {dim_analysis['width_stats']['min']:.1f}")
    print(f"  Max: {dim_analysis['width_stats']['max']:.1f}")
    print(f"  Promedio: {dim_analysis['width_stats']['mean']:.1f}")
    print(f"  Mediana: {dim_analysis['width_stats']['median']:.1f}")
    
    print(f"\nProfundidad (mm):")
    print(f"  Min: {dim_analysis['depth_stats']['min']:.1f}")
    print(f"  Max: {dim_analysis['depth_stats']['max']:.1f}")
    print(f"  Promedio: {dim_analysis['depth_stats']['mean']:.1f}")
    print(f"  Mediana: {dim_analysis['depth_stats']['median']:.1f}")
    
    print(f"\nAltura (mm):")
    print(f"  Min: {dim_analysis['height_stats']['min']:.1f}")
    print(f"  Max: {dim_analysis['height_stats']['max']:.1f}")
    print(f"  Promedio: {dim_analysis['height_stats']['mean']:.1f}")
    print(f"  Mediana: {dim_analysis['height_stats']['median']:.1f}")
    
    if dim_analysis['volume_stats']['count'] > 0:
        print(f"\nVolumen (litros):")
        print(f"  Min: {dim_analysis['volume_stats']['min']:.1f}L")
        print(f"  Max: {dim_analysis['volume_stats']['max']:.1f}L")
        print(f"  Promedio: {dim_analysis['volume_stats']['mean']:.1f}L")
        print(f"  Mediana: {dim_analysis['volume_stats']['median']:.1f}L")
        print(f"  Casos con volumen calculable: {dim_analysis['volume_stats']['count']}")
    
    # Análisis de compatibilidad
    print("\n🔌 Análisis de Compatibilidad")
    print("-" * 30)
    compat_analysis = analyze_compatibility(data)
    
    print("Soporte de Motherboards:")
    for mb_type, count in compat_analysis['motherboard_support'].items():
        percentage = (count / len(data)) * 100
        print(f"  {mb_type}: {count} casos ({percentage:.1f}%)")
    
    print(f"\nLongitud GPU soportada (mm):")
    gpu_stats = compat_analysis['gpu_length_stats']
    if gpu_stats['mean']:
        print(f"  Min: {gpu_stats['min']:.0f}mm")
        print(f"  Max: {gpu_stats['max']:.0f}mm")
        print(f"  Promedio: {gpu_stats['mean']:.0f}mm")
        print(f"  Mediana: {gpu_stats['median']:.0f}mm")
    
    print(f"\nAltura CPU Cooler soportada (mm):")
    cooler_stats = compat_analysis['cpu_cooler_height_stats']
    if cooler_stats['mean']:
        print(f"  Min: {cooler_stats['min']:.0f}mm")
        print(f"  Max: {cooler_stats['max']:.0f}mm")
        print(f"  Promedio: {cooler_stats['mean']:.0f}mm")
        print(f"  Mediana: {cooler_stats['median']:.0f}mm")
    
    # Análisis de ventiladores
    print("\n🌀 Análisis de Soporte de Ventiladores")
    print("-" * 30)
    fan_analysis = analyze_fan_support(data)
    
    for size in ['120mm', '140mm']:
        if fan_analysis[size]['max_slots_stats']['mean']:
            print(f"\nVentiladores {size}:")
            max_stats = fan_analysis[size]['max_slots_stats']
            print(f"  Slots máximos promedio: {max_stats['mean']:.1f}")
            print(f"  Configuraciones más comunes: {max_stats['common_values'][:3]}")
    
    print(f"\n✅ Análisis completado!")
    print(f"💡 Los datos normalizados permiten estos cálculos matemáticos automáticos")


if __name__ == "__main__":
    main()
