#!/usr/bin/env python3
"""
Ejemplo de uso del nuevo sistema de análisis matemático
Este script muestra cómo el nuevo sistema de análisis funciona con builds completos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces.analisis_tab import AnalisisMatematicoTab

def crear_build_ejemplo():
    """Crea un build de ejemplo para demostrar el análisis"""
    return {
        'cpu': {
            'name': 'Intel Core i7-12700K',
            'base_clock': 3.6,
            'boost_clock': 5.0,
            'cores': 12,
            'tdp': 125,
            'integrated_graphics': 'Intel UHD Graphics 770'
        },
        'gpu': {
            'name': 'NVIDIA GeForce RTX 4070',
            'base_clock': 1920,
            'boost_clock': 2475,
            'memory_size': 12,
            'memory_type': 'GDDR6X',
            'tdp': 200
        },
        'case': {
            'name': 'Corsair 4000D Airflow',
            'form_factor': 'ATX',
            'material': 'Steel',
            'dimensions': {'width': 230, 'height': 453, 'depth': 466},
            'fan_slots': 6,
            'max_gpu_length': 360,
            'max_cpu_cooler_height': 170
        },
        'cpu_cooler': {
            'name': 'Noctua NH-D15',
            'type': 'Air',
            'socket_compatibility': ['LGA1700', 'AM4'],
            'height': 165,
            'tdp_rating': 220
        },
        'psu': {
            'name': 'Corsair RM750x',
            'wattage': 750,
            'efficiency': '80+ Gold',
            'modular': True,
            'form_factor': 'ATX'
        },
        'motherboard': {
            'name': 'ASUS ROG Strix Z690-E',
            'socket': 'LGA1700',
            'form_factor': 'ATX',
            'chipset': 'Z690'
        },
        'ram': {
            'name': 'Corsair Vengeance RGB Pro 32GB',
            'capacity': 32,
            'speed': 3200,
            'type': 'DDR4',
            'modules': 2
        },
        'storage': {
            'name': 'Samsung 980 Pro 1TB',
            'capacity': 1000,
            'type': 'NVMe',
            'interface': 'PCIe 4.0'
        }
    }

def main():
    """Función principal para demostrar el uso del sistema"""
    print("=== Sistema de Análisis Matemático de PC Builder ===")
    print("Ejemplo de uso del nuevo sistema refactorizado")
    print()
    
    # Crear instancia del análisis
    print("1. Creando instancia del análisis matemático...")
    analisis_tab = AnalisisMatematicoTab()
    
    # Crear build de ejemplo
    print("2. Creando build de ejemplo...")
    build_ejemplo = crear_build_ejemplo()
    
    # Mostrar información del build
    print("3. Build de ejemplo:")
    for componente, datos in build_ejemplo.items():
        if isinstance(datos, dict) and 'name' in datos:
            print(f"   - {componente.upper()}: {datos['name']}")
    
    # Simular actualización de configuración
    print("\n4. Simulando actualización de configuración...")
    try:
        analisis_tab.actualizar_configuracion(build_ejemplo)
        print("   ✓ Configuración actualizada exitosamente")
    except Exception as e:
        print(f"   ✗ Error actualizando configuración: {e}")
    
    # Mostrar información del estado actual
    print("\n5. Estado actual del análisis:")
    configuracion = analisis_tab.obtener_configuracion_actual()
    
    print(f"   - Potencia adicional: {configuracion['potencia_adicional']} W")
    print(f"   - Temperatura ambiente: {configuracion['temperatura_ambiente']} °C")
    print(f"   - Factor de ventilación: {configuracion['factor_ventilacion']:.1f}x")
    print(f"   - Build activo: {'Sí' if configuracion['build_actual'] else 'No'}")
    
    # Información sobre análisis matemático
    print("\n6. Análisis matemático disponible:")
    print("   - Análisis térmico con derivadas")
    print("   - Análisis de eficiencia energética")
    print("   - Análisis de sensibilidad de parámetros")
    print("   - Generación de gráficos interactivos")
    print("   - Exportación de resultados")
    
    print("\n=== Ejemplo completado ===")
    print("El sistema está listo para usar con builds reales desde la pestaña principal.")

if __name__ == "__main__":
    main()
