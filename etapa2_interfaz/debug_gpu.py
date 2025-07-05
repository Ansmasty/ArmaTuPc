#!/usr/bin/env python3

import json
import sys
import os

# Añadir la ruta del módulo filtros
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from filtros import crear_workflow_seleccion_componentes

def debug_gpu_data():
    """Debug de datos GPU"""
    try:
        # Cargar workflow
        ruta_datos = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "normalized_data"
        )
        
        workflow = crear_workflow_seleccion_componentes(ruta_datos)
        gestor = workflow['gestor_filtros']
        
        # Obtener primeras 3 GPUs
        gpus = gestor.datos.get('gpu', [])[:3]
        
        print("=== DEBUG GPU DATA ===")
        for i, gpu in enumerate(gpus):
            print(f"\n--- GPU {i+1}: {gpu.get('name', 'Sin nombre')} ---")
            
            # Performance data
            performance = gpu.get('performance', {})
            vram_info = performance.get('vram', {})
            print(f"Performance: {performance}")
            print(f"VRAM info: {vram_info}")
            if isinstance(vram_info, dict):
                print(f"VRAM value: {vram_info.get('value')}")
            
            # Physical data
            physical = gpu.get('physical', {})
            length_info = physical.get('length', {})
            print(f"Physical: {physical}")
            print(f"Length info: {length_info}")
            if isinstance(length_info, dict):
                print(f"Length value: {length_info.get('value')}")
            
            print(f"Slots: {physical.get('slots')}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gpu_data()
