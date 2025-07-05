#!/usr/bin/env python3
"""
Analizador de CPU Coolers Normalizados
=====================================

Script especializado para analizar datos normalizados de CPU Coolers
con enfoque en análisis térmico y compatibilidad.
"""

import json
import statistics
from pathlib import Path
from collections import Counter


def load_cooler_data(file_path: str) -> list:
    """Carga los datos normalizados de CPU Coolers desde JSON"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def analyze_thermal_performance(data: list) -> dict:
    """Analiza el rendimiento térmico de los coolers"""
    tdp_values = []
    heights = []
    thermal_factors = []
    
    for cooler in data:
        specs = cooler['specifications']
        
        # Recopilar valores TDP
        if specs['tdp']['value'] is not None:
            tdp_values.append(specs['tdp']['value'])
        
        # Recopilar alturas
        if specs['height']['value'] is not None:
            heights.append(specs['height']['value'])
        
        # Recopilar factores térmicos
        thermal_factor = cooler['compatibility_analysis']['thermal_factor']
        if thermal_factor is not None:
            thermal_factors.append(thermal_factor)
    
    return {
        'tdp_stats': {
            'min': min(tdp_values) if tdp_values else None,
            'max': max(tdp_values) if tdp_values else None,
            'mean': statistics.mean(tdp_values) if tdp_values else None,
            'median': statistics.median(tdp_values) if tdp_values else None,
            'count': len(tdp_values)
        },
        'height_stats': {
            'min': min(heights) if heights else None,
            'max': max(heights) if heights else None,
            'mean': statistics.mean(heights) if heights else None,
            'median': statistics.median(heights) if heights else None,
            'count': len(heights)
        },
        'thermal_factor_stats': {
            'min': min(thermal_factors) if thermal_factors else None,
            'max': max(thermal_factors) if thermal_factors else None,
            'mean': statistics.mean(thermal_factors) if thermal_factors else None,
            'median': statistics.median(thermal_factors) if thermal_factors else None,
            'count': len(thermal_factors)
        }
    }


def analyze_cooler_types(data: list) -> dict:
    """Analiza los tipos de coolers en el dataset"""
    cooler_types = Counter()
    fan_distribution = Counter()
    
    for cooler in data:
        # Contar tipos de cooler
        cooler_type = cooler['compatibility_analysis']['cooler_type']
        cooler_types[cooler_type] += 1
        
        # Contar distribución de ventiladores
        total_fans = cooler['features']['total_fans']
        fan_distribution[total_fans] += 1
    
    return {
        'cooler_types': dict(cooler_types.most_common()),
        'fan_distribution': dict(fan_distribution.most_common()),
        'total_coolers': len(data)
    }


def analyze_socket_compatibility(data: list) -> dict:
    """Analiza la compatibilidad de sockets"""
    intel_support = Counter()
    amd_support = Counter()
    universal_coolers = 0
    intel_only = 0
    amd_only = 0
    
    all_intel_sockets = set()
    all_amd_sockets = set()
    
    for cooler in data:
        compat = cooler['compatibility_analysis']
        socket_families = compat['socket_families']
        
        # Recopilar todos los sockets únicos
        all_intel_sockets.update(socket_families['intel'])
        all_amd_sockets.update(socket_families['amd'])
        
        # Contar tipos de compatibilidad
        if compat['is_universal']:
            universal_coolers += 1
        elif compat['supports_intel'] and not compat['supports_amd']:
            intel_only += 1
        elif compat['supports_amd'] and not compat['supports_intel']:
            amd_only += 1
        
        # Contar sockets específicos
        for socket in socket_families['intel']:
            intel_support[socket] += 1
        for socket in socket_families['amd']:
            amd_support[socket] += 1
    
    return {
        'compatibility_distribution': {
            'universal': universal_coolers,
            'intel_only': intel_only,
            'amd_only': amd_only
        },
        'intel_sockets': {
            'total_unique': len(all_intel_sockets),
            'most_supported': dict(intel_support.most_common(10)),
            'all_sockets': sorted(list(all_intel_sockets))
        },
        'amd_sockets': {
            'total_unique': len(all_amd_sockets),
            'most_supported': dict(amd_support.most_common(10)),
            'all_sockets': sorted(list(all_amd_sockets))
        }
    }


def analyze_manufacturers(data: list) -> dict:
    """Analiza los fabricantes y sus especialidades"""
    manufacturers = Counter()
    manufacturer_cooler_types = {}
    manufacturer_avg_tdp = {}
    
    for cooler in data:
        producer = cooler['producer']
        if not producer:
            continue
            
        manufacturers[producer] += 1
        
        # Analizar tipos de cooler por fabricante
        if producer not in manufacturer_cooler_types:
            manufacturer_cooler_types[producer] = Counter()
        
        cooler_type = cooler['compatibility_analysis']['cooler_type']
        manufacturer_cooler_types[producer][cooler_type] += 1
        
        # Calcular TDP promedio por fabricante
        tdp_value = cooler['specifications']['tdp']['value']
        if tdp_value:
            if producer not in manufacturer_avg_tdp:
                manufacturer_avg_tdp[producer] = []
            manufacturer_avg_tdp[producer].append(tdp_value)
    
    # Calcular promedios de TDP
    for producer in manufacturer_avg_tdp:
        tdp_values = manufacturer_avg_tdp[producer]
        manufacturer_avg_tdp[producer] = {
            'average': statistics.mean(tdp_values),
            'count': len(tdp_values),
            'min': min(tdp_values),
            'max': max(tdp_values)
        }
    
    return {
        'market_share': dict(manufacturers.most_common()),
        'specializations': {
            producer: dict(types.most_common()) 
            for producer, types in manufacturer_cooler_types.items()
        },
        'thermal_capabilities': manufacturer_avg_tdp
    }


def main():
    """Función principal del analizador de CPU Coolers"""
    print("🌡️ Analizador de CPU Coolers Normalizados")
    print("=" * 50)
    
    # Cargar datos
    base_path = Path(__file__).parent.parent
    data_file = base_path / 'normalized_data' / 'CPUCoolerData_normalized.json'
    
    if not data_file.exists():
        print(f"❌ Error: No se encontró {data_file}")
        print("Primero ejecuta el normalizador para generar los datos.")
        return
    
    print(f"📁 Cargando datos desde: {data_file}")
    data = load_cooler_data(str(data_file))
    print(f"🌡️ Total de CPU Coolers cargados: {len(data)}")
    
    # Análisis térmico
    print("\n🔥 Análisis de Rendimiento Térmico")
    print("-" * 35)
    thermal_analysis = analyze_thermal_performance(data)
    
    tdp_stats = thermal_analysis['tdp_stats']
    if tdp_stats['count'] > 0:
        print(f"TDP (Watts):")
        print(f"  Min: {tdp_stats['min']:.0f}W")
        print(f"  Max: {tdp_stats['max']:.0f}W")
        print(f"  Promedio: {tdp_stats['mean']:.1f}W")
        print(f"  Mediana: {tdp_stats['median']:.0f}W")
        print(f"  Coolers con TDP: {tdp_stats['count']}")
    
    height_stats = thermal_analysis['height_stats']
    if height_stats['count'] > 0:
        print(f"\nAltura (mm):")
        print(f"  Min: {height_stats['min']:.0f}mm")
        print(f"  Max: {height_stats['max']:.0f}mm")
        print(f"  Promedio: {height_stats['mean']:.1f}mm")
        print(f"  Mediana: {height_stats['median']:.0f}mm")
    
    # Análisis de tipos de cooler
    print("\n🌀 Análisis de Tipos de Cooler")
    print("-" * 30)
    type_analysis = analyze_cooler_types(data)
    
    print("Distribución de tipos:")
    for cooler_type, count in type_analysis['cooler_types'].items():
        percentage = (count / type_analysis['total_coolers']) * 100
        print(f"  {cooler_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    print(f"\nDistribución de ventiladores:")
    for fan_count, count in list(type_analysis['fan_distribution'].items())[:5]:
        percentage = (count / type_analysis['total_coolers']) * 100
        print(f"  {fan_count} ventiladores: {count} ({percentage:.1f}%)")
    
    # Análisis de compatibilidad
    print("\n🔌 Análisis de Compatibilidad de Sockets")
    print("-" * 40)
    socket_analysis = analyze_socket_compatibility(data)
    
    compat_dist = socket_analysis['compatibility_distribution']
    total = sum(compat_dist.values())
    print("Compatibilidad:")
    print(f"  Universal (Intel + AMD): {compat_dist['universal']} ({(compat_dist['universal']/total)*100:.1f}%)")
    print(f"  Solo Intel: {compat_dist['intel_only']} ({(compat_dist['intel_only']/total)*100:.1f}%)")
    print(f"  Solo AMD: {compat_dist['amd_only']} ({(compat_dist['amd_only']/total)*100:.1f}%)")
    
    print(f"\nSockets Intel más soportados:")
    for socket, count in list(socket_analysis['intel_sockets']['most_supported'].items())[:5]:
        print(f"  {socket}: {count} coolers")
    
    print(f"\nSockets AMD más soportados:")
    for socket, count in list(socket_analysis['amd_sockets']['most_supported'].items())[:5]:
        print(f"  {socket}: {count} coolers")
    
    # Análisis de fabricantes
    print("\n🏭 Análisis de Fabricantes")
    print("-" * 25)
    manufacturer_analysis = analyze_manufacturers(data)
    
    print("Participación de mercado:")
    for manufacturer, count in list(manufacturer_analysis['market_share'].items())[:10]:
        percentage = (count / len(data)) * 100
        print(f"  {manufacturer}: {count} ({percentage:.1f}%)")
    
    # Mostrar especialización de top fabricantes
    top_manufacturers = list(manufacturer_analysis['market_share'].keys())[:5]
    print(f"\nEspecialización por tipo de cooler (top 5 fabricantes):")
    for manufacturer in top_manufacturers:
        if manufacturer in manufacturer_analysis['specializations']:
            specialization = manufacturer_analysis['specializations'][manufacturer]
            top_type = max(specialization.items(), key=lambda x: x[1])
            print(f"  {manufacturer}: {top_type[0].replace('_', ' ').title()} ({top_type[1]} modelos)")
    
    print(f"\n✅ Análisis completado!")
    print(f"💡 Los datos normalizados permiten análisis térmico avanzado")


if __name__ == "__main__":
    main()
