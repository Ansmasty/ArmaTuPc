"""
Módulo para manejo de base de datos de componentes
"""

import json
from typing import Dict, List, Optional
from main import OptimizadorPC, Componente, Gabinete, CPU, GPU, FuentePoder

class GestorBaseDatos:
    """Maneja la base de datos de componentes con funcionalidades avanzadas"""
    
    def __init__(self, archivo_json: str = "data.json"):
        self.archivo = archivo_json
        self.optimizador = OptimizadorPC(archivo_json)
        self.datos = self.optimizador.componentes_disponibles
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal de gestión"""
        while True:
            print("\n" + "="*50)
            print("🗃️  GESTOR DE BASE DE DATOS - COMPONENTES PC")
            print("="*50)
            print("1. 📋 Ver componentes por categoría")
            print("2. ➕ Agregar nuevo componente")
            print("3. 🔍 Buscar componentes")
            print("4. 📊 Estadísticas de la base de datos")
            print("5. 🧹 Limpiar/Resetear base de datos")
            print("6. 💾 Exportar/Importar datos")
            print("7. ✅ Validar integridad de datos")
            print("0. 🚪 Salir")
            print("-"*50)
            
            try:
                opcion = input("Selecciona una opción: ").strip()
                
                if opcion == "1":
                    self.mostrar_componentes_por_categoria()
                elif opcion == "2":
                    self.agregar_componente_interactivo()
                elif opcion == "3":
                    self.buscar_componentes_interactivo()
                elif opcion == "4":
                    self.mostrar_estadisticas()
                elif opcion == "5":
                    self.limpiar_base_datos()
                elif opcion == "6":
                    self.menu_exportar_importar()
                elif opcion == "7":
                    self.validar_integridad()
                elif opcion == "0":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida. Intenta de nuevo.")
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def mostrar_componentes_por_categoria(self):
        """Muestra componentes organizados por categoría"""
        print("\n📋 COMPONENTES POR CATEGORÍA")
        print("-"*40)
        
        for categoria, componentes in self.datos.items():
            print(f"\n🔧 {categoria.upper().replace('_', ' ')} ({len(componentes)} items):")
            if componentes:
                for i, comp in enumerate(componentes, 1):
                    precio = comp.get('precio', 0)
                    consumo = comp.get('consumo_watts', 0)
                    print(f"  {i}. {comp['nombre']} - ${precio} - {consumo}W")
            else:
                print("  (Sin componentes)")
    
    def agregar_componente_interactivo(self):
        """Agrega un componente de forma interactiva"""
        print("\n➕ AGREGAR NUEVO COMPONENTE")
        print("-"*30)
        
        # Seleccionar categoría
        categorias = list(self.datos.keys())
        print("Categorías disponibles:")
        for i, cat in enumerate(categorias, 1):
            print(f"  {i}. {cat.replace('_', ' ').title()}")
        
        try:
            idx_cat = int(input("Selecciona categoría (número): ")) - 1
            if idx_cat < 0 or idx_cat >= len(categorias):
                print("❌ Categoría inválida")
                return
            
            categoria = categorias[idx_cat]
            
            # Datos básicos del componente
            nombre = input("Nombre del componente: ").strip()
            if not nombre:
                print("❌ El nombre es obligatorio")
                return
            
            precio = float(input("Precio ($): "))
            consumo = float(input("Consumo en watts: "))
            marca = input("Marca: ").strip()
            
            # Dimensiones
            print("Dimensiones (en mm):")
            largo = float(input("  Largo: "))
            ancho = float(input("  Ancho: "))
            alto = float(input("  Alto: "))
            
            # Datos específicos según categoría
            componente_data = {
                'nombre': nombre,
                'precio': precio,
                'consumo_watts': consumo,
                'dimensiones': [largo, ancho, alto],
                'marca': marca
            }
            
            # Agregar campos específicos según categoría
            if categoria == 'gabinetes':
                volumen_interno = float(input("Volumen interno (mm³): "))
                tipo = input("Tipo (ATX/Micro-ATX/Mini-ITX): ").strip()
                componente_data.update({
                    'volumen_interno': volumen_interno,
                    'tipo': tipo
                })
            
            elif categoria == 'cpus':
                socket = input("Socket: ").strip()
                cores = int(input("Número de cores: "))
                frecuencia = float(input("Frecuencia base (GHz): "))
                tdp = float(input("TDP (watts): "))
                componente_data.update({
                    'socket': socket,
                    'cores': cores,
                    'frecuencia_base': frecuencia,
                    'tdp': tdp
                })
            
            elif categoria == 'gpus':
                vram = int(input("VRAM (GB): "))
                tdp = float(input("TDP (watts): "))
                conectores = input("Conectores de poder (ej: 8pin,6pin): ").strip().split(',')
                componente_data.update({
                    'vram': vram,
                    'tdp': tdp,
                    'conectores_power': [c.strip() for c in conectores if c.strip()]
                })
            
            elif categoria == 'fuentes':
                vatios_max = int(input("Potencia máxima (W): "))
                eficiencia = float(input("Eficiencia (0.0-1.0): "))
                certificacion = input("Certificación (ej: 80+ Bronze): ").strip()
                componente_data.update({
                    'vatios_max': vatios_max,
                    'eficiencia': eficiencia,
                    'certificacion': certificacion
                })
            
            # Agregar a la base de datos
            self.datos[categoria].append(componente_data)
            self.guardar_datos()
            
            print(f"✅ Componente '{nombre}' agregado exitosamente a {categoria}")
            
        except ValueError:
            print("❌ Error: Valor numérico inválido")
        except Exception as e:
            print(f"❌ Error al agregar componente: {e}")
    
    def buscar_componentes_interactivo(self):
        """Busca componentes con filtros"""
        print("\n🔍 BÚSQUEDA DE COMPONENTES")
        print("-"*30)
        
        categoria = input("Categoría (enter para todas): ").strip().lower()
        precio_max = input("Precio máximo (enter para sin límite): ").strip()
        marca_filtro = input("Marca (enter para todas): ").strip().lower()
        
        resultados = []
        categorias_buscar = [categoria] if categoria in self.datos else self.datos.keys()
        
        for cat in categorias_buscar:
            for comp in self.datos[cat]:
                # Aplicar filtros
                if precio_max and comp.get('precio', 0) > float(precio_max):
                    continue
                if marca_filtro and marca_filtro not in comp.get('marca', '').lower():
                    continue
                
                resultados.append((cat, comp))
        
        print(f"\n📊 {len(resultados)} resultados encontrados:")
        for cat, comp in resultados[:20]:  # Mostrar máximo 20
            precio = comp.get('precio', 0)
            print(f"  [{cat.upper()}] {comp['nombre']} - ${precio} ({comp.get('marca', 'N/A')})")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de la base de datos"""
        print("\n📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("-"*40)
        
        total_componentes = sum(len(comps) for comps in self.datos.values())
        print(f"📦 Total de componentes: {total_componentes}")
        
        # Estadísticas por categoría
        for categoria, componentes in self.datos.items():
            if componentes:
                precios = [c.get('precio', 0) for c in componentes]
                consumos = [c.get('consumo_watts', 0) for c in componentes]
                
                print(f"\n🔧 {categoria.upper()}:")
                print(f"   Cantidad: {len(componentes)}")
                print(f"   Precio promedio: ${sum(precios)/len(precios):.2f}")
                print(f"   Rango de precios: ${min(precios):.2f} - ${max(precios):.2f}")
                if any(consumos):
                    print(f"   Consumo promedio: {sum(consumos)/len(consumos):.1f}W")
        
        # Marcas más comunes
        marcas = {}
        for componentes in self.datos.values():
            for comp in componentes:
                marca = comp.get('marca', 'N/A')
                marcas[marca] = marcas.get(marca, 0) + 1
        
        if marcas:
            print(f"\n🏷️  Top 5 marcas:")
            for marca, cantidad in sorted(marcas.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {marca}: {cantidad} componentes")
    
    def validar_integridad(self):
        """Valida la integridad de los datos"""
        print("\n✅ VALIDACIÓN DE INTEGRIDAD")
        print("-"*30)
        
        errores = []
        warnings = []
        
        for categoria, componentes in self.datos.items():
            for i, comp in enumerate(componentes):
                # Campos obligatorios
                campos_requeridos = ['nombre', 'precio', 'consumo_watts', 'dimensiones', 'marca']
                for campo in campos_requeridos:
                    if campo not in comp:
                        errores.append(f"{categoria}[{i}]: Falta campo '{campo}'")
                
                # Validaciones específicas
                if comp.get('precio', 0) < 0:
                    errores.append(f"{categoria}[{i}]: Precio negativo")
                
                if comp.get('consumo_watts', 0) < 0:
                    warnings.append(f"{categoria}[{i}]: Consumo negativo (¿es correcto?)")
                
                dimensiones = comp.get('dimensiones', [])
                if not isinstance(dimensiones, list) or len(dimensiones) != 3:
                    errores.append(f"{categoria}[{i}]: Dimensiones inválidas")
        
        if errores:
            print(f"❌ {len(errores)} errores encontrados:")
            for error in errores[:10]:  # Mostrar máximo 10
                print(f"   {error}")
        
        if warnings:
            print(f"⚠️  {len(warnings)} advertencias:")
            for warning in warnings[:5]:  # Mostrar máximo 5
                print(f"   {warning}")
        
        if not errores and not warnings:
            print("✅ Base de datos íntegra - No se encontraron problemas")
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
            print(f"💾 Datos guardados en {self.archivo}")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
    
    def limpiar_base_datos(self):
        """Limpia o resetea la base de datos"""
        print("\n🧹 LIMPIAR BASE DE DATOS")
        print("-"*25)
        print("⚠️  ADVERTENCIA: Esta acción no se puede deshacer")
        
        confirmacion = input("¿Estás seguro? (escribe 'CONFIRMAR'): ")
        if confirmacion == 'CONFIRMAR':
            self.datos = {
                'gabinetes': [],
                'placas_base': [],
                'cpus': [],
                'gpus': [],
                'rams': [],
                'fuentes': []
            }
            self.guardar_datos()
            print("✅ Base de datos limpiada")
        else:
            print("❌ Operación cancelada")
    
    def menu_exportar_importar(self):
        """Menú para exportar/importar datos"""
        print("\n💾 EXPORTAR/IMPORTAR DATOS")
        print("-"*25)
        print("1. Exportar a archivo de respaldo")
        print("2. Importar desde archivo")
        print("0. Volver")
        
        opcion = input("Opción: ").strip()
        
        if opcion == "1":
            nombre_archivo = input("Nombre del archivo de respaldo: ").strip()
            if not nombre_archivo.endswith('.json'):
                nombre_archivo += '.json'
            
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.datos, f, indent=2, ensure_ascii=False)
                print(f"✅ Datos exportados a {nombre_archivo}")
            except Exception as e:
                print(f"❌ Error al exportar: {e}")
        
        elif opcion == "2":
            nombre_archivo = input("Nombre del archivo a importar: ").strip()
            try:
                with open(nombre_archivo, 'r', encoding='utf-8') as f:
                    datos_importados = json.load(f)
                
                print("⚠️  Esto sobrescribirá los datos actuales")
                if input("¿Continuar? (s/n): ").lower() == 's':
                    self.datos = datos_importados
                    self.guardar_datos()
                    print(f"✅ Datos importados desde {nombre_archivo}")
                else:
                    print("❌ Importación cancelada")
            except FileNotFoundError:
                print(f"❌ Archivo {nombre_archivo} no encontrado")
            except Exception as e:
                print(f"❌ Error al importar: {e}")

def main():
    """Función principal para gestión de base de datos"""
    print("🗃️  Iniciando Gestor de Base de Datos...")
    gestor = GestorBaseDatos("data.json")
    gestor.mostrar_menu_principal()

if __name__ == "__main__":
    main()