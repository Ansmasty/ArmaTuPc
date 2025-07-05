#!/usr/bin/env python3
"""
Análisis Térmico Comparativo
============================

Script que demuestra el poder del análisis térmico con datos normalizados,
mostrando correlaciones entre dimensiones de gabinetes y capacidades de CPU coolers.
"""

import json
import statistics
from pathlib import Path
import math


def load_both_datasets():
    """Carga ambos datasets normalizados"""
    base_path = Path(__file__).parent.parent / 'normalized_data'
    
    # Cargar datos de gabinetes
    case_file = base_path / 'CaseData_normalized.json'
    with open(case_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    # Cargar datos de coolers
    cooler_file = base_path / 'CPUCoolerData_normalized.json'
    with open(cooler_file, 'r', encoding='utf-8') as f:
        coolers = json.load(f)
    
    return cases, coolers


def calculate_case_thermal_capacity(case):
    """Calcula la capacidad térmica estimada de un gabinete"""
    dims = case['dimensions']
    fans = case['fan_support']
    
    # Volumen interno (litros)
    if all(d['value'] for d in [dims['width'], dims['depth'], dims['height']]):
        volume = (dims['width']['value'] * dims['depth']['value'] * dims['height']['value']) / 1000000
    else:
        return None
    
    # Factor de ventilación (ventiladores instalados + máximos)
    fan_score = 0
    for size, fan_data in fans.items():
        if fan_data['maximum'] is not None:
            # Peso por tamaño de ventilador (120mm = base 1.0)
            size_weight = {
                '80mm': 0.6,
                '120mm': 1.0,
                '140mm': 1.4,
                '200mm': 2.0
            }.get(size, 1.0)
            
            fan_score += fan_data['maximum'] * size_weight
    
    # Capacidad térmica estimada (W) = volumen * densidad_térmica + ventilación
    # Fórmula empírica: base 50W por litro + 25W por punto de ventilación
    if volume > 0:
        thermal_capacity = (volume * 50) + (fan_score * 25)
        return {
            'thermal_capacity_watts': thermal_capacity,
            'volume_liters': volume,
            'fan_score': fan_score,
            'thermal_density': thermal_capacity / volume
        }
    
    return None


def find_compatible_coolers(case, coolers):
    """Encuentra coolers compatibles con un gabinete específico"""
    compatible = []
    case_height_limit = case['compatibility']['supported_cpu_cooler_height']['value']
    
    if not case_height_limit:
        return compatible
    
    for cooler in coolers:
        cooler_height = cooler['specifications']['height']['value']
        
        if cooler_height and cooler_height <= case_height_limit:
            # Agregar información de compatibilidad
            cooler_copy = cooler.copy()
            cooler_copy['fit_margin'] = case_height_limit - cooler_height
            cooler_copy['height_utilization'] = (cooler_height / case_height_limit) * 100
            compatible.append(cooler_copy)
    
    return compatible


def analyze_thermal_matching():
    """Analiza el matching térmico entre gabinetes y coolers"""
    cases, coolers = load_both_datasets()
    
    print("🔥 Análisis de Matching Térmico Case-Cooler")
    print("=" * 50)
    
    # Análisis de muestra: primeros 5 gabinetes
    sample_cases = cases[:5]
    
    thermal_matches = []
    
    for i, case in enumerate(sample_cases):
        print(f"\n📦 Case {i+1}: {case['name'][:50]}...")
        
        # Calcular capacidad térmica del gabinete
        thermal_cap = calculate_case_thermal_capacity(case)
        if not thermal_cap:
            print("   ❌ No se pudo calcular capacidad térmica")
            continue
        
        print(f"   🌡️ Capacidad térmica estimada: {thermal_cap['thermal_capacity_watts']:.0f}W")
        print(f"   📏 Volumen: {thermal_cap['volume_liters']:.1f}L")
        print(f"   🌀 Factor ventilación: {thermal_cap['fan_score']:.1f}")
        
        # Encontrar coolers compatibles
        compatible_coolers = find_compatible_coolers(case, coolers)
        print(f"   🔧 Coolers compatibles (altura): {len(compatible_coolers)}")
        
        if compatible_coolers:
            # Filtrar coolers con TDP conocido
            coolers_with_tdp = [c for c in compatible_coolers if c['specifications']['tdp']['value']]
            
            if coolers_with_tdp:
                # Encontrar el cooler óptimo (máximo TDP que no exceda capacidad térmica)
                optimal_coolers = [
                    c for c in coolers_with_tdp 
                    if c['specifications']['tdp']['value'] <= thermal_cap['thermal_capacity_watts']
                ]
                
                if optimal_coolers:
                    best_cooler = max(optimal_coolers, key=lambda x: x['specifications']['tdp']['value'])
                    print(f"   ⭐ Mejor match: {best_cooler['name'][:30]}...")
                    print(f"      TDP: {best_cooler['specifications']['tdp']['value']}W")
                    print(f"      Utilización térmica: {(best_cooler['specifications']['tdp']['value']/thermal_cap['thermal_capacity_watts'])*100:.1f}%")
                    
                    thermal_matches.append({
                        'case': case['name'],
                        'cooler': best_cooler['name'],
                        'case_thermal_capacity': thermal_cap['thermal_capacity_watts'],
                        'cooler_tdp': best_cooler['specifications']['tdp']['value'],
                        'thermal_utilization': (best_cooler['specifications']['tdp']['value']/thermal_cap['thermal_capacity_watts'])*100,
                        'volume': thermal_cap['volume_liters']
                    })
                else:
                    print("   ⚠️ Ningún cooler óptimo encontrado (TDP excede capacidad)")
            else:
                print("   ⚠️ No hay coolers compatibles con TDP conocido")
    
    return thermal_matches


def analyze_thermal_efficiency():
    """Analiza la eficiencia térmica del dataset"""
    cases, coolers = load_both_datasets()
    
    print(f"\n📊 Análisis de Eficiencia Térmica Global")
    print("=" * 45)
    
    # Estadísticas de capacidad térmica de gabinetes
    case_thermal_capacities = []
    case_volumes = []
    
    for case in cases:
        thermal_cap = calculate_case_thermal_capacity(case)
        if thermal_cap:
            case_thermal_capacities.append(thermal_cap['thermal_capacity_watts'])
            case_volumes.append(thermal_cap['volume_liters'])
    
    # Estadísticas de TDP de coolers
    cooler_tdps = []
    cooler_heights = []
    
    for cooler in coolers:
        tdp = cooler['specifications']['tdp']['value']
        height = cooler['specifications']['height']['value']
        if tdp:
            cooler_tdps.append(tdp)
        if height:
            cooler_heights.append(height)
    
    print(f"Capacidades térmicas de gabinetes (W):")
    if case_thermal_capacities:
        print(f"  Min: {min(case_thermal_capacities):.0f}W")
        print(f"  Max: {max(case_thermal_capacities):.0f}W")
        print(f"  Promedio: {statistics.mean(case_thermal_capacities):.0f}W")
        print(f"  Mediana: {statistics.median(case_thermal_capacities):.0f}W")
    
    print(f"\nTDP de CPU Coolers (W):")
    if cooler_tdps:
        print(f"  Min: {min(cooler_tdps):.0f}W")
        print(f"  Max: {max(cooler_tdps):.0f}W")
        print(f"  Promedio: {statistics.mean(cooler_tdps):.0f}W")
        print(f"  Mediana: {statistics.median(cooler_tdps):.0f}W")
    
    # Correlación altura vs TDP en coolers
    height_tdp_pairs = []
    for cooler in coolers:
        tdp = cooler['specifications']['tdp']['value']
        height = cooler['specifications']['height']['value']
        if tdp and height and height > 0:
            height_tdp_pairs.append((height, tdp))
    
    if height_tdp_pairs:
        print(f"\n🔗 Correlación Altura-TDP en Coolers:")
        print(f"  Muestras válidas: {len(height_tdp_pairs)}")
        
        # Calcular correlación simple
        heights = [pair[0] for pair in height_tdp_pairs]
        tdps = [pair[1] for pair in height_tdp_pairs]
        
        # Eficiencia térmica (TDP/altura)
        thermal_efficiencies = [tdp/height for height, tdp in height_tdp_pairs]
        print(f"  Eficiencia térmica promedio: {statistics.mean(thermal_efficiencies):.2f} W/mm")
        print(f"  Mejor eficiencia: {max(thermal_efficiencies):.2f} W/mm")


def main():
    """Función principal del análisis térmico comparativo"""
    print("🌡️ Análisis Térmico Comparativo - Cases vs Coolers")
    print("=" * 60)
    
    try:
        # Análisis de matching térmico
        thermal_matches = analyze_thermal_matching()
        
        # Análisis de eficiencia global
        analyze_thermal_efficiency()
        
        print(f"\n✅ Análisis térmico completado!")
        print(f"💡 La normalización permite análisis térmicos sofisticados:")
        print(f"   • Cálculo de capacidades térmicas de gabinetes")
        print(f"   • Matching automático case-cooler por compatibilidad")
        print(f"   • Análisis de eficiencia térmica (W/mm)")
        print(f"   • Optimización de configuraciones térmicas")
        
        if thermal_matches:
            print(f"\n🎯 Se encontraron {len(thermal_matches)} matches térmicos óptimos")
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de ejecutar primero el normalizador para generar los datos.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
