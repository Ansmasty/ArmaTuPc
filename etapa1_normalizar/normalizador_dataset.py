#!/usr/bin/env python3
"""
Normalizador de Dataset de Componentes de PC
============================================

Este script normaliza los datos del dataset separando valores numéricos de sus unidades
de medida para facilitar análisis matemáticos futuros.

Autor: Sistema de Normalización
Fecha: 2025-07-03
"""

import os
import sys
from pathlib import Path
from clases import CaseDataNormalizer, CPUCoolerDataNormalizer, CPUDataNormalizer, GPUDataNormalizer, MotherboardDataNormalizer, PSUDataNormalizer, RAMDataNormalizer, SSDDataNormalizer, HDDDataNormalizer


def main():
    """Función principal del normalizador"""
    # Configurar rutas
    base_path = Path(__file__).parent.parent
    dataset_path = base_path / 'dataset'
    output_path = base_path / 'normalized_data'
    
    # Crear directorio de salida si no existe
    output_path.mkdir(exist_ok=True)
    
    print("🔧 Iniciando normalización del dataset...")
    print("=" * 50)
    
    # Normalizar CaseData
    print("📦 Procesando CaseData.csv...")
    case_normalizer = CaseDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        case_data_path = dataset_path / 'CaseData.csv'
        if not case_data_path.exists():
            print(f"❌ Error: No se encontró {case_data_path}")
            return
        
        normalized_cases = case_normalizer.normalize_csv(str(case_data_path))
        
        # Guardar en JSON
        output_file = output_path / 'CaseData_normalized.json'
        case_normalizer.save_to_json(str(output_file))
        
        print(f"✅ CaseData normalizado exitosamente!")
        print(f"   - Registros procesados: {len(normalized_cases)}")
        print(f"   - Archivo guardado en: {output_file}")
        
        # Mostrar ejemplo del primer registro
        if normalized_cases:
            print("\n📋 Ejemplo del primer registro normalizado:")
            print("-" * 40)
            first_case = normalized_cases[0]
            print(f"Nombre: {first_case['name']}")
            print(f"Fabricante: {first_case['producer']}")
            
            # Mostrar dimensiones normalizadas
            dims = first_case['dimensions']
            print(f"Dimensiones:")
            print(f"  - Ancho: {dims['width']['value']} {dims['width']['unit']}")
            print(f"  - Profundidad: {dims['depth']['value']} {dims['depth']['unit']}")
            print(f"  - Alto: {dims['height']['value']} {dims['height']['unit']}")
            
            # Mostrar soporte de ventiladores
            fans = first_case['fan_support']
            print(f"Ventiladores 120mm: {fans['120mm']['installed']}/{fans['120mm']['maximum']}")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error procesando CaseData: {e}")
        return
    
    # Normalizar CPUCoolerData
    print("\n🌡️ Procesando CPUCoolerData.csv...")
    cooler_normalizer = CPUCoolerDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        cooler_data_path = dataset_path / 'CPUCoolerData.csv'
        if not cooler_data_path.exists():
            print(f"❌ Error: No se encontró {cooler_data_path}")
        else:
            normalized_coolers = cooler_normalizer.normalize_csv(str(cooler_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'CPUCoolerData_normalized.json'
            cooler_normalizer.save_to_json(str(output_file))
            
            print(f"✅ CPUCoolerData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_coolers)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_coolers:
                print("\n🌡️ Ejemplo del primer cooler normalizado:")
                print("-" * 40)
                first_cooler = normalized_coolers[0]
                print(f"Nombre: {first_cooler['name']}")
                print(f"Fabricante: {first_cooler['producer']}")
                
                # Mostrar especificaciones térmicas
                specs = first_cooler['specifications']
                print(f"Altura: {specs['height']['value']} {specs['height']['unit']}")
                print(f"TDP: {specs['tdp']['value']} {specs['tdp']['unit']}")
                
                # Mostrar compatibilidad
                compat = first_cooler['compatibility_analysis']
                print(f"Tipo de cooler: {compat['cooler_type']}")
                print(f"Sockets Intel: {len(compat['socket_families']['intel'])}")
                print(f"Sockets AMD: {len(compat['socket_families']['amd'])}")
                print(f"Universal: {compat['is_universal']}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando CPUCoolerData: {e}")
        return
    
    # Normalizar CPUData
    print("\n💻 Procesando CPUData.csv...")
    cpu_normalizer = CPUDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        cpu_data_path = dataset_path / 'CPUData.csv'
        if not cpu_data_path.exists():
            print(f"❌ Error: No se encontró {cpu_data_path}")
        else:
            normalized_cpus = cpu_normalizer.normalize_csv(str(cpu_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'CPUData_normalized.json'
            cpu_normalizer.save_to_json(str(output_file))
            
            print(f"✅ CPUData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_cpus)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_cpus:
                print("\n💻 Ejemplo del primer CPU normalizado:")
                print("-" * 40)
                first_cpu = normalized_cpus[0]
                print(f"Nombre: {first_cpu['name']}")
                print(f"Fabricante: {first_cpu['producer']}")
                
                # Mostrar especificaciones de rendimiento
                perf = first_cpu['performance']
                arch = first_cpu['architecture']
                metrics = first_cpu['calculated_metrics']
                
                print(f"Frecuencia base: {perf['base_clock']['value']} {perf['base_clock']['unit']}")
                print(f"Frecuencia turbo: {perf['turbo_clock']['value']} {perf['turbo_clock']['unit']}")
                print(f"Núcleos/Hilos: {arch['cores']}/{arch['threads']}")
                print(f"TDP: {arch['tdp']['value']} {arch['tdp']['unit']}")
                print(f"Socket: {arch['socket']}")
                print(f"Categoría: {metrics['cpu_category']}")
                
                if metrics['performance_score']:
                    print(f"Puntuación rendimiento: {metrics['performance_score']:.0f}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando CPUData: {e}")
        return
    
    # Normalizar GPUData
    print("\n🎮 Procesando GPUData.csv...")
    gpu_normalizer = GPUDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        gpu_data_path = dataset_path / 'GPUData.csv'
        if not gpu_data_path.exists():
            print(f"❌ Error: No se encontró {gpu_data_path}")
        else:
            normalized_gpus = gpu_normalizer.normalize_csv(str(gpu_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'GPUData_normalized.json'
            gpu_normalizer.save_to_json(str(output_file))
            
            print(f"✅ GPUData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_gpus)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_gpus:
                print("\n🎮 Ejemplo de la primera GPU normalizada:")
                print("-" * 40)
                first_gpu = normalized_gpus[0]
                print(f"Nombre: {first_gpu['name']}")
                print(f"Fabricante: {first_gpu['producer']}")
                
                # Mostrar especificaciones físicas y de rendimiento
                physical = first_gpu['physical']
                perf = first_gpu['performance']
                display = first_gpu['display_outputs']
                power = first_gpu['power']
                metrics = first_gpu['calculated_metrics']
                
                print(f"Longitud: {physical['length']['value']} {physical['length']['unit']}")
                print(f"Slots: {physical['slots']}")
                print(f"Boost Clock: {perf['boost_clock']['value']} {perf['boost_clock']['unit']}")
                print(f"VRAM: {perf['vram']['value']} {perf['vram']['unit']}")
                print(f"TDP: {perf['tdp']['value']} {perf['tdp']['unit']}")
                print(f"Conectores 8-pin: {power['eight_pin_connectors']}")
                print(f"Salidas totales: {display['total_outputs']}")
                print(f"Categoría: {metrics['gpu_category']}")
                
                if metrics['performance_score']:
                    print(f"Puntuación rendimiento: {metrics['performance_score']:.0f}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando GPUData: {e}")
        return
    
    # Normalizar MotherboardData
    print("\n🔧 Procesando MotherboardData.csv...")
    motherboard_normalizer = MotherboardDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        motherboard_data_path = dataset_path / 'MotherboardData.csv'
        if not motherboard_data_path.exists():
            print(f"❌ Error: No se encontró {motherboard_data_path}")
        else:
            normalized_motherboards = motherboard_normalizer.normalize_csv(str(motherboard_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'MotherboardData_normalized.json'
            motherboard_normalizer.save_to_json(str(output_file))
            
            print(f"✅ MotherboardData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_motherboards)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_motherboards:
                print("\n🔧 Ejemplo de la primera motherboard normalizada:")
                print("-" * 40)
                first_mb = normalized_motherboards[0]
                print(f"Nombre: {first_mb['name']}")
                print(f"Fabricante: {first_mb['producer']}")
                
                # Mostrar especificaciones de plataforma y memoria
                platform = first_mb['platform']
                memory = first_mb['memory']
                connectivity = first_mb['connectivity']
                metrics = first_mb['calculated_metrics']
                
                print(f"Socket: {platform['socket']}")
                print(f"Chipset: {platform['chipset']}")
                print(f"Factor forma: {first_mb['form_factor']}")
                print(f"Memoria: {memory['type']} - {memory['capacity']['value']} {memory['capacity']['unit']}")
                print(f"Slots RAM: {memory['slots']}")
                print(f"Puertos SATA: {connectivity['sata_ports']}")
                print(f"Salidas video: {connectivity['video_outputs']['total']}")
                print(f"Categoría: {metrics['motherboard_category']}")
                print(f"Mercado objetivo: {metrics['target_market']}")
                
                if metrics['memory_support_score']:
                    print(f"Puntuación memoria: {metrics['memory_support_score']}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando MotherboardData: {e}")
        return
    
    # Normalizar PSUData
    print("\n⚡ Procesando PSUData.csv...")
    psu_normalizer = PSUDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        psu_data_path = dataset_path / 'PSUData.csv'
        if not psu_data_path.exists():
            print(f"❌ Error: No se encontró {psu_data_path}")
        else:
            normalized_psus = psu_normalizer.normalize_csv(str(psu_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'PSUData_normalized.json'
            psu_normalizer.save_to_json(str(output_file))
            
            print(f"✅ PSUData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_psus)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_psus:
                print("\n⚡ Ejemplo de la primera PSU normalizada:")
                print("-" * 40)
                first_psu = normalized_psus[0]
                print(f"Nombre: {first_psu['name']}")
                print(f"Fabricante: {first_psu['producer']}")
                
                # Mostrar especificaciones de potencia
                power = first_psu['power']
                metrics = first_psu['calculated_metrics']
                
                print(f"Potencia: {power['wattage']['value']} {power['wattage']['unit']}")
                print(f"Factor forma: {first_psu['form_factor']}")
                print(f"Eficiencia: {power['efficiency']['full_rating']}")
                print(f"Puntuación eficiencia: {power['efficiency']['efficiency_score']}")
                print(f"Categoría: {metrics['psu_category']}")
                print(f"Mercado objetivo: {metrics['target_market']}")
                print(f"Potencia recomendada sistema: {metrics['recommended_system_wattage']} W")
                
                if metrics['power_efficiency_score']:
                    print(f"Puntuación total: {metrics['power_efficiency_score']}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando PSUData: {e}")
        return
    
    # Normalizar RAMData
    print("\n💾 Procesando RAMData.csv...")
    ram_normalizer = RAMDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        ram_data_path = dataset_path / 'RAMData.csv'
        if not ram_data_path.exists():
            print(f"❌ Error: No se encontró {ram_data_path}")
        else:
            normalized_rams = ram_normalizer.normalize_csv(str(ram_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'RAMData_normalized.json'
            ram_normalizer.save_to_json(str(output_file))
            
            print(f"✅ RAMData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_rams)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_rams:
                print("\n💾 Ejemplo del primer módulo RAM normalizado:")
                print("-" * 40)
                first_ram = normalized_rams[0]
                print(f"Nombre: {first_ram['name']}")
                print(f"Fabricante: {first_ram['producer']}")
                
                # Mostrar especificaciones de memoria
                specs = first_ram['memory_specs']
                metrics = first_ram['calculated_metrics']
                
                print(f"Tipo: {specs['ram_type']['generation']}")
                print(f"Capacidad: {specs['capacity']['value']} {specs['capacity']['unit']}")
                print(f"Frecuencia: {specs['frequency']['value']} {specs['frequency']['unit']}")
                print(f"Timings: {specs['timings']['raw_value']}")
                print(f"Módulos: {specs['sticks']}")
                print(f"Categoría: {metrics['ram_category']}")
                print(f"Mercado objetivo: {metrics['target_market']}")
                
                if metrics['capacity_per_stick']:
                    print(f"Capacidad por módulo: {metrics['capacity_per_stick']} GB")
                
                if metrics['performance_score']:
                    print(f"Puntuación rendimiento: {metrics['performance_score']}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando RAMData: {e}")
        return
    
    # Normalizar SSDData
    print("\n💽 Procesando SSDData.csv...")
    ssd_normalizer = SSDDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        ssd_data_path = dataset_path / 'SSDData.csv'
        if not ssd_data_path.exists():
            print(f"❌ Error: No se encontró {ssd_data_path}")
        else:
            normalized_ssds = ssd_normalizer.normalize_csv(str(ssd_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'SSDData_normalized.json'
            ssd_normalizer.save_to_json(str(output_file))
            
            print(f"✅ SSDData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_ssds)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_ssds:
                print("\n💽 Ejemplo del primer SSD normalizado:")
                print("-" * 40)
                first_ssd = normalized_ssds[0]
                print(f"Nombre: {first_ssd['name']}")
                print(f"Fabricante: {first_ssd['producer']}")
                
                # Mostrar especificaciones
                storage = first_ssd['storage_specs']
                tech = first_ssd['technical_specs']
                metrics = first_ssd['calculated_metrics']
                
                print(f"Capacidad: {storage['capacity']['value']} {storage['capacity']['unit']}")
                print(f"Factor forma: {storage['form_factor']}")
                print(f"Protocolo: {storage['protocol']}")
                print(f"Tipo NAND: {tech['nand_type']}")
                print(f"Controlador: {tech['controller']}")
                print(f"Categoría: {metrics['ssd_category']}")
                print(f"Tier rendimiento: {metrics['performance_tier']}")
                print(f"Mercado objetivo: {metrics['target_market']}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando SSDData: {e}")
        return
    
    # Normalizar HDDData
    print("\n💿 Procesando HDDData.csv...")
    hdd_normalizer = HDDDataNormalizer()
    
    try:
        # Cargar y normalizar datos
        hdd_data_path = dataset_path / 'HDDData.csv'
        if not hdd_data_path.exists():
            print(f"❌ Error: No se encontró {hdd_data_path}")
        else:
            normalized_hdds = hdd_normalizer.normalize_csv(str(hdd_data_path))
            
            # Guardar en JSON
            output_file = output_path / 'HDDData_normalized.json'
            hdd_normalizer.save_to_json(str(output_file))
            
            print(f"✅ HDDData normalizado exitosamente!")
            print(f"   - Registros procesados: {len(normalized_hdds)}")
            print(f"   - Archivo guardado en: {output_file}")
            
            # Mostrar ejemplo del primer registro
            if normalized_hdds:
                print("\n💿 Ejemplo del primer HDD normalizado:")
                print("-" * 40)
                first_hdd = normalized_hdds[0]
                print(f"Nombre: {first_hdd['name']}")
                print(f"Fabricante: {first_hdd['producer']}")
                
                # Mostrar especificaciones
                storage = first_hdd['storage_specs']
                perf = first_hdd['performance_specs']
                metrics = first_hdd['calculated_metrics']
                
                print(f"Capacidad: {storage['capacity']['value']} {storage['capacity']['unit']}")
                print(f"RPM: {perf['rpm']}")
                print(f"Caché: {perf['cache']['value']} {perf['cache']['unit']}")
                print(f"Categoría: {metrics['hdd_category']}")
                print(f"Clase rendimiento: {metrics['performance_class']}")
                print(f"Mercado objetivo: {metrics['target_market']}")
                
                if metrics['capacity_per_rpm_ratio']:
                    print(f"Ratio capacidad/RPM: {metrics['capacity_per_rpm_ratio']}")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error procesando HDDData: {e}")
        return
    
    print(f"\n🎉 Normalización completada!")
    print(f"📁 Archivos guardados en: {output_path}")


def analyze_sample_data():
    """Función para analizar una muestra de los datos normalizados"""
    print("\n🔍 Análisis de datos normalizados:")
    print("=" * 40)
    
    # Aquí podríamos añadir análisis estadísticos
    # Por ejemplo: distribución de tamaños, marcas más comunes, etc.
    pass


if __name__ == "__main__":
    main()