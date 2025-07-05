#!/usr/bin/env python3
"""
Analizador de Datos de GPU Normalizados
========================================

Este script analiza los datos normalizados de GPUs para mostrar las capacidades
del sistema de análisis matemático y estadístico.

Autor: Sistema de Normalización
Fecha: 2025-07-03
"""

import json
import statistics
from pathlib import Path
from collections import defaultdict, Counter
import math


def load_gpu_data():
    """Carga los datos normalizados de GPU"""
    base_path = Path(__file__).parent.parent
    gpu_file = base_path / 'normalized_data' / 'GPUData_normalized.json'
    
    if not gpu_file.exists():
        print(f"❌ No se encontró el archivo: {gpu_file}")
        return None
    
    with open(gpu_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_gpu_categories(gpus):
    """Analiza la distribución de categorías de GPU"""
    print("🎮 ANÁLISIS DE CATEGORÍAS DE GPU")
    print("=" * 50)
    
    categories = Counter()
    form_factors = Counter()
    power_categories = Counter()
    
    for gpu in gpus:
        metrics = gpu.get('calculated_metrics', {})
        categories[metrics.get('gpu_category', 'unknown')] += 1
        form_factors[metrics.get('form_factor', 'unknown')] += 1
        power_categories[metrics.get('power_requirement_category', 'unknown')] += 1
    
    print("📊 Distribución por categoría de rendimiento:")
    for category, count in categories.most_common():
        percentage = (count / len(gpus)) * 100
        print(f"  {category.replace('_', ' ').title()}: {count} GPUs ({percentage:.1f}%)")
    
    print("\n📏 Distribución por factor forma:")
    for form_factor, count in form_factors.most_common():
        percentage = (count / len(gpus)) * 100
        print(f"  {form_factor.replace('_', ' ').title()}: {count} GPUs ({percentage:.1f}%)")
    
    print("\n⚡ Distribución por requerimientos de alimentación:")
    for power_cat, count in power_categories.most_common():
        percentage = (count / len(gpus)) * 100
        print(f"  {power_cat.replace('_', ' ').title()}: {count} GPUs ({percentage:.1f}%)")


def analyze_performance_metrics(gpus):
    """Analiza métricas de rendimiento"""
    print("\n\n🚀 ANÁLISIS DE RENDIMIENTO")
    print("=" * 50)
    
    # Recopilar métricas numéricas
    boost_clocks = []
    vram_sizes = []
    tdp_values = []
    performance_scores = []
    efficiency_scores = []
    memory_bandwidths = []
    
    for gpu in gpus:
        perf = gpu.get('performance', {})
        metrics = gpu.get('calculated_metrics', {})
        
        # Boost Clock
        boost_clock = perf.get('boost_clock', {}).get('value')
        if boost_clock:
            boost_clocks.append(boost_clock)
        
        # VRAM
        vram = perf.get('vram', {}).get('value')
        if vram:
            vram_sizes.append(vram)
        
        # TDP
        tdp = perf.get('tdp', {}).get('value')
        if tdp:
            tdp_values.append(tdp)
        
        # Performance Score
        perf_score = metrics.get('performance_score')
        if perf_score:
            performance_scores.append(perf_score)
        
        # Power Efficiency
        efficiency = metrics.get('power_efficiency')
        if efficiency:
            efficiency_scores.append(efficiency)
        
        # Memory Bandwidth
        bandwidth = metrics.get('memory_bandwidth_estimate')
        if bandwidth:
            memory_bandwidths.append(bandwidth)
    
    # Análisis estadístico de Boost Clock
    if boost_clocks:
        print("🔥 Frecuencias Boost Clock (MHz):")
        print(f"  Promedio: {statistics.mean(boost_clocks):.0f} MHz")
        print(f"  Mediana: {statistics.median(boost_clocks):.0f} MHz")
        print(f"  Mínimo: {min(boost_clocks):.0f} MHz")
        print(f"  Máximo: {max(boost_clocks):.0f} MHz")
        print(f"  Desv. Estándar: {statistics.stdev(boost_clocks):.0f} MHz")
    
    # Análisis de VRAM
    if vram_sizes:
        print(f"\n💾 Memoria de Video (GB):")
        vram_distribution = Counter(vram_sizes)
        for size, count in sorted(vram_distribution.items()):
            percentage = (count / len(vram_sizes)) * 100
            print(f"  {size} GB: {count} GPUs ({percentage:.1f}%)")
    
    # Análisis de TDP
    if tdp_values:
        print(f"\n⚡ Consumo Energético TDP (W):")
        print(f"  Promedio: {statistics.mean(tdp_values):.0f} W")
        print(f"  Mediana: {statistics.median(tdp_values):.0f} W")
        print(f"  Mínimo: {min(tdp_values):.0f} W")
        print(f"  Máximo: {max(tdp_values):.0f} W")
        print(f"  Desv. Estándar: {statistics.stdev(tdp_values):.0f} W")
    
    # Top 10 GPUs por rendimiento
    if performance_scores:
        print(f"\n🏆 TOP 10 GPUS POR RENDIMIENTO:")
        gpus_with_scores = []
        for gpu in gpus:
            score = gpu.get('calculated_metrics', {}).get('performance_score')
            if score:
                gpus_with_scores.append((gpu['name'], score, gpu.get('producer', 'Unknown')))
        
        top_gpus = sorted(gpus_with_scores, key=lambda x: x[1], reverse=True)[:10]
        for i, (name, score, producer) in enumerate(top_gpus, 1):
            print(f"  {i:2}. {name} ({producer}) - Score: {score:.0f}")


def analyze_physical_dimensions(gpus):
    """Analiza dimensiones físicas"""
    print("\n\n📏 ANÁLISIS DE DIMENSIONES FÍSICAS")
    print("=" * 50)
    
    lengths = []
    slots = []
    
    for gpu in gpus:
        physical = gpu.get('physical', {})
        
        # Longitud
        length = physical.get('length', {}).get('value')
        if length:
            lengths.append(length)
        
        # Slots
        slot_count = physical.get('slots')
        if slot_count:
            slots.append(slot_count)
    
    # Análisis de longitudes
    if lengths:
        print("📐 Longitudes de GPU (mm):")
        print(f"  Promedio: {statistics.mean(lengths):.1f} mm")
        print(f"  Mediana: {statistics.median(lengths):.1f} mm")
        print(f"  Mínimo: {min(lengths):.1f} mm")
        print(f"  Máximo: {max(lengths):.1f} mm")
        
        # Categorización por longitud
        compact = sum(1 for l in lengths if l <= 200)
        standard = sum(1 for l in lengths if 200 < l <= 280)
        large = sum(1 for l in lengths if l > 280)
        
        print(f"\n📊 Distribución por longitud:")
        print(f"  Compacta (≤200mm): {compact} GPUs ({(compact/len(lengths)*100):.1f}%)")
        print(f"  Estándar (200-280mm): {standard} GPUs ({(standard/len(lengths)*100):.1f}%)")
        print(f"  Grande (>280mm): {large} GPUs ({(large/len(lengths)*100):.1f}%)")
    
    # Análisis de slots
    if slots:
        print(f"\n🔌 Distribución por slots ocupados:")
        slot_distribution = Counter(slots)
        for slot_count, count in sorted(slot_distribution.items()):
            percentage = (count / len(slots)) * 100
            print(f"  {slot_count} slots: {count} GPUs ({percentage:.1f}%)")


def analyze_connectivity(gpus):
    """Analiza conectividad y salidas"""
    print("\n\n🔌 ANÁLISIS DE CONECTIVIDAD")
    print("=" * 50)
    
    # Análisis de conectores de alimentación
    power_8pin = []
    power_6pin = []
    total_power_connectors = []
    
    # Análisis de salidas de video
    hdmi_counts = []
    dp_counts = []
    total_outputs = []
    
    for gpu in gpus:
        power = gpu.get('power', {})
        display = gpu.get('display_outputs', {})
        
        # Conectores de alimentación
        pin8 = power.get('eight_pin_connectors', 0)
        pin6 = power.get('six_pin_connectors', 0)
        power_8pin.append(pin8)
        power_6pin.append(pin6)
        total_power_connectors.append(pin8 + pin6)
        
        # Salidas de video
        hdmi = display.get('hdmi_ports', 0)
        dp = display.get('displayport_outputs', 0)
        total = display.get('total_outputs', 0)
        
        hdmi_counts.append(hdmi)
        dp_counts.append(dp)
        total_outputs.append(total)
    
    # Análisis de alimentación
    print("⚡ Conectores de alimentación:")
    print(f"  Promedio conectores 8-pin: {statistics.mean(power_8pin):.1f}")
    print(f"  Promedio conectores 6-pin: {statistics.mean(power_6pin):.1f}")
    print(f"  Promedio total conectores: {statistics.mean(total_power_connectors):.1f}")
    
    no_external_power = sum(1 for total in total_power_connectors if total == 0)
    single_connector = sum(1 for total in total_power_connectors if total == 1)
    dual_connector = sum(1 for total in total_power_connectors if total == 2)
    triple_plus = sum(1 for total in total_power_connectors if total >= 3)
    
    print(f"\n📊 Distribución por conectores de alimentación:")
    print(f"  Solo PCIe (0 conectores): {no_external_power} GPUs ({(no_external_power/len(gpus)*100):.1f}%)")
    print(f"  Un conector: {single_connector} GPUs ({(single_connector/len(gpus)*100):.1f}%)")
    print(f"  Dos conectores: {dual_connector} GPUs ({(dual_connector/len(gpus)*100):.1f}%)")
    print(f"  Tres o más: {triple_plus} GPUs ({(triple_plus/len(gpus)*100):.1f}%)")
    
    # Análisis de salidas de video
    if total_outputs:
        print(f"\n🖥️ Salidas de video:")
        print(f"  Promedio puertos HDMI: {statistics.mean(hdmi_counts):.1f}")
        print(f"  Promedio salidas DisplayPort: {statistics.mean(dp_counts):.1f}")
        print(f"  Promedio total salidas: {statistics.mean(total_outputs):.1f}")


def analyze_manufacturer_distribution(gpus):
    """Analiza distribución por fabricante"""
    print("\n\n🏭 ANÁLISIS POR FABRICANTE")
    print("=" * 50)
    
    manufacturers = Counter()
    
    for gpu in gpus:
        manufacturer = gpu.get('producer', 'Unknown')
        manufacturers[manufacturer] += 1
    
    print("📊 Top 10 fabricantes:")
    for manufacturer, count in manufacturers.most_common(10):
        percentage = (count / len(gpus)) * 100
        print(f"  {manufacturer}: {count} modelos ({percentage:.1f}%)")


def main():
    """Función principal del analizador"""
    print("🎮 ANALIZADOR DE DATOS DE GPU NORMALIZADOS")
    print("=" * 60)
    
    # Cargar datos
    gpu_data = load_gpu_data()
    if not gpu_data:
        return
    
    print(f"📋 Datos cargados: {len(gpu_data)} GPUs")
    print("=" * 60)
    
    # Realizar análisis
    analyze_gpu_categories(gpu_data)
    analyze_performance_metrics(gpu_data)
    analyze_physical_dimensions(gpu_data)
    analyze_connectivity(gpu_data)
    analyze_manufacturer_distribution(gpu_data)
    
    print(f"\n✅ Análisis completado!")
    print("Los datos normalizados permiten realizar cálculos matemáticos precisos")
    print("y análisis estadísticos avanzados de las especificaciones de GPU.")


if __name__ == "__main__":
    main()
