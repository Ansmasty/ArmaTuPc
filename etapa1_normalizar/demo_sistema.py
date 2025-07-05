#!/usr/bin/env python3
"""
Demostración del Sistema de Normalización
=========================================

Script que demuestra todas las capacidades del sistema de normalización
y análisis matemático con datos separados en valores y unidades.
"""

import json
from pathlib import Path
from clases import Dimension, FanSlots, ThermalDesignPower, SocketSupport


def demo_dimension_parsing():
    """Demuestra el parsing de dimensiones"""
    print("📏 Demostración: Parsing de Dimensiones")
    print("-" * 40)
    
    examples = ["230 mm", "15.6 inches", "45.7 cm", "", "invalid"]
    
    for example in examples:
        dim = Dimension.from_string(example)
        print(f"'{example}' → Valor: {dim.value}, Unidad: '{dim.unit}'")
        
        # Demostrar conversión automática (ejemplo simplificado)
        if dim.value and dim.unit == "mm":
            cm_value = dim.value / 10
            print(f"    Conversión automática: {cm_value} cm")
    
    print()


def demo_thermal_calculations():
    """Demuestra cálculos térmicos con TDP"""
    print("🌡️ Demostración: Cálculos Térmicos")
    print("-" * 35)
    
    tdp_examples = ["200 W", "150 W", "65 W", ""]
    
    for example in tdp_examples:
        tdp = ThermalDesignPower.from_string(example)
        if tdp.value:
            print(f"TDP: {tdp.value}W")
            print(f"  Categoría: {get_tdp_category(tdp.value)}")
            print(f"  Cooler recomendado: {recommend_cooler_type(tdp.value)}")
    
    print()


def demo_socket_compatibility():
    """Demuestra análisis de compatibilidad de sockets"""
    print("🔌 Demostración: Compatibilidad de Sockets")
    print("-" * 42)
    
    socket_example = "1150, 1151, 1155, AM4, AM5, FM2+"
    sockets = SocketSupport.from_string(socket_example)
    
    print(f"Sockets: {socket_example}")
    print(f"Total: {sockets.to_dict()['count']}")
    
    families = sockets.get_socket_families()
    print(f"Intel: {families['intel']}")
    print(f"AMD: {families['amd']}")
    print(f"¿Universal?: {len(families['intel']) > 0 and len(families['amd']) > 0}")
    
    print()


def demo_fan_calculations():
    """Demuestra cálculos de ventilación"""
    print("🌀 Demostración: Cálculos de Ventilación")
    print("-" * 40)
    
    fan_examples = ["2/6", "0/4", "1/1", ""]
    
    for example in fan_examples:
        fans = FanSlots.from_string(example)
        if fans.maximum is not None:
            utilization = (fans.installed / fans.maximum * 100) if fans.maximum > 0 else 0
            potential = fans.maximum - fans.installed
            print(f"Ventiladores {example}:")
            print(f"  Utilización actual: {utilization:.1f}%")
            print(f"  Potencial expansión: +{potential} ventiladores")
    
    print()


def demo_mathematical_analysis():
    """Demuestra análisis matemático avanzado"""
    print("🧮 Demostración: Análisis Matemático Avanzado")
    print("-" * 48)
    
    # Ejemplo de gabinete
    case_dims = {
        'width': Dimension.from_string("230 mm"),
        'depth': Dimension.from_string("450 mm"),
        'height': Dimension.from_string("460 mm")
    }
    
    # Cálculos automáticos
    volume_mm3 = case_dims['width'].value * case_dims['depth'].value * case_dims['height'].value
    volume_liters = volume_mm3 / 1000000
    
    print(f"📦 Gabinete ejemplo:")
    print(f"  Dimensiones: {case_dims['width'].value}×{case_dims['depth'].value}×{case_dims['height'].value} mm")
    print(f"  Volumen calculado: {volume_liters:.1f} litros")
    print(f"  Categoría por volumen: {get_case_category(volume_liters)}")
    
    # Ejemplo de análisis térmico
    fan_config = {
        '120mm': FanSlots.from_string("2/6"),
        '140mm': FanSlots.from_string("0/2")
    }
    
    airflow_potential = calculate_airflow_potential(fan_config)
    thermal_capacity = estimate_thermal_capacity(volume_liters, airflow_potential)
    
    print(f"\n🌡️ Análisis térmico:")
    print(f"  Potencial de flujo de aire: {airflow_potential:.1f} puntos")
    print(f"  Capacidad térmica estimada: {thermal_capacity:.0f}W")
    
    print()


def get_tdp_category(tdp_value):
    """Categoriza TDP por rango"""
    if tdp_value <= 65:
        return "Bajo consumo"
    elif tdp_value <= 125:
        return "Estándar"
    elif tdp_value <= 200:
        return "Alto rendimiento"
    else:
        return "Extremo"


def recommend_cooler_type(tdp_value):
    """Recomienda tipo de cooler basado en TDP"""
    if tdp_value <= 65:
        return "Stock cooler suficiente"
    elif tdp_value <= 125:
        return "Tower cooler recomendado"
    elif tdp_value <= 200:
        return "High-end air cooler o AIO 240mm"
    else:
        return "AIO 280mm+ requerido"


def get_case_category(volume_liters):
    """Categoriza gabinete por volumen"""
    if volume_liters <= 20:
        return "Mini-ITX compacto"
    elif volume_liters <= 35:
        return "Micro-ATX"
    elif volume_liters <= 50:
        return "ATX estándar"
    else:
        return "Full tower / E-ATX"


def calculate_airflow_potential(fan_config):
    """Calcula potencial de flujo de aire"""
    airflow_points = 0
    fan_weights = {'120mm': 1.0, '140mm': 1.4, '200mm': 2.0}
    
    for size, fans in fan_config.items():
        if fans.maximum:
            weight = fan_weights.get(size, 1.0)
            airflow_points += fans.maximum * weight
    
    return airflow_points


def estimate_thermal_capacity(volume, airflow_potential):
    """Estima capacidad térmica del sistema"""
    # Fórmula empírica: 50W base por litro + 25W por punto de airflow
    return (volume * 50) + (airflow_potential * 25)


def show_normalized_data_sample():
    """Muestra muestra de datos normalizados"""
    print("📄 Demostración: Datos Normalizados vs Originales")
    print("-" * 52)
    
    print("🔸 ANTES (datos originales):")
    print("  'be quiet! Dark Rock 4 - 135mm', '159 mm', '200 W'")
    print("  ↳ Datos como strings, análisis manual requerido")
    
    print("\n🔸 DESPUÉS (datos normalizados):")
    normalized_sample = {
        "name": "be quiet! Dark Rock 4 - 135mm",
        "specifications": {
            "height": {"value": 159.0, "unit": "mm"},
            "tdp": {"value": 200.0, "unit": "W"}
        },
        "compatibility_analysis": {
            "cooler_type": "passive",
            "thermal_factor": 188.68,
            "is_universal": True
        }
    }
    
    print("  {")
    print(f'    "name": "{normalized_sample["name"]}",')
    print("    \"specifications\": {")
    print(f'      "height": {normalized_sample["specifications"]["height"]},')
    print(f'      "tdp": {normalized_sample["specifications"]["tdp"]}')
    print("    },")
    print(f'    "thermal_factor": {normalized_sample["compatibility_analysis"]["thermal_factor"]}')
    print("  }")
    print("  ↳ Análisis matemático automático posible!")
    
    # Demostrar cálculos automáticos
    height = normalized_sample["specifications"]["height"]["value"]
    tdp = normalized_sample["specifications"]["tdp"]["value"]
    
    print(f"\n🧮 Cálculos automáticos habilitados:")
    print(f"  • Eficiencia térmica: {tdp/height:.2f} W/mm")
    print(f"  • Categoría TDP: {get_tdp_category(tdp)}")
    print(f"  • Recomendación: {recommend_cooler_type(tdp)}")
    
    print()


def main():
    """Función principal de la demostración"""
    print("🎯 DEMOSTRACIÓN DEL SISTEMA DE NORMALIZACIÓN")
    print("=" * 60)
    print("Este script demuestra las ventajas de separar valores numéricos")
    print("de sus unidades de medida para análisis matemáticos avanzados.")
    print()
    
    # Ejecutar todas las demostraciones
    demo_dimension_parsing()
    demo_thermal_calculations()
    demo_socket_compatibility()
    demo_fan_calculations()
    demo_mathematical_analysis()
    show_normalized_data_sample()
    
    print("🎉 RESUMEN DE VENTAJAS:")
    print("=" * 30)
    print("✅ Separación automática de valores y unidades")
    print("✅ Cálculos matemáticos directos (volumen, eficiencia)")
    print("✅ Análisis térmico avanzado (capacidad, matching)")
    print("✅ Compatibilidad inteligente (sockets, dimensiones)")
    print("✅ Categorización automática por rangos")
    print("✅ Formato JSON estándar para integración")
    print("✅ Análisis estadístico habilitado")
    print("✅ Base para machine learning y optimización")
    print()
    print("💡 Los datos normalizados transforman strings en conocimiento!")


if __name__ == "__main__":
    main()
