"""
Interfaz gráfica para el Optimizador de PC
Integra todas las funcionalidades de main.py, script2.py y script3.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Dict, List
import json
import threading

# Importar nuestros módulos
from main import OptimizadorPC
from script3 import GestorBaseDatos
from script2 import VisualizadorPC

class InterfazOptimizadorPC:
    """Interfaz gráfica principal para el optimizador de PC"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.optimizador = OptimizadorPC("data.json")
        self.gestor_db = GestorBaseDatos("data.json")
        self.visualizador = VisualizadorPC(self.optimizador)
        
        # Variables de estado
        self.configuraciones_generadas = []
        self.config_optima = None
        
        self.configurar_ventana_principal()
        self.crear_interfaz()
        
    def configurar_ventana_principal(self):
        """Configura la ventana principal"""
        self.root.title("🖥️ Optimizador de PC - Configuraciones Eficientes")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2E86C1')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495E')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#566573')
        style.configure('Success.TLabel', font=('Arial', 10), foreground='#27AE60')
        style.configure('Warning.TLabel', font=('Arial', 10), foreground='#E74C3C')
        
        # Configurar grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
    def crear_interfaz(self):
        """Crea la interfaz principal con pestañas"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Título principal
        title_label = ttk.Label(main_frame, text="🖥️ Optimizador de PC", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Crear pestañas
        self.crear_pestaña_optimizacion()
        self.crear_pestaña_visualizacion()
        self.crear_pestaña_base_datos()
        self.crear_pestaña_configuracion()
        
        # Barra de estado
        self.crear_barra_estado(main_frame)
        
    def crear_pestaña_optimizacion(self):
        """Crea la pestaña principal de optimización"""
        # Frame de optimización
        opt_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(opt_frame, text="🎯 Optimización")
        
        # Configurar grid
        opt_frame.grid_columnconfigure(1, weight=1)
        
        # Panel izquierdo - Controles
        control_frame = ttk.LabelFrame(opt_frame, text="🔧 Controles", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Información de componentes
        info_label = ttk.Label(control_frame, text="📦 Componentes Disponibles:", style='Subtitle.TLabel')
        info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Mostrar estadísticas de componentes
        self.stats_text = tk.Text(control_frame, height=8, width=30, wrap=tk.WORD)
        stats_scroll = ttk.Scrollbar(control_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        self.stats_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        stats_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(0, 10))
        
        # Botones de control
        ttk.Button(control_frame, text="🔄 Actualizar Info", 
                  command=self.actualizar_info_componentes).grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Separator(control_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Parámetros de optimización
        params_label = ttk.Label(control_frame, text="⚙️ Parámetros:", style='Subtitle.TLabel')
        params_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(control_frame, text="Max configuraciones:").grid(row=5, column=0, sticky=tk.W)
        self.max_configs_var = tk.StringVar(value="20")
        ttk.Entry(control_frame, textvariable=self.max_configs_var, width=10).grid(row=5, column=1, sticky=tk.E)
        
        ttk.Label(control_frame, text="Peso costo (0-1):").grid(row=6, column=0, sticky=tk.W)
        self.peso_costo_var = tk.StringVar(value="0.4")
        ttk.Entry(control_frame, textvariable=self.peso_costo_var, width=10).grid(row=6, column=1, sticky=tk.E)
        
        # Botones principales
        ttk.Button(control_frame, text="🚀 Generar Configuraciones", 
                  command=self.generar_configuraciones, style='Accent.TButton').grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(control_frame, text="🏆 Encontrar Óptima", 
                  command=self.encontrar_optima).grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(control_frame, text="🎯 Análisis Crítico", 
                  command=self.analizar_puntos_criticos).grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Panel derecho - Resultados
        result_frame = ttk.LabelFrame(opt_frame, text="📊 Resultados", padding="10")
        result_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(1, weight=1)
        
        # Tabs para diferentes resultados
        self.result_notebook = ttk.Notebook(result_frame)
        self.result_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Tab de configuración óptima
        self.crear_tab_configuracion_optima()
        
        # Tab de todas las configuraciones
        self.crear_tab_todas_configuraciones()
        
        # Tab de análisis matemático
        self.crear_tab_analisis_matematico()
        
        # Inicializar información
        self.actualizar_info_componentes()
        
    def crear_tab_configuracion_optima(self):
        """Crea el tab de configuración óptima"""
        opt_config_frame = ttk.Frame(self.result_notebook, padding="10")
        self.result_notebook.add(opt_config_frame, text="🏆 Óptima")
        
        # Text widget para mostrar la configuración óptima
        self.optimal_text = tk.Text(opt_config_frame, height=15, wrap=tk.WORD, font=('Consolas', 10))
        optimal_scroll = ttk.Scrollbar(opt_config_frame, orient=tk.VERTICAL, command=self.optimal_text.yview)
        self.optimal_text.configure(yscrollcommand=optimal_scroll.set)
        
        self.optimal_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        optimal_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        opt_config_frame.grid_columnconfigure(0, weight=1)
        opt_config_frame.grid_rowconfigure(0, weight=1)
        
        # Botones de acción
        button_frame = ttk.Frame(opt_config_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(button_frame, text="💾 Exportar Configuración", 
                  command=self.exportar_configuracion_optima).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📋 Copiar al Portapapeles", 
                  command=self.copiar_configuracion).pack(side=tk.LEFT)
        
    def crear_tab_todas_configuraciones(self):
        """Crea el tab de todas las configuraciones"""
        all_config_frame = ttk.Frame(self.result_notebook, padding="10")
        self.result_notebook.add(all_config_frame, text="📋 Todas")
        
        # Treeview para mostrar todas las configuraciones
        columns = ('ID', 'Costo', 'Consumo', 'Eficiencia', 'Gabinete', 'CPU', 'GPU')
        self.config_tree = ttk.Treeview(all_config_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        for col in columns:
            self.config_tree.heading(col, text=col)
            self.config_tree.column(col, width=100)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(all_config_frame, orient=tk.VERTICAL, command=self.config_tree.yview)
        tree_scroll_x = ttk.Scrollbar(all_config_frame, orient=tk.HORIZONTAL, command=self.config_tree.xview)
        self.config_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.config_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        all_config_frame.grid_columnconfigure(0, weight=1)
        all_config_frame.grid_rowconfigure(0, weight=1)
        
        # Evento de selección
        self.config_tree.bind('<<TreeviewSelect>>', self.on_config_select)
        
    def crear_tab_analisis_matematico(self):
        """Crea el tab de análisis matemático"""
        math_frame = ttk.Frame(self.result_notebook, padding="10")
        self.result_notebook.add(math_frame, text="📐 Análisis")
        
        # Text widget para mostrar análisis matemático
        self.math_text = tk.Text(math_frame, height=15, wrap=tk.WORD, font=('Consolas', 10))
        math_scroll = ttk.Scrollbar(math_frame, orient=tk.VERTICAL, command=self.math_text.yview)
        self.math_text.configure(yscrollcommand=math_scroll.set)
        
        self.math_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        math_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        math_frame.grid_columnconfigure(0, weight=1)
        math_frame.grid_rowconfigure(0, weight=1)
        
    def crear_pestaña_visualizacion(self):
        """Crea la pestaña de visualización"""
        viz_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(viz_frame, text="📊 Visualización")
        
        viz_frame.grid_columnconfigure(1, weight=1)
        viz_frame.grid_rowconfigure(0, weight=1)
        
        # Panel de controles de visualización
        viz_control_frame = ttk.LabelFrame(viz_frame, text="🎨 Opciones de Visualización", padding="10")
        viz_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Botones de visualización
        viz_buttons = [
            ("📈 Consumo vs Costo", self.mostrar_consumo_vs_costo),
            ("🎯 Comparar Configs", self.mostrar_comparacion_configs),
            ("📦 Análisis Volúmenes", self.mostrar_analisis_volumenes),
            ("💰 Distribución Precios", self.mostrar_distribucion_precios),
            ("⚡ Análisis Consumo", self.mostrar_analisis_consumo),
            ("🏆 Dashboard Completo", self.mostrar_dashboard_completo)
        ]
        
        for i, (text, command) in enumerate(viz_buttons):
            ttk.Button(viz_control_frame, text=text, command=command, width=25
                      ).grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Separator(viz_control_frame, orient='horizontal').grid(row=len(viz_buttons), column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Opciones adicionales
        ttk.Label(viz_control_frame, text="Opciones:", style='Subtitle.TLabel').grid(row=len(viz_buttons)+1, column=0, sticky=tk.W)
        
        self.show_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(viz_control_frame, text="Mostrar grilla", variable=self.show_grid_var).grid(row=len(viz_buttons)+2, column=0, sticky=tk.W)
        
        self.high_dpi_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(viz_control_frame, text="Alta resolución", variable=self.high_dpi_var).grid(row=len(viz_buttons)+3, column=0, sticky=tk.W)
        
        # Panel de visualización
        self.viz_panel_frame = ttk.LabelFrame(viz_frame, text="📊 Gráficos", padding="10")
        self.viz_panel_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.viz_panel_frame.grid_columnconfigure(0, weight=1)
        self.viz_panel_frame.grid_rowconfigure(0, weight=1)
        
        # Label de instrucciones inicial
        self.viz_instructions = ttk.Label(self.viz_panel_frame, 
                                         text="Selecciona una opción de visualización\npara mostrar los gráficos aquí",
                                         style='Info.TLabel', justify=tk.CENTER)
        self.viz_instructions.grid(row=0, column=0)
        
    def crear_pestaña_base_datos(self):
        """Crea la pestaña de gestión de base de datos"""
        db_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(db_frame, text="🗃️ Base de Datos")
        
        db_frame.grid_columnconfigure(1, weight=1)
        db_frame.grid_rowconfigure(0, weight=1)
        
        # Panel de controles
        db_control_frame = ttk.LabelFrame(db_frame, text="🔧 Gestión de Datos", padding="10")
        db_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Botones de gestión
        db_buttons = [
            ("📋 Ver Componentes", self.mostrar_componentes),
            ("➕ Agregar Componente", self.agregar_componente_gui),
            ("🔍 Buscar Componentes", self.buscar_componentes_gui),
            ("📊 Estadísticas DB", self.mostrar_estadisticas_db),
            ("✅ Validar Integridad", self.validar_integridad_gui),
            ("💾 Exportar Datos", self.exportar_datos),
            ("📁 Importar Datos", self.importar_datos),
            ("🧹 Limpiar DB", self.limpiar_base_datos_gui)
        ]
        
        for i, (text, command) in enumerate(db_buttons):
            ttk.Button(db_control_frame, text=text, command=command, width=25
                      ).grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Panel de contenido de base de datos
        db_content_frame = ttk.LabelFrame(db_frame, text="📊 Contenido de la Base de Datos", padding="10")
        db_content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        db_content_frame.grid_columnconfigure(0, weight=1)
        db_content_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview para mostrar componentes
        db_columns = ('Categoría', 'Nombre', 'Precio', 'Consumo', 'Marca')
        self.db_tree = ttk.Treeview(db_content_frame, columns=db_columns, show='headings', height=20)
        
        for col in db_columns:
            self.db_tree.heading(col, text=col)
            self.db_tree.column(col, width=120)
        
        db_tree_scroll = ttk.Scrollbar(db_content_frame, orient=tk.VERTICAL, command=self.db_tree.yview)
        self.db_tree.configure(yscrollcommand=db_tree_scroll.set)
        
        self.db_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        db_tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Cargar datos iniciales
        self.actualizar_vista_base_datos()
        
    def crear_pestaña_configuracion(self):
        """Crea la pestaña de configuración de la aplicación"""
        config_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(config_frame, text="⚙️ Configuración")
        
        # Configuración de optimización
        opt_config_frame = ttk.LabelFrame(config_frame, text="🎯 Parámetros de Optimización", padding="10")
        opt_config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        opt_config_frame.grid_columnconfigure(1, weight=1)
        
        # Pesos de la función objetivo
        ttk.Label(opt_config_frame, text="Peso del costo (0-1):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.peso_costo_config = tk.StringVar(value="0.4")
        ttk.Entry(opt_config_frame, textvariable=self.peso_costo_config, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(opt_config_frame, text="Peso del consumo (0-1):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.peso_consumo_config = tk.StringVar(value="0.6")
        ttk.Entry(opt_config_frame, textvariable=self.peso_consumo_config, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(opt_config_frame, text="Factor de seguridad fuente:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.factor_seguridad = tk.StringVar(value="1.3")
        ttk.Entry(opt_config_frame, textvariable=self.factor_seguridad, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Configuración de visualización
        viz_config_frame = ttk.LabelFrame(config_frame, text="📊 Configuración de Visualización", padding="10")
        viz_config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.theme_var = tk.StringVar(value="default")
        ttk.Label(viz_config_frame, text="Tema de gráficos:").grid(row=0, column=0, sticky=tk.W)
        theme_combo = ttk.Combobox(viz_config_frame, textvariable=self.theme_var, 
                                  values=["default", "seaborn", "ggplot", "classic"])
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Configuración de archivos
        file_config_frame = ttk.LabelFrame(config_frame, text="📁 Configuración de Archivos", padding="10")
        file_config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        file_config_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(file_config_frame, text="Archivo de datos:").grid(row=0, column=0, sticky=tk.W)
        self.archivo_datos_var = tk.StringVar(value="data.json")
        ttk.Entry(file_config_frame, textvariable=self.archivo_datos_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        ttk.Button(file_config_frame, text="📁", command=self.seleccionar_archivo_datos, width=3).grid(row=0, column=2, padx=(5, 0))
        
        # Botón de aplicar configuración
        ttk.Button(config_frame, text="✅ Aplicar Configuración", 
                  command=self.aplicar_configuracion).grid(row=3, column=0, pady=20)
        
    def crear_barra_estado(self, parent):
        """Crea la barra de estado"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Listo")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
    def actualizar_info_componentes(self):
        """Actualiza la información de componentes disponibles"""
        self.stats_text.delete(1.0, tk.END)
        
        info = "📊 ESTADÍSTICAS DE COMPONENTES\n" + "="*35 + "\n\n"
        
        total_componentes = 0
        for tipo in ['gabinetes', 'cpus', 'gpus', 'fuentes']:
            componentes = self.optimizador.obtener_componentes_por_tipo(tipo)
            cantidad = len(componentes)
            total_componentes += cantidad
            
            info += f"🔧 {tipo.upper()}: {cantidad} items\n"
            
            if componentes:
                precios = [c.precio for c in componentes]
                consumos = [c.consumo_watts for c in componentes]
                info += f"   💰 Precio: ${min(precios):.0f} - ${max(precios):.0f}\n"
                if any(consumos):
                    info += f"   ⚡ Consumo: {min(consumos):.0f}W - {max(consumos):.0f}W\n"
            info += "\n"
        
        info += f"📦 TOTAL: {total_componentes} componentes\n"
        
        self.stats_text.insert(tk.END, info)
        self.stats_text.config(state=tk.DISABLED)
        
    def generar_configuraciones(self):
        """Genera configuraciones en un hilo separado"""
        def generar():
            self.status_var.set("Generando configuraciones...")
            self.progress.start()
            
            try:
                max_configs = int(self.max_configs_var.get())
                self.configuraciones_generadas = self.optimizador.generar_configuraciones_posibles(max_configs)
                
                self.root.after(0, self.on_configuraciones_generadas)
                
            except Exception as e:
                self.root.after(0, lambda: self.mostrar_error(f"Error al generar configuraciones: {e}"))
            finally:
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=generar, daemon=True).start()
        
    def on_configuraciones_generadas(self):
        """Callback cuando se generan las configuraciones"""
        cantidad = len(self.configuraciones_generadas)
        self.status_var.set(f"✅ {cantidad} configuraciones generadas")
        
        # Actualizar la tabla de configuraciones
        self.actualizar_tabla_configuraciones()
        
        if cantidad > 0:
            messagebox.showinfo("Éxito", f"Se generaron {cantidad} configuraciones válidas")
        else:
            messagebox.showwarning("Advertencia", "No se pudieron generar configuraciones válidas. Verifica los componentes disponibles.")
    
    def actualizar_tabla_configuraciones(self):
        """Actualiza la tabla de configuraciones"""
        # Limpiar tabla
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)
        
        # Agregar configuraciones
        for i, config in enumerate(self.configuraciones_generadas):
            costo = self.optimizador.calcular_costo_total(config)
            consumo = self.optimizador.calcular_consumo_total(config)
            eficiencia = self.optimizador.calcular_eficiencia_energetica(config)
            
            gabinete = config.get('gabinete', {}).nombre if config.get('gabinete') else "N/A"
            cpu = config.get('cpu', {}).nombre if config.get('cpu') else "N/A"
            gpu = config.get('gpu', {}).nombre if config.get('gpu') else "N/A"
            
            self.config_tree.insert('', 'end', values=(
                i+1, f"${costo:.2f}", f"{consumo:.1f}W", f"{eficiencia:.2f}",
                gabinete, cpu, gpu
            ))
    
    def on_config_select(self, event):
        """Maneja la selección de configuración en la tabla"""
        selection = self.config_tree.selection()
        if selection:
            item = self.config_tree.item(selection[0])
            config_id = int(item['values'][0]) - 1
            
            if 0 <= config_id < len(self.configuraciones_generadas):
                config = self.configuraciones_generadas[config_id]
                self.mostrar_detalle_configuracion(config)
    
    def mostrar_detalle_configuracion(self, config):
        """Muestra el detalle de una configuración"""
        detalle = "🖥️ DETALLE DE CONFIGURACIÓN\n" + "="*40 + "\n\n"
        
        for tipo, componente in config.items():
            if componente:
                detalle += f"🔧 {tipo.upper()}:\n"
                detalle += f"   📱 {componente.nombre}\n"
                detalle += f"   💰 ${componente.precio}\n"
                detalle += f"   ⚡ {componente.consumo_watts}W\n"
                detalle += f"   🏭 {componente.marca}\n\n"
        
        # Métricas calculadas
        costo_total = self.optimizador.calcular_costo_total(config)
        consumo_total = self.optimizador.calcular_consumo_total(config)
        eficiencia = self.optimizador.calcular_eficiencia_energetica(config)
        fuente_rec = self.optimizador.recomendar_fuente_poder(consumo_total)
        
        detalle += "📊 MÉTRICAS:\n"
        detalle += f"   💰 Costo total: ${costo_total:.2f}\n"
        detalle += f"   ⚡ Consumo total: {consumo_total:.1f}W\n"
        detalle += f"   📈 Eficiencia: {eficiencia:.2f}\n"
        detalle += f"   🔌 Fuente recomendada: {fuente_rec}W\n"
        
        # Mostrar en el tab de configuración óptima
        self.optimal_text.config(state=tk.NORMAL)
        self.optimal_text.delete(1.0, tk.END)
        self.optimal_text.insert(tk.END, detalle)
        self.optimal_text.config(state=tk.DISABLED)
    
    def encontrar_optima(self):
        """Encuentra la configuración óptima"""
        if not self.configuraciones_generadas:
            messagebox.showwarning("Advertencia", "Primero genera configuraciones")
            return
        
        def encontrar():
            self.status_var.set("Encontrando configuración óptima...")
            self.progress.start()
            
            try:
                self.config_optima = self.optimizador.encontrar_configuracion_optima()
                self.root.after(0, self.on_optima_encontrada)
            except Exception as e:
                self.root.after(0, lambda: self.mostrar_error(f"Error al encontrar óptima: {e}"))
            finally:
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=encontrar, daemon=True).start()
    
    def on_optima_encontrada(self):
        """Callback cuando se encuentra la configuración óptima"""
        if self.config_optima:
            self.mostrar_detalle_configuracion(self.config_optima['configuracion'])
            self.status_var.set("✅ Configuración óptima encontrada")
            messagebox.showinfo("Éxito", "Configuración óptima encontrada y mostrada")
        else:
            messagebox.showerror("Error", "No se pudo encontrar configuración óptima")
    
    # Métodos para visualización
    def mostrar_consumo_vs_costo(self):
        """Muestra gráfico de consumo vs costo"""
        if not self.configuraciones_generadas:
            messagebox.showwarning("Advertencia", "Primero genera configuraciones")
            return
        
        try:
            self.limpiar_panel_visualizacion()
            analisis = self.optimizador.analizar_puntos_criticos_consumo(self.configuraciones_generadas)
            
            if analisis['costos'] and analisis['consumos']:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                
                costos = analisis['costos']
                consumos = analisis['consumos']
                derivadas = analisis['derivadas']
                puntos_criticos = analisis['puntos_criticos']
                
                # Gráfica principal
                ax1.plot(costos, consumos, 'b-', linewidth=2, marker='o', markersize=4)
                for i, punto in enumerate(puntos_criticos):
                    ax1.plot(punto['costo'], punto['consumo'], 'ro', markersize=8)
                
                ax1.set_xlabel('Costo Total ($)')
                ax1.set_ylabel('Consumo Total (W)')
                ax1.set_title('Optimización: Consumo vs Costo')
                ax1.grid(self.show_grid_var.get())
                
                # Gráfica de derivadas
                if len(derivadas) > 2:
                    ax2.plot(costos[1:-1], derivadas[1:-1], 'g-', linewidth=2)
                    ax2.axhline(y=0, color='r', linestyle='--')
                    ax2.set_xlabel('Costo Total ($)')
                    ax2.set_ylabel('Derivada (W/$)')
                    ax2.set_title('Análisis de Derivadas')
                    ax2.grid(self.show_grid_var.get())
                
                self.mostrar_grafico_en_panel(fig)
            
        except Exception as e:
            self.mostrar_error(f"Error en visualización: {e}")
    
    def limpiar_panel_visualizacion(self):
        """Limpia el panel de visualización"""
        for widget in self.viz_panel_frame.winfo_children():
            widget.destroy()
    
    def mostrar_grafico_en_panel(self, fig):
        """Muestra un gráfico matplotlib en el panel"""
        canvas = FigureCanvasTkAgg(fig, self.viz_panel_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        messagebox.showerror("Error", mensaje)
        self.status_var.set("❌ Error")
    
    # Placeholder methods para otras funcionalidades
    def mostrar_comparacion_configs(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def mostrar_analisis_volumenes(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def mostrar_distribucion_precios(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def mostrar_analisis_consumo(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def mostrar_dashboard_completo(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def analizar_puntos_criticos(self):
        """Analiza puntos críticos y muestra resultados"""
        if not self.configuraciones_generadas:
            messagebox.showwarning("Advertencia", "Primero genera configuraciones")
            return
        
        analisis = self.optimizador.analizar_puntos_criticos_consumo(self.configuraciones_generadas)
        
        resultado = "🎯 ANÁLISIS DE PUNTOS CRÍTICOS\n" + "="*50 + "\n\n"
        
        if analisis['puntos_criticos']:
            resultado += f"📊 Se encontraron {len(analisis['puntos_criticos'])} puntos críticos:\n\n"
            for i, punto in enumerate(analisis['puntos_criticos'][:5]):
                resultado += f"Punto {i+1}:\n"
                resultado += f"  💰 Costo: ${punto['costo']:.2f}\n"
                resultado += f"  ⚡ Consumo: {punto['consumo']:.1f}W\n"
                resultado += f"  📈 Derivada: {punto['derivada']:.4f}\n\n"
        else:
            resultado += "No se encontraron puntos críticos en el análisis.\n"
        
        # Estadísticas generales
        if analisis['costos'] and analisis['consumos']:
            resultado += "📈 ESTADÍSTICAS GENERALES:\n"
            resultado += f"  💰 Rango de costos: ${min(analisis['costos']):.2f} - ${max(analisis['costos']):.2f}\n"
            resultado += f"  ⚡ Rango de consumo: {min(analisis['consumos']):.1f}W - {max(analisis['consumos']):.1f}W\n"
        
        self.math_text.config(state=tk.NORMAL)
        self.math_text.delete(1.0, tk.END)
        self.math_text.insert(tk.END, resultado)
        self.math_text.config(state=tk.DISABLED)
        
        # Cambiar al tab de análisis
        self.result_notebook.select(2)
    
    # Métodos para gestión de base de datos (placeholders)
    def mostrar_componentes(self):
        self.actualizar_vista_base_datos()
        messagebox.showinfo("Info", "Vista de componentes actualizada")
    
    def actualizar_vista_base_datos(self):
        """Actualiza la vista de la base de datos"""
        # Limpiar tree
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)
        
        # Cargar datos
        for categoria, componentes in self.gestor_db.datos.items():
            for comp in componentes:
                self.db_tree.insert('', 'end', values=(
                    categoria.title(),
                    comp.get('nombre', ''),
                    f"${comp.get('precio', 0):.2f}",
                    f"{comp.get('consumo_watts', 0)}W",
                    comp.get('marca', '')
                ))
    
    def agregar_componente_gui(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def buscar_componentes_gui(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def mostrar_estadisticas_db(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def validar_integridad_gui(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def exportar_datos(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def importar_datos(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def limpiar_base_datos_gui(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def exportar_configuracion_optima(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def copiar_configuracion(self):
        messagebox.showinfo("Info", "Funcionalidad en desarrollo")
    
    def seleccionar_archivo_datos(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if archivo:
            self.archivo_datos_var.set(archivo)
    
    def aplicar_configuracion(self):
        """Aplica la configuración modificada"""
        try:
            # Actualizar pesos
            peso_costo = float(self.peso_costo_config.get())
            peso_consumo = float(self.peso_consumo_config.get())
            
            if peso_costo + peso_consumo != 1.0:
                messagebox.showwarning("Advertencia", "Los pesos deben sumar 1.0")
                return
            
            # Aplicar tema de gráficos
            plt.style.use(self.theme_var.get())
            
            messagebox.showinfo("Éxito", "Configuración aplicada correctamente")
            self.status_var.set("✅ Configuración actualizada")
            
        except ValueError:
            messagebox.showerror("Error", "Valores numéricos inválidos")
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

def main():
    """Función principal"""
    app = InterfazOptimizadorPC()
    app.ejecutar()

if __name__ == "__main__":
    main()