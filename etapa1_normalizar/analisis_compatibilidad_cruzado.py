#!/usr/bin/env python3
"""
Análisis Cruzado de Compatibilidad GPU-Case-Cooler
==================================================

Este script realiza análisis avanzado de compatibilidad entre GPUs, gabinetes
y coolers, demostrando las capacidades del sistema de normalización.

Autor: Sistema de Normalización
Fecha: 2025-07-03
"""

import json
import statistics
from pathlib import Path
from collections import defaultdict, Counter
import math


def load_all_data():
    """Carga todos los datos normalizados"""
    base_path = Path(__file__).parent.parent
    normalized_path = base_path / 'normalized_data'
    
    data = {}
    
    # Archivos a cargar
    files = {
        'cases': 'CaseData_normalized.json',
        'coolers': 'CPUCoolerData_normalized.json',
        'cpus': 'CPUData_normalized.json',
        'gpus': 'GPUData_normalized.json'
    }
    
    for key, filename in files.items():
        file_path = normalized_path / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        else:
            print(f"⚠️ No se encontró: {filename}")
            data[key] = []
    
    return data


def analyze_gpu_case_compatibility(gpus, cases):
    """Analiza compatibilidad entre GPUs y gabinetes"""
    print("🎮📦 ANÁLISIS DE COMPATIBILIDAD GPU-GABINETE")
    print("=" * 60)
    
    compatible_combinations = 0
    total_combinations = len(gpus) * len(cases)
    
    # Contadores de problemas de compatibilidad
    length_issues = 0
    slot_issues = 0
    power_issues = 0
    
    # Análisis por categorías
    compatibility_by_gpu_category = defaultdict(lambda: {'compatible': 0, 'total': 0})
    compatibility_by_case_size = defaultdict(lambda: {'compatible': 0, 'total': 0})
    
    print(f"🔍 Analizando {len(gpus)} GPUs vs {len(cases)} gabinetes...")
    
    for gpu in gpus[:100]:  # Limitamos para no sobrecargar
        gpu_length = gpu.get('physical', {}).get('length', {}).get('value', 0)
        gpu_slots = gpu.get('physical', {}).get('slots', 0)
        gpu_category = gpu.get('calculated_metrics', {}).get('gpu_category', 'unknown')
        
        if not gpu_length or not gpu_slots:
            continue
        
        for case in cases[:100]:  # Limitamos para no sobrecargar
            case_gpu_support = case.get('compatibility', {}).get('supported_gpu_length', {}).get('value', 0)
            case_motherboard = case.get('compatibility', {}).get('motherboard', '').lower()
            
            # Determinar tamaño de gabinete
            case_dims = case.get('dimensions', {})
            case_volume = 1
            for dim_key in ['width', 'depth', 'height']:
                dim_val = case_dims.get(dim_key, {}).get('value', 0)
                if dim_val:
                    case_volume *= dim_val
            
            if case_volume < 30000:  # mm³
                case_size = 'mini_itx'
            elif case_volume < 60000:
                case_size = 'micro_atx'
            else:
                case_size = 'atx_plus'
            
            # Verificar compatibilidad
            is_compatible = True
            
            # Verificar longitud
            if case_gpu_support and gpu_length > case_gpu_support:
                is_compatible = False
                length_issues += 1
            
            # Verificar slots (asumimos que la mayoría de cases soportan hasta 3 slots)
            if gpu_slots > 3.0:
                is_compatible = False
                slot_issues += 1
            
            # Actualizar contadores
            compatibility_by_gpu_category[gpu_category]['total'] += 1
            compatibility_by_case_size[case_size]['total'] += 1
            
            if is_compatible:
                compatible_combinations += 1
                compatibility_by_gpu_category[gpu_category]['compatible'] += 1
                compatibility_by_case_size[case_size]['compatible'] += 1
    
    # Mostrar resultados
    analyzed_combinations = len(gpus[:100]) * len(cases[:100])
    compatibility_rate = (compatible_combinations / analyzed_combinations) * 100
    
    print(f"📊 Resultados del análisis:")
    print(f"  Combinaciones analizadas: {analyzed_combinations:,}")
    print(f"  Combinaciones compatibles: {compatible_combinations:,}")
    print(f"  Tasa de compatibilidad: {compatibility_rate:.1f}%")
    
    print(f"\n⚠️ Principales problemas de incompatibilidad:")
    print(f"  Longitud de GPU: {length_issues:,} casos")
    print(f"  Exceso de slots: {slot_issues:,} casos")
    
    print(f"\n📈 Compatibilidad por categoría de GPU:")
    for category, stats in compatibility_by_gpu_category.items():
        if stats['total'] > 0:
            rate = (stats['compatible'] / stats['total']) * 100
            print(f"  {category.replace('_', ' ').title()}: {rate:.1f}% ({stats['compatible']}/{stats['total']})")
    
    print(f"\n📈 Compatibilidad por tamaño de gabinete:")
    for size, stats in compatibility_by_case_size.items():
        if stats['total'] > 0:
            rate = (stats['compatible'] / stats['total']) * 100
            print(f"  {size.replace('_', ' ').title()}: {rate:.1f}% ({stats['compatible']}/{stats['total']})")


def analyze_thermal_setup(gpus, coolers, cpus):
    """Analiza configuraciones térmicas óptimas"""
    print("\n\n🌡️ ANÁLISIS TÉRMICO AVANZADO")
    print("=" * 60)
    
    # Crear perfiles térmicos
    thermal_profiles = {
        'low_power': {'cpu_tdp_max': 65, 'gpu_tdp_max': 150, 'total_tdp_max': 200},
        'mainstream': {'cpu_tdp_max': 105, 'gpu_tdp_max': 250, 'total_tdp_max': 350},
        'high_performance': {'cpu_tdp_max': 150, 'gpu_tdp_max': 350, 'total_tdp_max': 500},
        'enthusiast': {'cpu_tdp_max': 250, 'gpu_tdp_max': 500, 'total_tdp_max': 750}
    }
    
    print("🔥 Análisis de perfiles térmicos:")
    
    for profile_name, limits in thermal_profiles.items():
        print(f"\n📊 Perfil {profile_name.replace('_', ' ').title()}:")
        
        # Contar componentes compatibles
        compatible_cpus = []
        compatible_gpus = []
        compatible_coolers = []
        
        for cpu in cpus:
            cpu_tdp = cpu.get('architecture', {}).get('tdp', {}).get('value', 0)
            if cpu_tdp and cpu_tdp <= limits['cpu_tdp_max']:
                compatible_cpus.append(cpu)
        
        for gpu in gpus:
            gpu_tdp = gpu.get('performance', {}).get('tdp', {}).get('value', 0)
            if gpu_tdp and gpu_tdp <= limits['gpu_tdp_max']:
                compatible_gpus.append(gpu)
        
        for cooler in coolers:
            cooler_tdp = cooler.get('specifications', {}).get('tdp', {}).get('value', 0)
            if cooler_tdp and cooler_tdp >= limits['cpu_tdp_max']:
                compatible_coolers.append(cooler)
        
        print(f"  CPUs compatibles: {len(compatible_cpus)}/{len(cpus)} ({len(compatible_cpus)/len(cpus)*100:.1f}%)")
        print(f"  GPUs compatibles: {len(compatible_gpus)}/{len(gpus)} ({len(compatible_gpus)/len(gpus)*100:.1f}%)")
        print(f"  Coolers compatibles: {len(compatible_coolers)}/{len(coolers)} ({len(compatible_coolers)/len(coolers)*100:.1f}%)")
        
        # Calcular configuraciones completas posibles
        total_configs = len(compatible_cpus) * len(compatible_gpus) * len(compatible_coolers)
        print(f"  Configuraciones posibles: {total_configs:,}")


def analyze_performance_scaling(gpus, cpus):
    """Analiza escalado de rendimiento GPU-CPU"""
    print("\n\n⚡ ANÁLISIS DE ESCALADO DE RENDIMIENTO")
    print("=" * 60)
    
    # Categorizar CPUs y GPUs por rendimiento
    cpu_tiers = defaultdict(list)
    gpu_tiers = defaultdict(list)
    
    for cpu in cpus:
        category = cpu.get('calculated_metrics', {}).get('cpu_category', 'unknown')
        cpu_tiers[category].append(cpu)
    
    for gpu in gpus:
        category = gpu.get('calculated_metrics', {}).get('gpu_category', 'unknown')
        gpu_tiers[category].append(gpu)
    
    print("🎯 Combinaciones recomendadas por nivel de rendimiento:")
    
    # Matriz de compatibilidad por rendimiento
    performance_matrix = {
        'entry_level': ['entry_level', 'budget'],
        'budget': ['entry_level', 'budget', 'mainstream'],
        'mainstream': ['budget', 'mainstream', 'performance'],
        'performance': ['mainstream', 'performance', 'performance_standard'],
        'high_end': ['performance', 'high_performance', 'workstation'],
        'enthusiast': ['high_performance', 'workstation', 'extreme']
    }
    
    for gpu_tier, compatible_cpu_tiers in performance_matrix.items():
        if gpu_tier in gpu_tiers:
            gpu_count = len(gpu_tiers[gpu_tier])
            
            compatible_cpu_count = 0
            for cpu_tier in compatible_cpu_tiers:
                if cpu_tier in cpu_tiers:
                    compatible_cpu_count += len(cpu_tiers[cpu_tier])
            
            print(f"  {gpu_tier.replace('_', ' ').title()} GPU ({gpu_count} modelos):")
            print(f"    -> CPUs compatibles: {compatible_cpu_count} modelos")
            
            if gpu_count > 0 and compatible_cpu_count > 0:
                total_combinations = gpu_count * compatible_cpu_count
                print(f"    -> Combinaciones posibles: {total_combinations:,}")


def analyze_form_factor_constraints(gpus, cases):
    """Analiza restricciones de factor forma"""
    print("\n\n📏 ANÁLISIS DE RESTRICCIONES DE FACTOR FORMA")
    print("=" * 60)
    
    # Análisis de GPUs por factor forma vs gabinetes
    gpu_form_factors = Counter()
    case_sizes = Counter()
    
    for gpu in gpus:
        form_factor = gpu.get('calculated_metrics', {}).get('form_factor', 'unknown')
        gpu_form_factors[form_factor] += 1
    
    for case in cases:
        # Determinar tamaño de gabinete basado en dimensiones
        dims = case.get('dimensions', {})
        width = dims.get('width', {}).get('value', 0)
        depth = dims.get('depth', {}).get('value', 0)
        height = dims.get('height', {}).get('value', 0)
        
        if width and depth and height:
            volume = width * depth * height
            if volume < 25000:  # mm³
                case_size = 'mini_itx'
            elif volume < 50000:
                case_size = 'micro_atx'
            elif volume < 80000:
                case_size = 'mid_tower'
            else:
                case_size = 'full_tower'
        else:
            case_size = 'unknown'
        
        case_sizes[case_size] += 1
    
    print("📊 Distribución de factores forma GPU:")
    for form_factor, count in gpu_form_factors.most_common():
        percentage = (count / len(gpus)) * 100
        print(f"  {form_factor.replace('_', ' ').title()}: {count} GPUs ({percentage:.1f}%)")
    
    print(f"\n📊 Distribución de tamaños de gabinete:")
    for case_size, count in case_sizes.most_common():
        percentage = (count / len(cases)) * 100
        print(f"  {case_size.replace('_', ' ').title()}: {count} cases ({percentage:.1f}%)")
    
    # Matriz de compatibilidad
    print(f"\n🔗 Matriz de compatibilidad (estimada):")
    print(f"  Mini-ITX -> Low Profile, Compact GPUs")
    print(f"  Micro-ATX -> Compact, Standard GPUs")
    print(f"  Mid-Tower -> Standard, Large GPUs")
    print(f"  Full-Tower -> Cualquier GPU")


def main():
    """Función principal del analizador cruzado"""
    print("🔄 ANÁLISIS CRUZADO DE COMPATIBILIDAD DE COMPONENTES")
    print("=" * 70)
    
    # Cargar todos los datos
    print("📋 Cargando datos normalizados...")
    data = load_all_data()
    
    if not all(data.values()):
        print("❌ Error: No se pudieron cargar todos los datos")
        return
    
    print(f"✅ Datos cargados:")
    print(f"  - {len(data['cases'])} gabinetes")
    print(f"  - {len(data['coolers'])} coolers")
    print(f"  - {len(data['cpus'])} CPUs")
    print(f"  - {len(data['gpus'])} GPUs")
    
    # Realizar análisis cruzados
    analyze_gpu_case_compatibility(data['gpus'], data['cases'])
    analyze_thermal_setup(data['gpus'], data['coolers'], data['cpus'])
    analyze_performance_scaling(data['gpus'], data['cpus'])
    analyze_form_factor_constraints(data['gpus'], data['cases'])
    
    print(f"\n✅ Análisis cruzado completado!")
    print("🚀 El sistema de normalización permite análisis de compatibilidad")
    print("   y optimización de configuraciones de PC de manera automatizada.")


if __name__ == "__main__":
    main()
