#!/usr/bin/env python3
"""
Resumen del Sistema de Normalización
====================================

Script que genera un resumen completo de todos los componentes normalizados
y las capacidades del sistema.
"""

import json
from pathlib import Path


def load_all_normalized_data():
    """Carga todos los datasets normalizados"""
    base_path = Path(__file__).parent.parent / 'normalized_data'
    
    datasets = {}
    
    # Intentar cargar cada dataset
    dataset_files = {
        'cases': 'CaseData_normalized.json',
        'coolers': 'CPUCoolerData_normalized.json',
        'cpus': 'CPUData_normalized.json',
        'gpus': 'GPUData_normalized.json'
    }
    
    for name, filename in dataset_files.items():
        file_path = base_path / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                datasets[name] = json.load(f)
            print(f"✅ {name.upper()}: {len(datasets[name])} registros cargados")
        else:
            print(f"❌ {name.upper()}: Archivo no encontrado")
    
    return datasets


def demonstrate_cross_component_analysis(datasets):
    """Demuestra análisis cruzado entre componentes"""
    print(f"\n🔗 Análisis Cruzado de Componentes")
    print("=" * 35)
    
    if 'cases' not in datasets or 'coolers' not in datasets:
        print("❌ Datos insuficientes para análisis cruzado")
        return
    
    cases = datasets['cases']
    coolers = datasets['coolers']
    
    # Ejemplo: Encontrar coolers compatibles con el primer gabinete
    sample_case = cases[0]
    case_cooler_height_limit = sample_case['compatibility']['supported_cpu_cooler_height']['value']
    
    print(f"📦 Gabinete ejemplo: {sample_case['name'][:50]}...")
    print(f"   Altura máxima cooler: {case_cooler_height_limit} mm")
    
    if case_cooler_height_limit:
        compatible_coolers = []
        for cooler in coolers:
            cooler_height = cooler['specifications']['height']['value']
            if cooler_height and cooler_height <= case_cooler_height_limit:
                compatible_coolers.append({
                    'name': cooler['name'],
                    'height': cooler_height,
                    'tdp': cooler['specifications']['tdp']['value'],
                    'type': cooler['compatibility_analysis']['cooler_type']
                })
        
        print(f"   🌡️ Coolers compatibles encontrados: {len(compatible_coolers)}")
        
        # Mostrar algunos ejemplos
        if compatible_coolers:
            # Ordenar por TDP descendente
            compatible_coolers.sort(key=lambda x: x['tdp'] or 0, reverse=True)
            print(f"   Top 3 por TDP:")
            for i, cooler in enumerate(compatible_coolers[:3]):
                tdp_str = f"{cooler['tdp']}W" if cooler['tdp'] else "N/A"
                print(f"     {i+1}. {cooler['name'][:30]}... ({tdp_str}, {cooler['height']}mm)")


def demonstrate_mathematical_capabilities(datasets):
    """Demuestra capacidades matemáticas con datos normalizados"""
    print(f"\n🧮 Capacidades Matemáticas Avanzadas")
    print("=" * 40)
    
    if 'cases' in datasets:
        cases = datasets['cases']
        
        # Calcular volúmenes automáticamente
        volumes = []
        for case in cases:
            dims = case['dimensions']
            if all(d['value'] for d in [dims['width'], dims['depth'], dims['height']]):
                volume = (dims['width']['value'] * dims['depth']['value'] * dims['height']['value']) / 1000000
                volumes.append(volume)
        
        if volumes:
            avg_volume = sum(volumes) / len(volumes)
            min_volume = min(volumes)
            max_volume = max(volumes)
            
            print(f"📦 Análisis de volúmenes de gabinetes:")
            print(f"   Volumen promedio: {avg_volume:.1f}L")
            print(f"   Rango: {min_volume:.1f}L - {max_volume:.1f}L")
            print(f"   Gabinetes analizados: {len(volumes)}")
    
    if 'cpus' in datasets:
        cpus = datasets['cpus']
        
        # Calcular eficiencias automáticamente
        efficiencies = []
        for cpu in cpus:
            efficiency = cpu['calculated_metrics']['efficiency_score']
            if efficiency:
                efficiencies.append(efficiency)
        
        if efficiencies:
            avg_efficiency = sum(efficiencies) / len(efficiencies)
            max_efficiency = max(efficiencies)
            
            print(f"\n💻 Análisis de eficiencia de CPUs:")
            print(f"   Eficiencia promedio: {avg_efficiency:.1f} puntos/W")
            print(f"   Máxima eficiencia: {max_efficiency:.1f} puntos/W")
            print(f"   CPUs analizados: {len(efficiencies)}")
    
    if 'coolers' in datasets:
        coolers = datasets['coolers']
        
        # Calcular factores térmicos
        thermal_factors = []
        for cooler in coolers:
            factor = cooler['compatibility_analysis']['thermal_factor']
            if factor:
                thermal_factors.append(factor)
        
        if thermal_factors:
            avg_thermal = sum(thermal_factors) / len(thermal_factors)
            
            print(f"\n🌡️ Análisis térmico de coolers:")
            print(f"   Factor térmico promedio: {avg_thermal:.1f}")
            print(f"   Coolers analizados: {len(thermal_factors)}")
    
    if 'gpus' in datasets:
        gpus = datasets['gpus']
        
        # Calcular eficiencias de GPU
        gpu_efficiencies = []
        gpu_performance_scores = []
        for gpu in gpus:
            efficiency = gpu['calculated_metrics']['power_efficiency']
            performance = gpu['calculated_metrics']['performance_score']
            if efficiency:
                gpu_efficiencies.append(efficiency)
            if performance:
                gpu_performance_scores.append(performance)
        
        if gpu_efficiencies:
            avg_gpu_efficiency = sum(gpu_efficiencies) / len(gpu_efficiencies)
            max_gpu_performance = max(gpu_performance_scores) if gpu_performance_scores else 0
            
            print(f"\n🎮 Análisis de rendimiento de GPUs:")
            print(f"   Eficiencia energética promedio: {avg_gpu_efficiency:.1f}")
            print(f"   Máximo rendimiento: {max_gpu_performance:.0f}")
            print(f"   GPUs analizadas: {len(gpu_efficiencies)}")


def show_normalization_benefits():
    """Muestra las ventajas de la normalización"""
    print(f"\n🎯 Beneficios de la Normalización")
    print("=" * 35)
    
    benefits = [
        "✅ Separación automática de valores numéricos y unidades",
        "✅ Cálculos matemáticos directos (volúmenes, eficiencias, ratios)",
        "✅ Análisis térmico avanzado (capacidades, matching)",
        "✅ Categorización automática inteligente",
        "✅ Compatibilidad cruzada entre componentes",
        "✅ Métricas calculadas automáticamente",
        "✅ Formato JSON estándar para APIs",
        "✅ Base sólida para machine learning",
        "✅ Análisis estadístico habilitado",
        "✅ Optimización de configuraciones"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")


def show_examples_comparison():
    """Muestra comparación antes vs después"""
    print(f"\n📊 Antes vs Después de la Normalización")
    print("=" * 45)
    
    print("🔸 ANTES (datos originales):")
    print("   'AMD Ryzen 5 5600X', '3.7 GHz', '4.6 GHz', '6', '12', '65 W'")
    print("   ↳ Datos como strings, análisis manual requerido")
    
    print("\n🔸 DESPUÉS (datos normalizados):")
    print("   {")
    print('     "name": "AMD Ryzen 5 5600X",')
    print('     "performance": {')
    print('       "base_clock": {"value": 3.7, "unit": "GHz"},')
    print('       "turbo_clock": {"value": 4.6, "unit": "GHz"}')
    print('     },')
    print('     "architecture": {')
    print('       "cores": 6, "threads": 12,')
    print('       "tdp": {"value": 65.0, "unit": "W"}')
    print('     },')
    print('     "calculated_metrics": {')
    print('       "performance_score": 44400.0,')
    print('       "efficiency_score": 683.08,')
    print('       "frequency_boost_ratio": 1.24,')
    print('       "cpu_category": "performance_standard"')
    print('     }')
    print("   }")
    print("   ↳ ¡Análisis matemático y categorización automática!")


def main():
    """Función principal del resumen"""
    print("🎯 RESUMEN DEL SISTEMA DE NORMALIZACIÓN")
    print("=" * 50)
    print("Sistema completo para normalizar datasets de componentes PC")
    print("separando valores numéricos de unidades para análisis avanzado.")
    print()
    
    # Cargar todos los datos
    datasets = load_all_normalized_data()
    
    if not datasets:
        print("❌ No se encontraron datos normalizados.")
        print("Ejecuta primero: python normalizador_dataset.py")
        return
    
    # Mostrar estadísticas generales
    total_components = sum(len(data) for data in datasets.values())
    print(f"\n📈 Estadísticas Generales:")
    print(f"   Total de componentes normalizados: {total_components}")
    print(f"   Tipos de componentes: {len(datasets)}")
    print(f"   Archivos JSON generados: {len(datasets)}")
    
    # Demostraciones
    demonstrate_cross_component_analysis(datasets)
    demonstrate_mathematical_capabilities(datasets)
    show_examples_comparison()
    show_normalization_benefits()
    
    print(f"\n🚀 Próximos Pasos Sugeridos:")
    print("=" * 30)
    print("  1. Normalizar más componentes (GPU, RAM, Motherboard)")
    print("  2. Crear API REST para consultas normalizadas")
    print("  3. Implementar algoritmos de matching automático")
    print("  4. Desarrollar dashboard web para visualización")
    print("  5. Aplicar machine learning para predicciones")
    
    print(f"\n✨ El sistema está listo para análisis avanzados!")
    print("💡 Los datos normalizados transforman strings en conocimiento accionable.")


if __name__ == "__main__":
    main()
