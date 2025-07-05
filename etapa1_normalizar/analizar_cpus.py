#!/usr/bin/env python3
"""
Analizador de CPU Data Normalizada
==================================

Script para analizar datos normalizados de CPUs con enfoque en 
rendimiento, eficiencia y categorización.
"""

import json
import statistics
from pathlib import Path
from collections import Counter


def load_cpu_data(file_path: str) -> list:
    """Carga los datos normalizados de CPUs desde JSON"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def analyze_performance_metrics(data: list) -> dict:
    """Analiza métricas de rendimiento de los CPUs"""
    base_clocks = []
    turbo_clocks = []
    performance_scores = []
    efficiency_scores = []
    boost_ratios = []
    
    for cpu in data:
        perf = cpu['performance']
        metrics = cpu['calculated_metrics']
        
        # Recopilar frecuencias base
        if perf['base_clock']['value'] is not None:
            base_clocks.append(perf['base_clock']['value'])
        
        # Recopilar frecuencias turbo
        if perf['turbo_clock']['value'] is not None:
            turbo_clocks.append(perf['turbo_clock']['value'])
        
        # Recopilar métricas calculadas
        if metrics['performance_score'] is not None:
            performance_scores.append(metrics['performance_score'])
        
        if metrics['efficiency_score'] is not None:
            efficiency_scores.append(metrics['efficiency_score'])
        
        if metrics['frequency_boost_ratio'] is not None:
            boost_ratios.append(metrics['frequency_boost_ratio'])
    
    return {
        'base_clock_stats': {
            'min': min(base_clocks) if base_clocks else None,
            'max': max(base_clocks) if base_clocks else None,
            'mean': statistics.mean(base_clocks) if base_clocks else None,
            'median': statistics.median(base_clocks) if base_clocks else None,
            'count': len(base_clocks)
        },
        'turbo_clock_stats': {
            'min': min(turbo_clocks) if turbo_clocks else None,
            'max': max(turbo_clocks) if turbo_clocks else None,
            'mean': statistics.mean(turbo_clocks) if turbo_clocks else None,
            'median': statistics.median(turbo_clocks) if turbo_clocks else None,
            'count': len(turbo_clocks)
        },
        'performance_score_stats': {
            'min': min(performance_scores) if performance_scores else None,
            'max': max(performance_scores) if performance_scores else None,
            'mean': statistics.mean(performance_scores) if performance_scores else None,
            'median': statistics.median(performance_scores) if performance_scores else None,
            'count': len(performance_scores)
        },
        'efficiency_stats': {
            'min': min(efficiency_scores) if efficiency_scores else None,
            'max': max(efficiency_scores) if efficiency_scores else None,
            'mean': statistics.mean(efficiency_scores) if efficiency_scores else None,
            'median': statistics.median(efficiency_scores) if efficiency_scores else None,
            'count': len(efficiency_scores)
        },
        'boost_ratio_stats': {
            'min': min(boost_ratios) if boost_ratios else None,
            'max': max(boost_ratios) if boost_ratios else None,
            'mean': statistics.mean(boost_ratios) if boost_ratios else None,
            'median': statistics.median(boost_ratios) if boost_ratios else None,
            'count': len(boost_ratios)
        }
    }


def analyze_architecture_distribution(data: list) -> dict:
    """Analiza la distribución de arquitecturas de CPU"""
    core_counts = Counter()
    thread_counts = Counter()
    tdp_ranges = Counter()
    socket_types = Counter()
    cpu_categories = Counter()
    threads_per_core = Counter()
    
    for cpu in data:
        arch = cpu['architecture']
        metrics = cpu['calculated_metrics']
        
        # Contar núcleos
        if arch['cores'] is not None:
            core_counts[arch['cores']] += 1
        
        # Contar hilos
        if arch['threads'] is not None:
            thread_counts[arch['threads']] += 1
        
        # Agrupar TDP en rangos
        if arch['tdp']['value'] is not None:
            tdp_value = arch['tdp']['value']
            if tdp_value <= 35:
                tdp_ranges['Ultra Low Power (≤35W)'] += 1
            elif tdp_value <= 65:
                tdp_ranges['Low Power (36-65W)'] += 1
            elif tdp_value <= 105:
                tdp_ranges['Standard (66-105W)'] += 1
            elif tdp_value <= 125:
                tdp_ranges['High Performance (106-125W)'] += 1
            else:
                tdp_ranges['Extreme (>125W)'] += 1
        
        # Contar tipos de socket
        if arch['socket']:
            socket_types[arch['socket']] += 1
        
        # Contar categorías de CPU
        if metrics['cpu_category']:
            cpu_categories[metrics['cpu_category']] += 1
        
        # Contar threads por core
        if metrics['threads_per_core'] is not None:
            threads_per_core[metrics['threads_per_core']] += 1
    
    return {
        'core_distribution': dict(core_counts.most_common()),
        'thread_distribution': dict(thread_counts.most_common()),
        'tdp_ranges': dict(tdp_ranges.most_common()),
        'socket_distribution': dict(socket_types.most_common()),
        'category_distribution': dict(cpu_categories.most_common()),
        'threads_per_core_distribution': dict(threads_per_core.most_common()),
        'total_cpus': len(data)
    }


def analyze_integrated_graphics(data: list) -> dict:
    """Analiza CPUs con gráficos integrados"""
    igpu_count = 0
    igpu_models = Counter()
    igpu_by_producer = Counter()
    
    for cpu in data:
        igpu = cpu['integrated_graphics']
        producer = cpu['producer']
        
        if igpu['has_igpu']:
            igpu_count += 1
            igpu_by_producer[producer] += 1
            
            if igpu['gpu_model']:
                # Extraer modelo base (sin detalles específicos)
                model = igpu['gpu_model']
                if 'Vega' in model:
                    igpu_models['Radeon Vega Series'] += 1
                elif 'UHD' in model:
                    igpu_models['Intel UHD Graphics'] += 1
                elif 'Iris' in model:
                    igpu_models['Intel Iris Graphics'] += 1
                elif 'Ryzen' in model:
                    igpu_models['Ryzen Graphics'] += 1
                else:
                    igpu_models[model] += 1
    
    total_cpus = len(data)
    igpu_percentage = (igpu_count / total_cpus * 100) if total_cpus > 0 else 0
    
    return {
        'igpu_statistics': {
            'total_with_igpu': igpu_count,
            'total_without_igpu': total_cpus - igpu_count,
            'igpu_percentage': igpu_percentage
        },
        'igpu_models': dict(igpu_models.most_common()),
        'igpu_by_producer': dict(igpu_by_producer.most_common())
    }


def analyze_manufacturers(data: list) -> dict:
    """Analiza fabricantes y sus estrategias de producto"""
    manufacturers = Counter()
    manufacturer_categories = {}
    manufacturer_tdp_avg = {}
    manufacturer_performance_avg = {}
    
    for cpu in data:
        producer = cpu['producer']
        if not producer:
            continue
        
        manufacturers[producer] += 1
        
        # Analizar categorías por fabricante
        if producer not in manufacturer_categories:
            manufacturer_categories[producer] = Counter()
        
        category = cpu['calculated_metrics']['cpu_category']
        if category:
            manufacturer_categories[producer][category] += 1
        
        # Calcular TDP promedio por fabricante
        tdp_value = cpu['architecture']['tdp']['value']
        if tdp_value:
            if producer not in manufacturer_tdp_avg:
                manufacturer_tdp_avg[producer] = []
            manufacturer_tdp_avg[producer].append(tdp_value)
        
        # Calcular rendimiento promedio por fabricante
        perf_score = cpu['calculated_metrics']['performance_score']
        if perf_score:
            if producer not in manufacturer_performance_avg:
                manufacturer_performance_avg[producer] = []
            manufacturer_performance_avg[producer].append(perf_score)
    
    # Calcular promedios
    for producer in manufacturer_tdp_avg:
        tdp_values = manufacturer_tdp_avg[producer]
        manufacturer_tdp_avg[producer] = {
            'average': statistics.mean(tdp_values),
            'count': len(tdp_values),
            'min': min(tdp_values),
            'max': max(tdp_values)
        }
    
    for producer in manufacturer_performance_avg:
        perf_values = manufacturer_performance_avg[producer]
        manufacturer_performance_avg[producer] = {
            'average': statistics.mean(perf_values),
            'count': len(perf_values),
            'min': min(perf_values),
            'max': max(perf_values)
        }
    
    return {
        'market_share': dict(manufacturers.most_common()),
        'category_specialization': {
            producer: dict(categories.most_common()) 
            for producer, categories in manufacturer_categories.items()
        },
        'thermal_profiles': manufacturer_tdp_avg,
        'performance_profiles': manufacturer_performance_avg
    }


def main():
    """Función principal del analizador de CPUs"""
    print("💻 Analizador de CPU Data Normalizada")
    print("=" * 45)
    
    # Cargar datos
    base_path = Path(__file__).parent.parent
    data_file = base_path / 'normalized_data' / 'CPUData_normalized.json'
    
    if not data_file.exists():
        print(f"❌ Error: No se encontró {data_file}")
        print("Primero ejecuta el normalizador para generar los datos.")
        return
    
    print(f"📁 Cargando datos desde: {data_file}")
    data = load_cpu_data(str(data_file))
    print(f"💻 Total de CPUs cargados: {len(data)}")
    
    # Análisis de rendimiento
    print("\n🚀 Análisis de Rendimiento")
    print("-" * 30)
    perf_analysis = analyze_performance_metrics(data)
    
    base_stats = perf_analysis['base_clock_stats']
    if base_stats['count'] > 0:
        print(f"Frecuencia Base (GHz):")
        print(f"  Min: {base_stats['min']:.1f} GHz")
        print(f"  Max: {base_stats['max']:.1f} GHz")
        print(f"  Promedio: {base_stats['mean']:.1f} GHz")
        print(f"  Mediana: {base_stats['median']:.1f} GHz")
    
    turbo_stats = perf_analysis['turbo_clock_stats']
    if turbo_stats['count'] > 0:
        print(f"\nFrecuencia Turbo (GHz):")
        print(f"  Min: {turbo_stats['min']:.1f} GHz")
        print(f"  Max: {turbo_stats['max']:.1f} GHz")
        print(f"  Promedio: {turbo_stats['mean']:.1f} GHz")
        print(f"  Mediana: {turbo_stats['median']:.1f} GHz")
    
    perf_stats = perf_analysis['performance_score_stats']
    if perf_stats['count'] > 0:
        print(f"\nPuntuación de Rendimiento:")
        print(f"  Min: {perf_stats['min']:.0f}")
        print(f"  Max: {perf_stats['max']:.0f}")
        print(f"  Promedio: {perf_stats['mean']:.0f}")
    
    # Análisis de arquitectura
    print("\n🏗️ Análisis de Arquitectura")
    print("-" * 30)
    arch_analysis = analyze_architecture_distribution(data)
    
    print("Distribución de núcleos:")
    for cores, count in list(arch_analysis['core_distribution'].items())[:8]:
        percentage = (count / arch_analysis['total_cpus']) * 100
        print(f"  {cores} núcleos: {count} CPUs ({percentage:.1f}%)")
    
    print(f"\nDistribución de TDP:")
    for tdp_range, count in arch_analysis['tdp_ranges'].items():
        percentage = (count / arch_analysis['total_cpus']) * 100
        print(f"  {tdp_range}: {count} ({percentage:.1f}%)")
    
    print(f"\nSockets más comunes:")
    for socket, count in list(arch_analysis['socket_distribution'].items())[:5]:
        percentage = (count / arch_analysis['total_cpus']) * 100
        print(f"  {socket}: {count} ({percentage:.1f}%)")
    
    # Análisis de gráficos integrados
    print("\n🎮 Análisis de Gráficos Integrados")
    print("-" * 35)
    igpu_analysis = analyze_integrated_graphics(data)
    
    igpu_stats = igpu_analysis['igpu_statistics']
    print(f"CPUs con iGPU: {igpu_stats['total_with_igpu']} ({igpu_stats['igpu_percentage']:.1f}%)")
    print(f"CPUs sin iGPU: {igpu_stats['total_without_igpu']} ({100-igpu_stats['igpu_percentage']:.1f}%)")
    
    if igpu_analysis['igpu_models']:
        print(f"\nModelos de iGPU más comunes:")
        for model, count in list(igpu_analysis['igpu_models'].items())[:5]:
            print(f"  {model}: {count}")
    
    # Análisis de fabricantes
    print("\n🏭 Análisis de Fabricantes")
    print("-" * 25)
    manufacturer_analysis = analyze_manufacturers(data)
    
    print("Participación de mercado:")
    for manufacturer, count in manufacturer_analysis['market_share'].items():
        percentage = (count / len(data)) * 100
        print(f"  {manufacturer}: {count} ({percentage:.1f}%)")
    
    # Mostrar perfiles térmicos de fabricantes
    print(f"\nPerfiles térmicos promedio:")
    for manufacturer, profile in manufacturer_analysis['thermal_profiles'].items():
        if profile['count'] >= 5:  # Solo mostrar fabricantes con suficientes datos
            print(f"  {manufacturer}: {profile['average']:.1f}W promedio ({profile['count']} CPUs)")
    
    print(f"\n✅ Análisis completado!")
    print(f"💡 La normalización permite análisis detallado de rendimiento y eficiencia")


if __name__ == "__main__":
    main()
