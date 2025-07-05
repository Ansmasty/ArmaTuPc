"""
Script de instalación y configuración para PC Builder
"""

import subprocess
import sys
import os


def instalar_dependencias():
    """Instala las dependencias necesarias"""
    print("🔧 Instalando dependencias para PC Builder...")
    
    # Obtener la ruta del archivo requirements.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_dir, 'requirements.txt')
    
    try:
        # Actualizar pip primero
        print("📦 Actualizando pip...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # Instalar dependencias
        print("📦 Instalando PyQt6 y dependencias...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
        
        print("✅ Dependencias instaladas correctamente!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo requirements.txt en: {requirements_path}")
        return False


def verificar_instalacion():
    """Verifica que las dependencias estén instaladas correctamente"""
    print("🔍 Verificando instalación...")
    
    dependencias = [
        ('PyQt6', 'PyQt6.QtWidgets'),
        ('PyQt6.QtCore', 'PyQt6.QtCore'),
        ('PyQt6.QtGui', 'PyQt6.QtGui'),
    ]
    
    todas_ok = True
    
    for nombre, modulo in dependencias:
        try:
            __import__(modulo)
            print(f"✅ {nombre} - OK")
        except ImportError:
            print(f"❌ {nombre} - FALTA")
            todas_ok = False
    
    return todas_ok


def ejecutar_aplicacion():
    """Ejecuta la aplicación PC Builder"""
    print("🚀 Iniciando PC Builder...")
    
    try:
        # Importar y ejecutar la aplicación
        from pc_builder_app import main
        main()
        
    except ImportError as e:
        print(f"❌ Error importando la aplicación: {e}")
        print("Asegúrate de que todos los archivos estén en el directorio correcto")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")
        return False


def main():
    """Función principal del instalador"""
    print("="*60)
    print("🖥️  PC BUILDER - INSTALADOR Y LAUNCHER")
    print("="*60)
    
    # Verificar si las dependencias ya están instaladas
    if verificar_instalacion():
        print("\n✅ Todas las dependencias están instaladas!")
        
        respuesta = input("\n¿Deseas ejecutar PC Builder ahora? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
            ejecutar_aplicacion()
        else:
            print("👋 Para ejecutar PC Builder manualmente, usa: python pc_builder_app.py")
            
    else:
        print("\n⚠️  Faltan dependencias. ¿Deseas instalarlas?")
        respuesta = input("Instalar dependencias? (s/n): ").lower().strip()
        
        if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
            if instalar_dependencias():
                print("\n🎉 Instalación completada!")
                
                respuesta = input("\n¿Deseas ejecutar PC Builder ahora? (s/n): ").lower().strip()
                if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
                    ejecutar_aplicacion()
                else:
                    print("👋 Para ejecutar PC Builder manualmente, usa: python pc_builder_app.py")
            else:
                print("\n❌ Error en la instalación. Revisa los mensajes de error arriba.")
        else:
            print("\n👋 Instalación cancelada.")
            print("Para instalar manualmente: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
