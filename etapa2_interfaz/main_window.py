"""
Ventana principal del PC Builder
Interface modular para armado virtual de PC
"""

import sys
import os
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QGroupBox, QScrollArea,
    QListWidget, QListWidgetItem, QRadioButton, QButtonGroup,
    QFrame, QTextEdit, QProgressBar, QMessageBox, QSplitter,
    QTabWidget, QCheckBox, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

# Importar nuestros módulos
from filtros import crear_workflow_seleccion_componentes, formatear_componente_para_ui
from splash_screen import mostrar_splash_arquitectura

# Importar las nuevas pestañas de análisis matemático
try:
    from interfaces.analisis_tab import AnalisisMatematicoTab
    from interfaces.optimizacion_tab import OptimizacionTab
    PESTANAS_MATEMATICAS_DISPONIBLES = True
except ImportError as e:
    print(f"Pestañas de análisis matemático no disponibles: {e}")
    PESTANAS_MATEMATICAS_DISPONIBLES = False


class ComponenteWidget(QFrame):
    """Widget personalizado para mostrar un componente"""
    
    componente_seleccionado = pyqtSignal(dict, str)  # componente, tipo
    
    def __init__(self, componente_data: Dict, tipo_componente: str):
        super().__init__()
        self.componente_data = componente_data
        self.tipo_componente = tipo_componente
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la UI del widget de componente"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setObjectName("componenteWidget")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Nombre del componente
        nombre_label = QLabel(self.componente_data.get('nombre', 'Sin nombre'))
        nombre_label.setObjectName("componenteNombre")
        nombre_label.setWordWrap(True)
        layout.addWidget(nombre_label)
        
        # Fabricante
        fabricante_label = QLabel(f"Fabricante: {self.componente_data.get('fabricante', 'N/A')}")
        fabricante_label.setObjectName("componenteFabricante")
        layout.addWidget(fabricante_label)
        
        # Información específica por tipo
        self._agregar_info_especifica(layout)
        
    def _agregar_info_especifica(self, layout):
        """Agrega información específica según el tipo de componente"""
        if self.tipo_componente == 'cpu':
            specs = f"{self.componente_data.get('cores', 0)}C/{self.componente_data.get('threads', 0)}T - {self.componente_data.get('tdp', 0)}W"
            layout.addWidget(QLabel(specs))
            layout.addWidget(QLabel(f"Socket: {self.componente_data.get('socket', 'N/A')}"))
            
        elif self.tipo_componente == 'motherboard':
            layout.addWidget(QLabel(f"Socket: {self.componente_data.get('socket', 'N/A')}"))
            layout.addWidget(QLabel(f"Chipset: {self.componente_data.get('chipset', 'N/A')}"))
            layout.addWidget(QLabel(f"Form Factor: {self.componente_data.get('form_factor', 'N/A')}"))
            
        elif self.tipo_componente == 'ram':
            # Mostrar información detallada de RAM
            capacidad = self.componente_data.get('capacidad', 0)
            capacidad_unit = self.componente_data.get('capacidad_unit', 'GB')
            tipo_ram = self.componente_data.get('tipo', 'N/A')
            frecuencia = self.componente_data.get('frecuencia', 0)
            sticks = self.componente_data.get('sticks', 1)
            timings = self.componente_data.get('timings', '')
            
            # Especificaciones principales
            specs = f"{int(capacidad)}{capacidad_unit} {tipo_ram}-{int(frecuencia)}"
            layout.addWidget(QLabel(specs))
            layout.addWidget(QLabel(f"🔢 {sticks} stick{'s' if sticks > 1 else ''}"))
            
            # Timings si están disponibles
            if timings:
                layout.addWidget(QLabel(f"⏱️ {timings}"))
            
        elif self.tipo_componente == 'case':
            # Mostrar compatibilidad de motherboard y PSU
            mb_support = self.componente_data.get('motherboard_support', 'N/A')
            psu_support = self.componente_data.get('psu_support', 'N/A')
            max_gpu_length = self.componente_data.get('max_gpu_length', 0)
            
            layout.addWidget(QLabel(f"🔧 MB: {mb_support}"))
            layout.addWidget(QLabel(f"⚡ PSU: {psu_support}"))
            layout.addWidget(QLabel(f"🎮 GPU: {int(max_gpu_length)}mm"))
            
        elif self.tipo_componente == 'psu':
            # Mostrar watts, eficiencia y form factor
            watts = self.componente_data.get('wattage', 0)
            efficiency = self.componente_data.get('efficiency', 'N/A')
            form_factor = self.componente_data.get('form_factor', 'N/A')
            
            layout.addWidget(QLabel(f"⚡ {int(watts)}W"))
            layout.addWidget(QLabel(f"🏅 {efficiency}"))
            layout.addWidget(QLabel(f"📏 {form_factor}"))
            
        elif self.tipo_componente == 'gpu':
            # Mostrar VRAM, longitud y slots
            vram_size = self.componente_data.get('vram', 0)
            gpu_length = self.componente_data.get('length', 0)
            slots = self.componente_data.get('slots', 0)
            
            # Mostrar VRAM
            if vram_size > 0:
                layout.addWidget(QLabel(f"🎮 {int(vram_size)}GB VRAM"))
            else:
                layout.addWidget(QLabel(f"🎮 VRAM: N/A"))
                
            # Mostrar longitud
            if gpu_length > 0:
                layout.addWidget(QLabel(f"📏 {int(gpu_length)}mm"))
            else:
                layout.addWidget(QLabel(f"📏 Longitud: N/A"))
                
            # Mostrar slots
            if slots > 0:
                layout.addWidget(QLabel(f"📍 {slots} slots"))
            
        elif self.tipo_componente == 'ssd':
            # Mostrar información detallada de SSD
            capacity = self.componente_data.get('capacity', 0)
            capacity_unit = self.componente_data.get('capacity_unit', 'GB')
            form_factor = self.componente_data.get('form_factor', '')
            protocol = self.componente_data.get('protocol', '')
            nand_type = self.componente_data.get('nand_type', '')
            
            # Capacidad
            if capacity > 0:
                layout.addWidget(QLabel(f"💾 {int(capacity)}{capacity_unit}"))
            else:
                layout.addWidget(QLabel(f"💾 Capacidad: N/A"))
                
            # Form factor y protocolo
            if form_factor:
                layout.addWidget(QLabel(f"� {form_factor}"))
            if protocol:
                layout.addWidget(QLabel(f"� {protocol}"))
            if nand_type:
                layout.addWidget(QLabel(f"⚙️ {nand_type}"))
            
        elif self.tipo_componente == 'hdd':
            # Mostrar información detallada de HDD
            capacity = self.componente_data.get('capacity', 0)
            capacity_unit = self.componente_data.get('capacity_unit', 'GB')
            rpm = self.componente_data.get('rpm', 0)
            cache = self.componente_data.get('cache', 0)
            cache_unit = self.componente_data.get('cache_unit', 'MB')
            
            # Capacidad
            if capacity > 0:
                layout.addWidget(QLabel(f"💿 {int(capacity)}{capacity_unit}"))
            else:
                layout.addWidget(QLabel(f"💿 Capacidad: N/A"))
                
            # RPM
            if rpm > 0:
                layout.addWidget(QLabel(f"🔄 {int(rpm)} RPM"))
                
            # Cache
            if cache is not None and cache > 0:
                layout.addWidget(QLabel(f"�️ {int(cache)}{cache_unit}"))
                
        elif self.tipo_componente == 'cpu_cooler':
            # Mostrar información detallada de CPU Cooler
            tdp = self.componente_data.get('tdp', 0)
            height = self.componente_data.get('height', 0)
            socket_count = self.componente_data.get('socket_count', 0)
            supported_sockets = self.componente_data.get('supported_sockets', [])
            
            # TDP - verificar que no sea None
            if tdp is not None and tdp > 0:
                layout.addWidget(QLabel(f"⚡ {int(tdp)}W TDP"))
                
            # Altura - verificar que no sea None
            if height is not None and height > 0:
                layout.addWidget(QLabel(f"📏 {int(height)}mm"))
                
            # Sockets soportados
            if socket_count > 0:
                layout.addWidget(QLabel(f"🔌 {socket_count} sockets"))
            elif supported_sockets:
                # Mostrar algunos sockets principales
                sockets_principales = supported_sockets[:3]
                sockets_text = ", ".join(sockets_principales)
                if len(supported_sockets) > 3:
                    sockets_text += f" (+{len(supported_sockets) - 3})"
                layout.addWidget(QLabel(f"� {sockets_text}"))
            
    def mousePressEvent(self, event):
        """Maneja el clic en el componente"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.componente_seleccionado.emit(self.componente_data, self.tipo_componente)
        super().mousePressEvent(event)


class BotonComponente(QPushButton):
    """Botón tipo tarjeta para seleccionar tipos de componentes"""
    
    componente_seleccionado = pyqtSignal(str, str)  # tipo, nombre
    
    def __init__(self, nombre: str, tipo: str, icono_texto: str = "🔧"):
        super().__init__()
        self.nombre = nombre
        self.tipo = tipo
        self.icono_texto = icono_texto
        self.is_selected = False
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la UI del botón tarjeta"""
        self.setFixedHeight(60)  # Reducido de 80 a 60
        self.setObjectName("botonComponente")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Configurar el texto del botón (solo nombre, sin tipo redundante)
        texto_completo = f"{self.icono_texto}  {self.nombre}"
        self.setText(texto_completo)
        
        # Conectar clic
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Maneja el clic en el botón"""
        self.componente_seleccionado.emit(self.tipo, self.nombre)
        
    def set_selected(self, selected: bool):
        """Establece el estado de selección"""
        self.is_selected = selected
        if selected:
            self.setObjectName("botonComponenteSeleccionado")
        else:
            self.setObjectName("botonComponente")
        # Reaplicar estilos
        self.style().unpolish(self)
        self.style().polish(self)


class FiltrosPanel(QGroupBox):
    """Panel de filtros para componentes"""
    
    filtros_cambiados = pyqtSignal(dict)
    
    def __init__(self, titulo: str):
        super().__init__(titulo)
        self.filtros_actuales = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la UI del panel de filtros"""
        layout = QVBoxLayout(self)
        
        # Mensaje informativo sobre filtros automáticos
        info_label = QLabel("Los filtros se aplican automáticamente\nbasado en la compatibilidad de componentes")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)
        
    def _on_filtro_cambiado(self):
        """Maneja cambios en los filtros - No usado actualmente"""
        pass


class ComponentesPanel(QWidget):
    """Panel para mostrar lista de componentes"""
    
    def __init__(self, tipo_componente: str):
        super().__init__()
        self.tipo_componente = tipo_componente
        self.componentes_actuales = []
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la UI del panel"""
        layout = QVBoxLayout(self)
        
        # Área de scroll para componentes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget contenedor para los componentes
        self.contenedor_componentes = QWidget()
        self.layout_componentes = QVBoxLayout(self.contenedor_componentes)
        self.layout_componentes.addStretch()
        
        self.scroll_area.setWidget(self.contenedor_componentes)
        layout.addWidget(self.scroll_area)
        
    def actualizar_componentes(self, componentes: List[Dict]):
        """Actualiza la lista de componentes mostrados"""
        # Limpiar componentes anteriores
        while self.layout_componentes.count() > 1:  # Mantener el stretch
            child = self.layout_componentes.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        self.componentes_actuales = componentes
        
        # Agregar nuevos componentes
        for comp_data in componentes[:20]:  # Limitar a 20 por rendimiento
            comp_formatted = formatear_componente_para_ui(comp_data, self.tipo_componente)
            widget = ComponenteWidget(comp_formatted, self.tipo_componente)
            self.layout_componentes.insertWidget(
                self.layout_componentes.count() - 1, widget
            )
            
        # Actualizar scroll
        self.scroll_area.verticalScrollBar().setValue(0)


class ConfiguracionPanel(QWidget):
    """Panel que muestra la configuración actual del PC"""
    
    def __init__(self):
        super().__init__()
        self.configuracion_actual = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la UI del panel de configuración"""
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Configuración Actual")
        titulo.setObjectName("tituloConfiguracion")
        layout.addWidget(titulo)
        
        # Área de configuración
        self.config_scroll = QScrollArea()
        self.config_scroll.setWidgetResizable(True)
        
        self.config_widget = QWidget()
        self.config_layout = QVBoxLayout(self.config_widget)
        
        # Crear campos para cada tipo de componente
        self.campos_componentes = {}
        tipos_componentes = [
            ('CPU', 'cpu'),
            ('Motherboard', 'motherboard'),
            ('RAM', 'ram'),
            ('GPU', 'gpu'),
            ('Case', 'case'),
            ('PSU', 'psu'),
            ('CPU Cooler', 'cpu_cooler'),
            ('SSD', 'ssd'),
            ('HDD', 'hdd')
        ]
        
        for nombre, tipo in tipos_componentes:
            campo = self._crear_campo_componente(nombre, tipo)
            self.campos_componentes[tipo] = campo
            self.config_layout.addWidget(campo)
            
        self.config_layout.addStretch()
        self.config_scroll.setWidget(self.config_widget)
        layout.addWidget(self.config_scroll)
        
        # Panel de validación
        self.validacion_text = QTextEdit()
        self.validacion_text.setMaximumHeight(100)
        self.validacion_text.setObjectName("validacionText")
        layout.addWidget(QLabel("Estado de Compatibilidad:"))
        layout.addWidget(self.validacion_text)
        
    def _crear_campo_componente(self, nombre: str, tipo: str) -> QFrame:
        """Crea un campo para mostrar un componente seleccionado"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setObjectName("campoComponente")
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # Etiqueta del tipo
        tipo_label = QLabel(nombre)
        tipo_label.setObjectName("tipoComponente")
        layout.addWidget(tipo_label)
        
        # Campo de contenido
        contenido_label = QLabel("No seleccionado")
        contenido_label.setObjectName("contenidoComponente")
        contenido_label.setWordWrap(True)
        layout.addWidget(contenido_label)
        
        # Guardar referencia al label de contenido
        frame.contenido_label = contenido_label
        
        return frame
        
    def actualizar_componente(self, componente_data: Dict, tipo: str):
        """Actualiza un componente en la configuración"""
        self.configuracion_actual[tipo] = componente_data
        
        if tipo in self.campos_componentes:
            campo = self.campos_componentes[tipo]
            nombre = componente_data.get('nombre', 'Componente sin nombre')
            fabricante = componente_data.get('fabricante', '')
            
            texto = f"{nombre}"
            if fabricante:
                texto += f"\n{fabricante}"
                
            campo.contenido_label.setText(texto)
            
        # Actualizar validación
        self._actualizar_validacion()
        
    def _actualizar_validacion(self):
        """Actualiza el estado de validación"""
        # Aquí integraremos con el sistema de filtros
        mensajes = []
        
        # Verificaciones básicas
        if 'cpu' in self.configuracion_actual and 'motherboard' in self.configuracion_actual:
            cpu_socket = self.configuracion_actual['cpu'].get('socket')
            mb_socket = self.configuracion_actual['motherboard'].get('socket')
            
            if cpu_socket == mb_socket:
                mensajes.append("✅ CPU y Motherboard compatibles")
            else:
                mensajes.append(f"❌ Sockets incompatibles: CPU({cpu_socket}) vs MB({mb_socket})")
                
        if len(self.configuracion_actual) == 0:
            mensajes.append("Selecciona componentes para comenzar")
        elif len(self.configuracion_actual) < 5:
            mensajes.append("⚠️ Configuración incompleta")
        else:
            mensajes.append("✅ Configuración básica completa")
            
        self.validacion_text.setText("\n".join(mensajes))


class PCBuilderMainWindow(QMainWindow):
    """Ventana principal del PC Builder"""
    
    def __init__(self, arquitectura: str):
        super().__init__()
        self.arquitectura = arquitectura
        self.workflow = None
        self.configuracion_actual = {}
        self.tipo_seleccionado = 'cpu'  # Tipo de componente seleccionado actualmente
        self.botones_componentes = {}   # Diccionario de botones de componentes
        self.filtros_componentes = {}   # Diccionario de paneles de filtros
        self.filtros_widget_actual = None  # Widget de filtros actualmente mostrado
        self.setup_ui()
        self.setup_styles()
        self.inicializar_datos()
       
    def setup_ui(self):
        """Configura la interfaz principal"""
        self.setWindowTitle(f"PC Builder - {self.arquitectura}")
        self.setMinimumSize(1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Crear el widget de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabWidget")
        
        # Pestaña principal - PC Builder
        builder_tab = self._crear_tab_builder()
        self.tab_widget.addTab(builder_tab, "🔧 PC Builder")
        
        # Pestañas de análisis matemático si están disponibles
        if PESTANAS_MATEMATICAS_DISPONIBLES:
            try:
                # Pestaña de análisis matemático
                self.analisis_tab = AnalisisMatematicoTab()
                self.tab_widget.addTab(self.analisis_tab, "📊 Análisis Matemático")
                
                # Pestaña de optimización
                #self.optimizacion_tab = OptimizacionTab()
                #self.tab_widget.addTab(self.optimizacion_tab, "⚡ Optimización")
                
                print("✓ Pestañas matemáticas creadas exitosamente")
                
            except Exception as e:
                print(f"Error creando pestañas matemáticas: {e}")
                import traceback
                traceback.print_exc()
                
                # Crear pestañas de fallback
                self.analisis_tab = QWidget()
                #self.optimizacion_tab = QWidget()
                
                # Agregar labels informativos
                fallback_layout = QVBoxLayout(self.analisis_tab)
                fallback_layout.addWidget(QLabel("Análisis Matemático no disponible"))
                fallback_layout.addWidget(QLabel(f"Error: {e}"))
                
                #fallback_layout2 = QVBoxLayout(self.optimizacion_tab)
                #fallback_layout2.addWidget(QLabel("Optimización no disponible"))
                #fallback_layout2.addWidget(QLabel(f"Error: {e}"))
                
                self.tab_widget.addTab(self.analisis_tab, "📊 Análisis Matemático")
                #self.tab_widget.addTab(self.optimizacion_tab, "⚡ Optimización")
        
        main_layout.addWidget(self.tab_widget)
        
    def _crear_tab_builder(self) -> QWidget:
        """Crea la pestaña principal del PC Builder"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Navegación y filtros
        panel_izquierdo = self._crear_panel_izquierdo()
        splitter.addWidget(panel_izquierdo)
        
        # Panel central - Lista de componentes
        panel_central = self._crear_panel_central()
        splitter.addWidget(panel_central)
        
        # Panel derecho - Configuración actual
        panel_derecho = self._crear_panel_derecho()
        splitter.addWidget(panel_derecho)
        
        # Configurar proporciones del splitter
        splitter.setSizes([300, 500, 400])
        
        layout.addWidget(splitter)
        return widget
        
    def _crear_panel_izquierdo(self) -> QWidget:
        """Crea el panel de navegación y filtros"""
        widget = QWidget()
        widget.setMaximumWidth(350)
        layout = QVBoxLayout(widget)
        
        # Información de arquitectura
        arq_label = QLabel(f"Arquitectura: {self.arquitectura}")
        arq_label.setObjectName("arquitecturaLabel")
        layout.addWidget(arq_label)
        
        # Título para selección de componentes
        titulo_seleccion = QLabel("Selecciona el tipo de componente:")
        titulo_seleccion.setObjectName("tituloSeleccion")
        layout.addWidget(titulo_seleccion)
        
        # Contenedor con scroll para botones de componentes
        scroll_botones = QScrollArea()
        scroll_botones.setWidgetResizable(True)
        scroll_botones.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_botones.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_botones.setMaximumHeight(400)
        
        widget_botones = QWidget()
        layout_botones = QVBoxLayout(widget_botones)
        layout_botones.setSpacing(8)
        
        # Crear botones/tarjetas para cada tipo de componente
        self.botones_componentes = {}
        self.filtros_componentes = {}
        tipos_componentes = [
            ('CPU', 'cpu', '🔲'),
            ('Motherboard', 'motherboard', '🔧'),
            ('RAM', 'ram', '📊'),
            ('GPU', 'gpu', '🎮'),
            ('Case', 'case', '📦'),
            ('PSU', 'psu', '⚡'),
            ('SSD', 'ssd', '💾'),
            ('HDD', 'hdd', '💿'),
            ('CPU Cooler', 'cpu_cooler', '❄️')
            # Removido Monitor por ahora hasta que tengamos los datos
        ]
        
        for nombre, tipo, icono in tipos_componentes:
            boton = BotonComponente(nombre, tipo, icono)
            boton.componente_seleccionado.connect(self._on_tipo_componente_seleccionado)
            self.botones_componentes[tipo] = boton
            layout_botones.addWidget(boton)
            
        layout_botones.addStretch()
        scroll_botones.setWidget(widget_botones)
        layout.addWidget(scroll_botones)
        
        # Panel de filtros (se muestra cuando se selecciona un tipo)
        self.filtros_panel = QFrame()
        self.filtros_panel.setFrameStyle(QFrame.Shape.Box)
        self.filtros_panel.setObjectName("filtrosPanel")
        self.filtros_layout = QVBoxLayout(self.filtros_panel)
        
        # Inicialmente oculto
        self.filtros_panel.hide()
        layout.addWidget(self.filtros_panel)
        
        # Botón de validación completa
        btn_validar = QPushButton("💯 Validar Configuración Completa")
        btn_validar.setObjectName("botonValidar")
        btn_validar.clicked.connect(self._validar_configuracion_completa)
        layout.addWidget(btn_validar)
        
        # Seleccionar CPU por defecto
        self.tipo_seleccionado = 'cpu'
        self.botones_componentes['cpu'].set_selected(True)
        self._mostrar_filtros_para_tipo('cpu')
        
        return widget
        
    def _crear_panel_central(self) -> QWidget:
        """Crea el panel central con la lista de componentes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título dinámico
        self.titulo_componentes = QLabel("Selecciona un tipo de componente")
        self.titulo_componentes.setObjectName("tituloComponentes")
        layout.addWidget(self.titulo_componentes)
        
        # Panel de componentes (se creará dinámicamente)
        self.panel_componentes = ComponentesPanel('cpu')  # Por defecto
        layout.addWidget(self.panel_componentes)
        
        # Conectar selección de componentes
        self.panel_componentes.contenedor_componentes.setProperty('tipo_actual', 'cpu')
        
        return widget
        
    def _crear_panel_derecho(self) -> QWidget:
        """Crea el panel de configuración actual"""
        widget = QWidget()
        widget.setMaximumWidth(400)
        layout = QVBoxLayout(widget)
        
        # Panel de configuración
        self.config_panel = ConfiguracionPanel()
        layout.addWidget(self.config_panel)
        
        return widget
        
    def inicializar_datos(self):
        """Inicializa el workflow de datos"""
        try:
            ruta_datos = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "normalized_data"
            )
            
            self.workflow = crear_workflow_seleccion_componentes(ruta_datos)
            
            # Cargar componentes iniciales (CPUs de la arquitectura seleccionada)
            self._cargar_componentes_iniciales()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando datos: {e}")
            
    def _cargar_componentes_iniciales(self):
        """Carga los componentes iniciales basados en la arquitectura"""
        if not self.workflow:
            return
            
        # Cargar CPUs de la arquitectura seleccionada por defecto
        self._cargar_componentes_por_tipo('cpu')
        
        # Conectar eventos de selección
        self._conectar_eventos_componentes()
        
    def _conectar_eventos_componentes(self):
        """Conecta los eventos de selección de componentes"""
        # Iterar sobre todos los widgets de componentes y conectar sus señales
        for i in range(self.panel_componentes.layout_componentes.count() - 1):
            widget = self.panel_componentes.layout_componentes.itemAt(i).widget()
            if isinstance(widget, ComponenteWidget):
                widget.componente_seleccionado.connect(self._on_componente_seleccionado)
                
    @pyqtSlot(dict, str)
    def _on_componente_seleccionado(self, componente_data: Dict, tipo: str):
        """Maneja la selección de un componente"""
        # Actualizar configuración
        self.config_panel.actualizar_componente(componente_data, tipo)
        
        # Actualizar configuración interna
        self.configuracion_actual[tipo] = componente_data
                # Propagar configuración a las pestañas de análisis
        self.propagar_build_a_analisis(self.configuracion_actual)
  
        # Si es una selección crítica, actualizar filtros automáticamente
        if tipo in ['cpu', 'motherboard']:
            self._actualizar_filtros_automaticos(componente_data, tipo)
            
    def _actualizar_filtros_automaticos(self, componente_data: Dict, tipo: str):
        """Actualiza filtros automáticamente basado en selecciones críticas"""
        if not self.workflow:
            return
            
        gestor = self.workflow['gestor_filtros']
        
        # Actualizar configuración interna
        self.configuracion_actual = self.config_panel.configuracion_actual
        
        if tipo == 'cpu':
            # CPU seleccionado -> actualizar automáticamente motherboards compatibles
            socket = componente_data.get('socket')
            if socket:
                # Si estamos viendo motherboards, actualizarlas inmediatamente
                if self.tipo_seleccionado == 'motherboard':
                    try:
                        motherboards = gestor.filtrar_motherboards_por_socket(socket)
                        self._actualizar_panel_componentes('motherboard', motherboards)
                    except Exception as e:
                        print(f"Error filtrando motherboards: {e}")
                
                # Resaltar el botón de motherboard para sugerir próxima selección
                if self.tipo_seleccionado != 'motherboard':
                    self.botones_componentes['motherboard'].setStyleSheet("""
                        QPushButton#botonComponente {
                            border: 3px solid #e74c3c;
                            background-color: #fdeaea;
                        }
                    """)
                
        elif tipo == 'motherboard':
            # Motherboard seleccionado -> actualizar RAM y Case compatibles
            socket = componente_data.get('socket')
            form_factor = componente_data.get('form_factor')
            
            # Actualizar RAM si estamos viendo RAM
            if self.tipo_seleccionado == 'ram' and socket:
                try:
                    ram_data = gestor.filtrar_ram_por_motherboard(socket, form_factor)
                    if isinstance(ram_data, tuple):
                        ram_compatible = ram_data[0]
                    else:
                        ram_compatible = ram_data
                    self._actualizar_panel_componentes('ram', ram_compatible)
                except Exception as e:
                    print(f"Error filtrando RAM: {e}")
                
            # Actualizar Cases si estamos viendo Cases
            if self.tipo_seleccionado == 'case' and form_factor:
                try:
                    cases = gestor.filtrar_cases_por_motherboard_form_factor(form_factor)
                    self._actualizar_panel_componentes('case', cases)
                except Exception as e:
                    print(f"Error filtrando Cases: {e}")
            
            # Resaltar botones sugeridos
            if self.tipo_seleccionado not in ['ram', 'case']:
                for sugerido in ['ram', 'case']:
                    if sugerido in self.botones_componentes:
                        self.botones_componentes[sugerido].setStyleSheet("""
                            QPushButton#botonComponente {
                                border: 3px solid #f39c12;
                                background-color: #fef5e7;
                            }
                        """)
                
    def _actualizar_panel_componentes(self, tipo: str, componentes: List[Dict]):
        """Actualiza el panel de componentes con nuevos datos"""
        self.panel_componentes.tipo_componente = tipo
        self.panel_componentes.actualizar_componentes(componentes)
        self.titulo_componentes.setText(f"{tipo.upper()} - {len(componentes)} disponibles")
        
        # Reconectar eventos
        self._conectar_eventos_componentes()
        
    def _aplicar_filtros(self, tipo: str, filtros: Dict):
        """Aplica filtros a los componentes del tipo especificado"""
        # Los filtros se aplican automáticamente por compatibilidad
        # No hay filtros manuales por ahora
        pass
        
    def _validar_configuracion_completa(self):
        """Valida la configuración completa usando el sistema de filtros"""
        if not self.workflow or not self.config_panel.configuracion_actual:
            QMessageBox.information(self, "Validación", "No hay componentes seleccionados para validar")
            return
            
        validador = self.workflow['validador']
        configuracion = self.config_panel.configuracion_actual
        
        # Verificar compatibilidad general
        resultado_general = self.workflow['gestor_filtros'].verificar_compatibilidad_completa(configuracion)
        
        # Verificar dimensiones físicas
        resultado_fisico = validador.validar_dimensiones_fisicas(configuracion)
            # Propagar configuración completa a las pestañas de análisis
        self.propagar_build_a_analisis(configuracion)
        # Mostrar resultados
        mensaje = "=== VALIDACIÓN COMPLETA ===\n\n"
        
        if resultado_general['compatible'] and resultado_fisico['compatible']:
            mensaje += "✅ CONFIGURACIÓN COMPATIBLE\n\n"
        else:
            mensaje += "❌ PROBLEMAS DETECTADOS\n\n"
            
        if resultado_general['errores']:
            mensaje += "Errores:\n"
            for error in resultado_general['errores']:
                mensaje += f"• {error}\n"
            mensaje += "\n"
            
        if resultado_general['advertencias'] or resultado_fisico['advertencias']:
            mensaje += "Advertencias:\n"
            for adv in resultado_general['advertencias'] + resultado_fisico['advertencias']:
                mensaje += f"• {adv}\n"
                
        QMessageBox.information(self, "Validación Completa", mensaje)
        
    def setup_styles(self):
        """Configura los estilos CSS de la aplicación"""
        try:
            # Cargar CSS desde archivo externo
            css_path = os.path.join(os.path.dirname(__file__), 'static', 'style.css')
            with open(css_path, 'r', encoding='utf-8') as f:
                style = f.read()
            self.setStyleSheet(style)
        except Exception as e:
            print(f"Error cargando estilos CSS: {e}")
            # Fallback a estilo básico
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8fafc;
                }
                QPushButton {
                    padding: 8px 16px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
        
    @pyqtSlot(str, str)
    def _on_tipo_componente_seleccionado(self, tipo: str, nombre: str):
        """Maneja la selección de un tipo de componente"""
        # Deseleccionar el botón anterior
        if hasattr(self, 'tipo_seleccionado') and self.tipo_seleccionado in self.botones_componentes:
            self.botones_componentes[self.tipo_seleccionado].set_selected(False)
            
        # Limpiar estilos especiales de todos los botones
        self._limpiar_estilos_botones()
            
        # Seleccionar el nuevo botón
        self.tipo_seleccionado = tipo
        self.botones_componentes[tipo].set_selected(True)
        
        # Mostrar filtros para este tipo
        self._mostrar_filtros_para_tipo(tipo)
        
        # Cargar componentes de este tipo
        self._cargar_componentes_por_tipo(tipo)
        
    def _limpiar_estilos_botones(self):
        """Limpia los estilos especiales de todos los botones"""
        for boton in self.botones_componentes.values():
            boton.setStyleSheet("")  # Limpiar estilo personalizado
        
    def _mostrar_filtros_para_tipo(self, tipo: str):
        """Muestra los filtros específicos para un tipo de componente"""
        # Ocultar el widget de filtros actual si existe
        if hasattr(self, 'filtros_widget_actual') and self.filtros_widget_actual:
            self.filtros_widget_actual.setParent(None)
            self.filtros_widget_actual = None
        
        # Crear o reutilizar filtros específicos para el tipo
        if tipo not in self.filtros_componentes:
            filtros = FiltrosPanel(f"Filtros {tipo.upper()}")
            filtros.filtros_cambiados.connect(
                lambda f, t=tipo: self._aplicar_filtros(t, f)
            )
            self.filtros_componentes[tipo] = filtros
        
        # Obtener el widget de filtros para este tipo
        filtros_widget = self.filtros_componentes[tipo]
        
        # Agregar al layout
        self.filtros_layout.addWidget(filtros_widget)
        self.filtros_widget_actual = filtros_widget
        self.filtros_panel.show()
        
    def _cargar_componentes_por_tipo(self, tipo: str, filtros_adicionales: Optional[Dict] = None):
        """Carga los componentes del tipo especificado"""
        if not self.workflow:
            return
            
        gestor = self.workflow['gestor_filtros']
        componentes = []
        
        try:
            if tipo == 'cpu':
                componentes = gestor.filtrar_cpus_por_arquitectura(self.arquitectura)
            elif tipo == 'motherboard':
                # Filtrar por CPU si ya hay uno seleccionado
                if 'cpu' in self.configuracion_actual:
                    cpu_data = self.configuracion_actual['cpu']
                    socket = cpu_data.get('architecture', {}).get('socket') if isinstance(cpu_data.get('architecture'), dict) else cpu_data.get('socket')
                    if socket:
                        componentes = gestor.filtrar_motherboards_por_socket(socket)
                    else:
                        componentes = gestor.datos.get('motherboard', [])
                else:
                    componentes = gestor.datos.get('motherboard', [])
                    
            elif tipo == 'ram':
                # Filtrar por motherboard si ya hay uno seleccionado
                if 'motherboard' in self.configuracion_actual:
                    mb_data = self.configuracion_actual['motherboard']
                    socket = mb_data.get('socket')
                    form_factor = mb_data.get('form_factor')
                    if socket or form_factor:
                        ram_data = gestor.filtrar_ram_por_motherboard(socket, form_factor)
                        # El método puede devolver una tupla o lista, manejar ambos casos
                        if isinstance(ram_data, tuple):
                            componentes = ram_data[0]
                        else:
                            componentes = ram_data
                    else:
                        componentes = gestor.datos.get('ram', [])
                else:
                    componentes = gestor.datos.get('ram', [])
                    
            elif tipo == 'gpu':
                componentes = gestor.datos.get('gpu', [])
                
            elif tipo == 'case':
                # Filtrar por motherboard si ya hay uno seleccionado
                if 'motherboard' in self.configuracion_actual:
                    mb_data = self.configuracion_actual['motherboard']
                    form_factor = mb_data.get('form_factor')
                    if form_factor:
                        componentes = gestor.filtrar_cases_por_motherboard_form_factor(form_factor)
                    else:
                        componentes = gestor.datos.get('case', [])
                else:
                    componentes = gestor.datos.get('case', [])
                    
            elif tipo == 'psu':
                componentes = gestor.datos.get('psu', [])
                
            elif tipo == 'ssd':
                componentes = gestor.datos.get('ssd', [])
                
            elif tipo == 'hdd':
                componentes = gestor.datos.get('hdd', [])
                
            elif tipo == 'cpu_cooler':
                # Para CPU Cooler, cargar todos por ahora (método específico no existe)
                componentes = gestor.datos.get('cpu_cooler', [])
                    
            else:
                # Tipo no reconocido, intentar cargar datos básicos
                componentes = gestor.datos.get(tipo, [])
                
            # Actualizar panel de componentes
            self._actualizar_panel_componentes(tipo, componentes)
            
        except Exception as e:
            print(f"Error cargando componentes {tipo}: {e}")
            import traceback
            traceback.print_exc()
            # Cargar datos básicos como fallback
            componentes = gestor.datos.get(tipo, [])
            if componentes:
                self._actualizar_panel_componentes(tipo, componentes)
            else:
                self.titulo_componentes.setText(f"Sin datos para {tipo}")
    def propagar_build_a_analisis(self, configuracion: dict):
        """Propaga la configuración de build a la pestaña de análisis"""
        try:
            # Actualizar pestaña de análisis
            if hasattr(self, 'analisis_tab') and self.analisis_tab:
                if hasattr(self.analisis_tab, 'actualizar_configuracion'):
                    self.analisis_tab.actualizar_configuracion(configuracion)
                else:
                    print("⚠️ analisis_tab no tiene método actualizar_configuracion")
            
            # Actualizar pestaña de optimización
            #if hasattr(self, 'optimizacion_tab') and self.optimizacion_tab:
               #if hasattr(self.optimizacion_tab, 'actualizar_configuracion'):
                   #self.optimizacion_tab.actualizar_configuracion(configuracion)
               #else:
                   #print("⚠️ optimizacion_tab no tiene método actualizar_configuracion")

            # Actualizar configuración interna
            self.configuracion_actual = configuracion.copy()
            
            print(f"✓ Configuración propagada: {len(configuracion)} componentes")
            
        except Exception as e:
            print(f"Error propagando configuración: {e}")
            import traceback
            traceback.print_exc()