#!/usr/bin/env python3
"""
Analizador Avanzado de Dataset Normalizado
==========================================

Este script demuestra las capacidades analíticas avanzadas del dataset normalizado,
realizando análisis matemáticos, térmicos y de compatibilidad entre componentes.

Autor: Sistema de Normalización
Fecha: 2025-07-03
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics
from collections import Counter, defaultdict

class AdvancedDatasetAnalyzer:
    """Analizador avanzado para el dataset normalizado"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.datasets = {}
        self.load_all_datasets()
    
    def load_all_datasets(self):
        """Carga todos los datasets normalizados"""
        dataset_files = {
            'cases': 'CaseData_normalized.json',
            'cpu_coolers': 'CPUCoolerData_normalized.json',
            'cpus': 'CPUData_normalized.json',
            'gpus': 'GPUData_normalized.json',
            'hdds': 'HDDData_normalized.json',
            'motherboards': 'MotherboardData_normalized.json',
            'psus': 'PSUData_normalized.json',
            'ram': 'RAMData_normalized.json',
            'ssds': 'SSDData_normalized.json'
        }
        
        for category, filename in dataset_files.items():
            file_path = self.data_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.datasets[category] = json.load(f)
                print(f"✅ Cargado {category}: {len(self.datasets[category])} componentes")
            else:
                print(f"❌ No encontrado: {filename}")
    
    def analyze_thermal_compatibility(self):
        """Análisis de compatibilidad térmica CPU-Cooler"""
        print("\n🌡️  ANÁLISIS DE COMPATIBILIDAD TÉRMICA")
        print("=" * 50)
        
        if 'cpus' not in self.datasets or 'cpu_coolers' not in self.datasets:
            print("❌ Datos de CPU o Coolers no disponibles")
            return
        
        # Estadísticas de TDP de CPUs
        cpu_tdps = [cpu.get('architecture', {}).get('tdp', {}).get('value', 0) 
                   for cpu in self.datasets['cpus'] if cpu.get('architecture', {}).get('tdp', {}).get('value')]
        
        # Estadísticas de TDP de Coolers
        cooler_tdps = [cooler.get('thermal_performance', {}).get('tdp', {}).get('value', 0) 
                      for cooler in self.datasets['cpu_coolers'] if cooler.get('thermal_performance', {}).get('tdp', {}).get('value')]
        
        if not cpu_tdps:
            print("❌ No se encontraron datos de TDP de CPUs")
            return
        
        if not cooler_tdps:
            print("❌ No se encontraron datos de TDP de Coolers")
            print("📊 Solo estadísticas TDP de CPUs:")
            print(f"   - Promedio: {statistics.mean(cpu_tdps):.1f}W")
            print(f"   - Mediana: {statistics.median(cpu_tdps):.1f}W")
            print(f"   - Rango: {min(cpu_tdps):.1f}W - {max(cpu_tdps):.1f}W")
            return
        
        print(f"📊 Estadísticas TDP de CPUs:")
        print(f"   - Promedio: {statistics.mean(cpu_tdps):.1f}W")
        print(f"   - Mediana: {statistics.median(cpu_tdps):.1f}W")
        print(f"   - Rango: {min(cpu_tdps):.1f}W - {max(cpu_tdps):.1f}W")
        
        print(f"\n📊 Estadísticas TDP de Coolers:")
        print(f"   - Promedio: {statistics.mean(cooler_tdps):.1f}W")
        print(f"   - Mediana: {statistics.median(cooler_tdps):.1f}W")
        print(f"   - Rango: {min(cooler_tdps):.1f}W - {max(cooler_tdps):.1f}W")
        
        # Análisis de compatibilidad
        compatible_pairs = 0
        total_pairs = 0
        
        for cpu in self.datasets['cpus']:
            cpu_tdp = cpu.get('architecture', {}).get('tdp', {}).get('value', 0)
            cpu_socket = cpu.get('architecture', {}).get('socket', '')
            
            for cooler in self.datasets['cpu_coolers']:
                cooler_tdp = cooler.get('thermal_specs', {}).get('tdp', {}).get('value', 0)
                
                # Verificar compatibilidad de socket
                socket_compatible = False
                compatibility = cooler.get('compatibility', {})
                if compatibility.get('universal', False):
                    socket_compatible = True
                else:
                    intel_sockets = compatibility.get('intel_sockets', [])
                    amd_sockets = compatibility.get('amd_sockets', [])
                    if cpu_socket in intel_sockets or cpu_socket in amd_sockets:
                        socket_compatible = True
                
                # Verificar compatibilidad térmica (cooler debe manejar al menos el TDP del CPU)
                thermal_compatible = cooler_tdp >= cpu_tdp
                
                if socket_compatible and thermal_compatible and cpu_tdp > 0 and cooler_tdp > 0:
                    compatible_pairs += 1
                
                if cpu_tdp > 0 and cooler_tdp > 0:
                    total_pairs += 1
        
        compatibility_rate = (compatible_pairs / total_pairs * 100) if total_pairs > 0 else 0
        print(f"\n🔗 Compatibilidad general:")
        print(f"   - Pares compatibles: {compatible_pairs:,}")
        print(f"   - Total evaluado: {total_pairs:,}")
        print(f"   - Tasa de compatibilidad: {compatibility_rate:.1f}%")
    
    def analyze_system_power_requirements(self):
        """Análisis de requerimientos de potencia del sistema"""
        print("\n⚡ ANÁLISIS DE REQUERIMIENTOS DE POTENCIA")
        print("=" * 50)
        
        if 'gpus' not in self.datasets or 'psus' not in self.datasets:
            print("❌ Datos de GPU o PSU no disponibles")
            return
        
        # Distribución de TDP de GPUs
        gpu_tdps = [gpu.get('performance', {}).get('tdp', {}).get('value', 0) 
                   for gpu in self.datasets['gpus'] if gpu.get('performance', {}).get('tdp', {}).get('value')]
        
        # Distribución de potencia de PSUs
        psu_powers = [psu.get('power', {}).get('wattage', {}).get('value', 0) 
                     for psu in self.datasets['psus'] if psu.get('power', {}).get('wattage', {}).get('value')]
        
        print(f"📊 Estadísticas TDP de GPUs:")
        print(f"   - Promedio: {statistics.mean(gpu_tdps):.1f}W")
        print(f"   - Percentil 90: {sorted(gpu_tdps)[int(len(gpu_tdps) * 0.9)]:.1f}W")
        print(f"   - GPU más potente: {max(gpu_tdps):.1f}W")
        
        print(f"\n📊 Estadísticas de PSUs:")
        print(f"   - Promedio: {statistics.mean(psu_powers):.1f}W")
        print(f"   - Mediana: {statistics.median(psu_powers):.1f}W")
        print(f"   - Rango: {min(psu_powers):.1f}W - {max(psu_powers):.1f}W")
        
        # Categorizar sistemas por requerimiento de potencia
        power_categories = {
            'office': 300,
            'budget_gaming': 500,
            'mainstream_gaming': 650,
            'high_end_gaming': 850,
            'enthusiast': 1000,
            'extreme': 1200
        }
        
        print(f"\n🎯 Análisis de categorías de sistemas:")
        for category, min_power in power_categories.items():
            suitable_psus = len([psu for psu in psu_powers if psu >= min_power])
            total_psus = len(psu_powers)
            percentage = (suitable_psus / total_psus * 100) if total_psus > 0 else 0
            print(f"   - {category.replace('_', ' ').title()}: {suitable_psus}/{total_psus} PSUs ({percentage:.1f}%)")
    
    def analyze_memory_trends(self):
        """Análisis de tendencias en memoria RAM"""
        print("\n💾 ANÁLISIS DE TENDENCIAS DE MEMORIA")
        print("=" * 50)
        
        if 'ram' not in self.datasets:
            print("❌ Datos de RAM no disponibles")
            return
        
        # Distribución por generación DDR
        ddr_generations = [ram.get('memory_specs', {}).get('ram_type', {}).get('generation', 'Unknown') 
                          for ram in self.datasets['ram']]
        ddr_counts = Counter(ddr_generations)
        
        print("📊 Distribución por generación DDR:")
        for generation, count in sorted(ddr_counts.items()):
            percentage = (count / len(ddr_generations) * 100) if ddr_generations else 0
            print(f"   - {generation}: {count:,} módulos ({percentage:.1f}%)")
        
        # Distribución de capacidades
        capacities = [ram.get('memory_specs', {}).get('capacity', {}).get('value', 0) 
                     for ram in self.datasets['ram'] if ram.get('memory_specs', {}).get('capacity', {}).get('value')]
        
        capacity_ranges = {
            '4GB': len([c for c in capacities if c <= 4]),
            '8GB': len([c for c in capacities if 4 < c <= 8]),
            '16GB': len([c for c in capacities if 8 < c <= 16]),
            '32GB': len([c for c in capacities if 16 < c <= 32]),
            '64GB+': len([c for c in capacities if c > 32])
        }
        
        print(f"\n📊 Distribución de capacidades:")
        total_modules = sum(capacity_ranges.values())
        for range_name, count in capacity_ranges.items():
            percentage = (count / total_modules * 100) if total_modules > 0 else 0
            print(f"   - {range_name}: {count:,} módulos ({percentage:.1f}%)")
        
        # Análisis de frecuencias
        frequencies = [ram.get('memory_specs', {}).get('frequency', {}).get('value', 0) 
                      for ram in self.datasets['ram'] if ram.get('memory_specs', {}).get('frequency', {}).get('value')]
        
        if frequencies:
            print(f"\n📊 Estadísticas de frecuencias:")
            print(f"   - Frecuencia promedio: {statistics.mean(frequencies):.0f} MHz")
            print(f"   - Frecuencia mediana: {statistics.median(frequencies):.0f} MHz")
            print(f"   - Rango: {min(frequencies):.0f} - {max(frequencies):.0f} MHz")
    
    def analyze_storage_evolution(self):
        """Análisis de evolución del almacenamiento SSD vs HDD"""
        print("\n💽 ANÁLISIS DE EVOLUCIÓN DEL ALMACENAMIENTO")
        print("=" * 50)
        
        if 'ssds' not in self.datasets or 'hdds' not in self.datasets:
            print("❌ Datos de SSD o HDD no disponibles")
            return
        
        ssd_count = len(self.datasets['ssds'])
        hdd_count = len(self.datasets['hdds'])
        total_storage = ssd_count + hdd_count
        
        print(f"📊 Distribución del mercado de almacenamiento:")
        print(f"   - SSDs: {ssd_count:,} modelos ({ssd_count/total_storage*100:.1f}%)")
        print(f"   - HDDs: {hdd_count:,} modelos ({hdd_count/total_storage*100:.1f}%)")
        
        # Análisis de capacidades SSD
        ssd_capacities = [ssd.get('storage_specs', {}).get('capacity', {}).get('gb_equivalent', 0) 
                         for ssd in self.datasets['ssds'] if ssd.get('storage_specs', {}).get('capacity', {}).get('gb_equivalent')]
        
        # Análisis de capacidades HDD
        hdd_capacities = [hdd.get('storage_specs', {}).get('capacity', {}).get('gb_equivalent', 0) 
                         for hdd in self.datasets['hdds'] if hdd.get('storage_specs', {}).get('capacity', {}).get('gb_equivalent')]
        
        if ssd_capacities and hdd_capacities:
            print(f"\n📊 Comparativa de capacidades:")
            print(f"   SSD - Promedio: {statistics.mean(ssd_capacities):.0f} GB, Máximo: {max(ssd_capacities):.0f} GB")
            print(f"   HDD - Promedio: {statistics.mean(hdd_capacities):.0f} GB, Máximo: {max(hdd_capacities):.0f} GB")
        
        # Análisis de factores de forma SSD
        ssd_form_factors = [ssd.get('storage_specs', {}).get('form_factor', 'Unknown') 
                           for ssd in self.datasets['ssds']]
        ff_counts = Counter(ssd_form_factors)
        
        print(f"\n📊 Factores de forma SSD:")
        for ff, count in sorted(ff_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(ssd_form_factors) * 100) if ssd_form_factors else 0
            print(f"   - {ff}: {count:,} modelos ({percentage:.1f}%)")
    
    def analyze_gpu_performance_tiers(self):
        """Análisis de niveles de rendimiento de GPUs"""
        print("\n🎮 ANÁLISIS DE NIVELES DE RENDIMIENTO GPU")
        print("=" * 50)
        
        if 'gpus' not in self.datasets:
            print("❌ Datos de GPU no disponibles")
            return
        
        # Distribución por categorías
        gpu_categories = [gpu.get('calculated_metrics', {}).get('gpu_category', 'unknown') 
                         for gpu in self.datasets['gpus']]
        category_counts = Counter(gpu_categories)
        
        print("📊 Distribución por categorías de rendimiento:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(gpu_categories) * 100) if gpu_categories else 0
            print(f"   - {category.replace('_', ' ').title()}: {count:,} GPUs ({percentage:.1f}%)")
        
        # Análisis de VRAM
        vram_sizes = [gpu.get('performance', {}).get('vram', {}).get('value', 0) 
                     for gpu in self.datasets['gpus'] if gpu.get('performance', {}).get('vram', {}).get('value')]
        
        vram_distribution = Counter(vram_sizes)
        
        print(f"\n📊 Distribución de VRAM:")
        for vram, count in sorted(vram_distribution.items()):
            percentage = (count / len(vram_sizes) * 100) if vram_sizes else 0
            print(f"   - {vram:.0f} GB: {count:,} GPUs ({percentage:.1f}%)")
        
        # Performance scores
        performance_scores = [gpu.get('calculated_metrics', {}).get('performance_score', 0) 
                            for gpu in self.datasets['gpus'] if gpu.get('calculated_metrics', {}).get('performance_score')]
        
        if performance_scores:
            print(f"\n📊 Estadísticas de rendimiento:")
            print(f"   - Puntuación promedio: {statistics.mean(performance_scores):.0f}")
            print(f"   - Mediana: {statistics.median(performance_scores):.0f}")
            print(f"   - GPU más potente: {max(performance_scores):.0f} puntos")
    
    def generate_compatibility_matrix(self):
        """Genera matriz básica de compatibilidad entre componentes"""
        print("\n🔗 MATRIZ DE COMPATIBILIDAD DE COMPONENTES")
        print("=" * 50)
        
        # Compatibilidad CPU-Motherboard por socket
        if 'cpus' in self.datasets and 'motherboards' in self.datasets:
            cpu_sockets = set(cpu.get('architecture', {}).get('socket', '') 
                            for cpu in self.datasets['cpus'] if cpu.get('architecture', {}).get('socket'))
            mb_sockets = set(mb.get('motherboard_specs', {}).get('socket', '') 
                           for mb in self.datasets['motherboards'] if mb.get('motherboard_specs', {}).get('socket'))
            
            common_sockets = cpu_sockets.intersection(mb_sockets)
            
            print(f"🔌 Compatibilidad CPU-Motherboard:")
            print(f"   - Sockets de CPU únicos: {len(cpu_sockets)}")
            print(f"   - Sockets de Motherboard únicos: {len(mb_sockets)}")
            print(f"   - Sockets compatibles: {len(common_sockets)}")
            print(f"   - Sockets: {', '.join(sorted(common_sockets)[:10])}{'...' if len(common_sockets) > 10 else ''}")
        
        # Compatibilidad RAM-Motherboard por tipo DDR
        if 'ram' in self.datasets and 'motherboards' in self.datasets:
            ram_types = set(ram.get('memory_specs', {}).get('ram_type', {}).get('generation', '') 
                          for ram in self.datasets['ram'] if ram.get('memory_specs', {}).get('ram_type', {}).get('generation'))
            mb_ram_types = set(mb.get('memory_specs', {}).get('memory_type', '') 
                             for mb in self.datasets['motherboards'] if mb.get('memory_specs', {}).get('memory_type'))
            
            print(f"\n💾 Compatibilidad RAM-Motherboard:")
            print(f"   - Tipos RAM disponibles: {', '.join(sorted(ram_types))}")
            print(f"   - Tipos soportados por MB: {', '.join(sorted(mb_ram_types))}")
    
    def run_complete_analysis(self):
        """Ejecuta análisis completo del dataset"""
        print("🔬 ANÁLISIS AVANZADO DEL DATASET NORMALIZADO")
        print("=" * 60)
        print(f"Ruta de datos: {self.data_path}")
        print(f"Total de categorías cargadas: {len(self.datasets)}")
        
        total_components = sum(len(dataset) for dataset in self.datasets.values())
        print(f"Total de componentes: {total_components:,}")
        
        # Ejecutar todos los análisis
        self.analyze_thermal_compatibility()
        self.analyze_system_power_requirements()
        self.analyze_memory_trends()
        self.analyze_storage_evolution()
        self.analyze_gpu_performance_tiers()
        self.generate_compatibility_matrix()
        
        print(f"\n🎉 Análisis completo finalizado!")
        print("=" * 60)


def main():
    """Función principal"""
    base_path = Path(__file__).parent.parent
    data_path = base_path / 'normalized_data'
    
    if not data_path.exists():
        print(f"❌ Error: Directorio de datos no encontrado: {data_path}")
        return
    
    analyzer = AdvancedDatasetAnalyzer(str(data_path))
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()
