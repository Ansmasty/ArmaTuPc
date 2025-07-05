"""
Splash Screen para selección de arquitectura inicial
Modulo independiente para mantener la separación de responsabilidades
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QWidget, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor, QIcon
from typing import Optional


class SplashArquitectura(QDialog):
    """
    Splash Screen para selección de arquitectura (AMD vs Intel)
    """
    
    # Señal emitida cuando se selecciona una arquitectura
    arquitectura_seleccionada = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.arquitectura_elegida = None
        self.ruta_static = self._obtener_ruta_static()
        self.setupUI()
        self.setupStyles()
        
    def _obtener_ruta_static(self) -> str:
        """Obtiene la ruta del directorio static"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, 'static')
        
    def setupUI(self):
        """Configura la interfaz del splash"""
        # Configurar ventana
        self.setFixedSize(600, 400)
        self.setWindowTitle("PC Builder")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("PC Builder - Selecciona tu Arquitectura")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Elige la arquitectura de CPU para comenzar a armar tu PC")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setObjectName("subtitle")
        layout.addWidget(subtitle_label)
        
        # Contenedor de botones
        buttons_frame = QFrame()
        buttons_frame.setObjectName("buttonsFrame")
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(40)
        
        # Botón AMD
        self.btn_amd = self._crear_boton_arquitectura(
            "AMD", 
            "amd_logo_render_icon.png",
            "#ED1C24"  # Rojo AMD
        )
        buttons_layout.addWidget(self.btn_amd)
        
        # Botón Intel
        self.btn_intel = self._crear_boton_arquitectura(
            "Intel", 
            "intel_logo_render_icon.png",
            "#0071C5"  # Azul Intel
        )
        buttons_layout.addWidget(self.btn_intel)
        
        layout.addWidget(buttons_frame)
        
        # Información adicional
        info_label = QLabel("Esta selección determinará los componentes compatibles disponibles")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setObjectName("info")
        layout.addWidget(info_label)
        
        # Botón de salir
        btn_salir = QPushButton("Salir")
        btn_salir.setObjectName("exitButton")
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir)
        
    def _crear_boton_arquitectura(self, texto: str, imagen: str, color_hover: str) -> QPushButton:
        """
        Crea un botón estilizado para selección de arquitectura
        
        Args:
            texto: Texto del botón (AMD/Intel)
            imagen: Nombre del archivo de imagen
            color_hover: Color para el efecto hover
        """
        boton = QPushButton()
        boton.setFixedSize(200, 150)
        boton.setObjectName(f"btn{texto}")
        
        # Layout interno del botón
        layout = QVBoxLayout(boton)
        layout.setSpacing(10)
        
        # Imagen/Logo
        ruta_imagen = os.path.join(self.ruta_static, imagen)
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            # Escalar manteniendo proporción
            pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, 
                                 Qt.TransformationMode.SmoothTransformation)
            
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(img_label)
        
        # Texto
        text_label = QLabel(texto)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setObjectName(f"text{texto}")
        layout.addWidget(text_label)
        
        # Conectar evento
        boton.clicked.connect(lambda: self._seleccionar_arquitectura(texto))
        
        return boton
        
    def _seleccionar_arquitectura(self, arquitectura: str):
        """
        Maneja la selección de arquitectura
        
        Args:
            arquitectura: Arquitectura seleccionada (AMD/Intel)
        """
        self.arquitectura_elegida = arquitectura
        
        # Efecto visual de selección
        self._mostrar_seleccion(arquitectura)
        
        # Emitir señal después de un breve delay para mostrar el efecto
        QTimer.singleShot(500, lambda: self._confirmar_seleccion(arquitectura))
        
    def _mostrar_seleccion(self, arquitectura: str):
        """Muestra efecto visual de selección"""
        # Deshabilitar ambos botones
        self.btn_amd.setEnabled(False)
        self.btn_intel.setEnabled(False)
        
        # Aplicar estilo de seleccionado
        if arquitectura == "AMD":
            self.btn_amd.setObjectName("btnAMDSelected")
        else:
            self.btn_intel.setObjectName("btnIntelSelected")
            
        # Reaplicar estilos
        self.btn_amd.style().unpolish(self.btn_amd)
        self.btn_amd.style().polish(self.btn_amd)
        self.btn_intel.style().unpolish(self.btn_intel)
        self.btn_intel.style().polish(self.btn_intel)
        
    def _confirmar_seleccion(self, arquitectura: str):
        """Confirma la selección y cierra el splash"""
        self.arquitectura_seleccionada.emit(arquitectura)
        self.close()
        
    def setupStyles(self):
        """Configura los estilos CSS del splash"""
        style = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QLabel#title {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 10px;
        }
        
        QLabel#subtitle {
            font-size: 14px;
            color: #cccccc;
            margin-bottom: 20px;
        }
        
        QLabel#info {
            font-size: 11px;
            color: #999999;
            margin-top: 20px;
        }
        
        QFrame#buttonsFrame {
            background-color: transparent;
        }
        
        QPushButton#btnAMD, QPushButton#btnIntel {
            background-color: #404040;
            border: 2px solid #555555;
            border-radius: 15px;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
        }
        
        QPushButton#btnAMD:hover {
            border-color: #ED1C24;
            background-color: #4a3030;
        }
        
        QPushButton#btnIntel:hover {
            border-color: #0071C5;
            background-color: #304050;
        }
        
        QPushButton#btnAMDSelected {
            background-color: #ED1C24;
            border-color: #ffffff;
            color: #ffffff;
        }
        
        QPushButton#btnIntelSelected {
            background-color: #0071C5;
            border-color: #ffffff;
            color: #ffffff;
        }
        
        QLabel#textAMD, QLabel#textIntel {
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
        }
        
        QPushButton#exitButton {
            background-color: #505050;
            border: 1px solid #707070;
            border-radius: 5px;
            color: #ffffff;
            font-size: 12px;
            padding: 8px 16px;
            max-width: 100px;
        }
        
        QPushButton#exitButton:hover {
            background-color: #606060;
        }
        
        QPushButton#exitButton:pressed {
            background-color: #404040;
        }
        """
        
        self.setStyleSheet(style)
        
    def get_arquitectura_seleccionada(self) -> Optional[str]:
        """
        Retorna la arquitectura seleccionada
        
        Returns:
            Arquitectura seleccionada o None si no se seleccionó nada
        """
        return self.arquitectura_elegida


def mostrar_splash_arquitectura() -> Optional[str]:
    """
    Función helper para mostrar el splash y retornar la selección
    
    Returns:
        Arquitectura seleccionada o None si se canceló
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    splash = SplashArquitectura()
    
    # Variable para capturar la selección
    arquitectura_resultado = [None]
    
    def on_arquitectura_seleccionada(arq):
        arquitectura_resultado[0] = arq
        app.quit()
    
    splash.arquitectura_seleccionada.connect(on_arquitectura_seleccionada)
    
    # Mostrar splash centrado
    splash.show()
    
    # Centrar en pantalla
    screen = app.primaryScreen().geometry()
    splash_geo = splash.geometry()
    x = (screen.width() - splash_geo.width()) // 2
    y = (screen.height() - splash_geo.height()) // 2
    splash.move(x, y)
    
    # Ejecutar hasta que se seleccione algo o se cierre
    app.exec()
    
    return arquitectura_resultado[0]


# Ejemplo de uso independiente
if __name__ == "__main__":
    arquitectura = mostrar_splash_arquitectura()
    
    if arquitectura:
        print(f"Arquitectura seleccionada: {arquitectura}")
    else:
        print("No se seleccionó ninguna arquitectura")
