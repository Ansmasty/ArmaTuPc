"""
PC Builder - Aplicación principal
Armador virtual de PCs con filtros de compatibilidad
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Importar nuestros módulos
from splash_screen import mostrar_splash_arquitectura
from main_window import PCBuilderMainWindow


class PCBuilderApp:
    """Clase principal de la aplicación PC Builder"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.arquitectura_seleccionada = None
        
    def iniciar(self):
        """Inicia la aplicación completa"""
        # Crear aplicación Qt
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PC Builder")
        self.app.setApplicationVersion("1.0")
        
        # Configurar icono si existe
        self._configurar_icono()
        
        # Mostrar splash de selección de arquitectura
        self.arquitectura_seleccionada = mostrar_splash_arquitectura()
        
        if not self.arquitectura_seleccionada:
            # Usuario canceló la selección
            return 0
            
        # Verificar datos necesarios
        if not self._verificar_datos():
            return 1
            
        # Crear y mostrar ventana principal
        try:
            self.main_window = PCBuilderMainWindow(self.arquitectura_seleccionada)
            self.main_window.show()
            
            # Ejecutar aplicación
            return self.app.exec()
            
        except Exception as e:
            QMessageBox.critical(
                None, 
                "Error Fatal", 
                f"Error iniciando la aplicación:\n{e}"
            )
            return 1
            
    def _configurar_icono(self):
        """Configura el icono de la aplicación"""
        try:
            # Intentar usar el icono de PC
            ruta_icono = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'static',
                'pc_render_icon.png'
            )
            
            if os.path.exists(ruta_icono):
                self.app.setWindowIcon(QIcon(ruta_icono))
                
        except Exception:
            # Si no se puede cargar el icono, continuar sin él
            pass
            
    def _verificar_datos(self) -> bool:
        """Verifica que los datos normalizados estén disponibles"""
        try:
            ruta_datos = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "normalized_data"
            )
            
            if not os.path.exists(ruta_datos):
                QMessageBox.critical(
                    None,
                    "Error de Datos",
                    f"No se encontró el directorio de datos normalizados:\n{ruta_datos}\n\n"
                    "Asegúrate de ejecutar primero el proceso de normalización."
                )
                return False
                
            # Verificar archivos críticos
            archivos_criticos = [
                'CPUData_normalized.json',
                'MotherboardData_normalized.json',
                'RAMData_normalized.json',
                'CaseData_normalized.json',
                'PSUData_normalized.json'
            ]
            
            archivos_faltantes = []
            for archivo in archivos_criticos:
                ruta_archivo = os.path.join(ruta_datos, archivo)
                if not os.path.exists(ruta_archivo):
                    archivos_faltantes.append(archivo)
                    
            if archivos_faltantes:
                QMessageBox.warning(
                    None,
                    "Datos Incompletos",
                    f"Faltan algunos archivos de datos:\n" + 
                    "\n".join(archivos_faltantes) +
                    "\n\nLa aplicación funcionará con datos limitados."
                )
                
            return True
            
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error de Verificación",
                f"Error verificando datos:\n{e}"
            )
            return False


def main():
    """Función principal de entrada"""
    try:
        # Configurar la aplicación para alta resolución
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            
        # Crear y ejecutar la aplicación
        app = PCBuilderApp()
        exit_code = app.iniciar()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nAplicación interrumpida por el usuario")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
