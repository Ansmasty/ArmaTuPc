"""
Módulo para visualización de datos y análisis gráfico
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
import seaborn as sns
from main import OptimizadorPC

class VisualizadorPC:
    """Clase para generar visualizaciones del análisis"""
    
    def __init__(self, optimizador: OptimizadorPC = None):
        plt.style.use('default')  # Cambiar de seaborn-v0_8 a default
        sns.set_palette("husl")
        self.optimizador = optimizador or OptimizadorPC("data.json")
    
    def menu_principal(self):
        """Menú principal de visualizaciones"""
        while True:
            print("\n" + "="*50)
            print("📊 VISUALIZADOR DE ANÁLISIS PC")
            print("="*50)
            print("1. 📈 Análisis Consumo vs Costo")
            print("2. 🎯 Comparación de Configuraciones")
            print("3. 📦 Análisis de Volúmenes")
            print("4. 💰 Distribución de Precios por Categoría")
            print("5. ⚡ Análisis de Consumo Energético")
            print("6. 🏆 Dashboard Completo")
            print("0. 🚪 Salir")
            print("-"*50)
            
            try:
                opcion = input("Selecciona una opción: ").strip()
                
                if opcion == "1":
                    self.ejecutar_analisis_consumo_costo()
                elif opcion == "2":
                    self.ejecutar_comparacion_configuraciones()
                elif opcion == "3":
                    self.ejecutar_analisis_volumenes()
                elif opcion == "4":
                    self.graficar_distribucion_precios()
                elif opcion == "5":
                    self.graficar_analisis_consumo()
                elif opcion == "6":
                    self.crear_dashboard_completo()
                elif opcion == "0":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida")
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def ejecutar_analisis_consumo_costo(self):
        """Ejecuta el análisis de consumo vs costo"""
        print("\n📈 Generando análisis consumo vs costo...")
        
        # Generar configuraciones
        configuraciones = self.optimizador.generar_configuraciones_posibles(30)
        
        if len(configuraciones) < 3:
            print("❌ Necesitas al menos 3 configuraciones para el análisis")
            return
        
        # Realizar análisis
        analisis = self.optimizador.analizar_puntos_criticos_consumo(configuraciones)
        
        if analisis['costos'] and analisis['consumos']:
            self.graficar_consumo_vs_costo(analisis)
        else:
            print("❌ No se pudieron generar datos suficientes para el análisis")
    
    def ejecutar_comparacion_configuraciones(self):
        """Ejecuta comparación de configuraciones"""
        print("\n🎯 Generando comparación de configuraciones...")
        
        configuraciones = self.optimizador.generar_configuraciones_posibles(10)
        
        if len(configuraciones) < 2:
            print("❌ Necesitas al menos 2 configuraciones para comparar")
            return
        
        # Preparar datos para comparación
        configs_con_metricas = []
        nombres = []
        
        for i, config in enumerate(configuraciones[:5]):  # Máximo 5 para claridad
            metricas = {
                'costo_normalizado': self.normalizar_valor(
                    self.optimizador.calcular_costo_total(config),
                    [self.optimizador.calcular_costo_total(c) for c in configuraciones]
                ),
                'consumo_normalizado': self.normalizar_valor(
                    self.optimizador.calcular_consumo_total(config),
                    [self.optimizador.calcular_consumo_total(c) for c in configuraciones]
                ),
                'eficiencia_normalizada': self.normalizar_valor(
                    self.optimizador.calcular_eficiencia_energetica(config),
                    [self.optimizador.calcular_eficiencia_energetica(c) for c in configuraciones],
                    invertir=True  # Mayor eficiencia es mejor
                ),
                'compatibilidad': 1.0 if self.optimizador.verificar_compatibilidad_fisica(config) else 0.0
            }
            configs_con_metricas.append(metricas)
            nombres.append(f"Config {i+1}")
        
        self.graficar_comparacion_configuraciones(configs_con_metricas, nombres)
    
    def normalizar_valor(self, valor: float, lista_valores: List[float], invertir: bool = False) -> float:
        """Normaliza un valor entre 0 y 1"""
        if not lista_valores or max(lista_valores) == min(lista_valores):
            return 0.5
        
        normalizado = (valor - min(lista_valores)) / (max(lista_valores) - min(lista_valores))
        return 1 - normalizado if invertir else normalizado
    
    def ejecutar_analisis_volumenes(self):
        """Ejecuta análisis de volúmenes"""
        print("\n📦 Generando análisis de volúmenes...")
        
        configuraciones = self.optimizador.generar_configuraciones_posibles(5)
        
        if not configuraciones:
            print("❌ No hay configuraciones disponibles")
            return
        
        # Tomar la primera configuración como ejemplo
        config_ejemplo = configuraciones[0]
        self.graficar_volumen_componentes(config_ejemplo)
    
    def graficar_consumo_vs_costo(self, analisis: Dict):
        """Gráfica de consumo energético vs costo con puntos críticos"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        costos = analisis['costos']
        consumos = analisis['consumos']
        derivadas = analisis['derivadas']
        puntos_criticos = analisis['puntos_criticos']
        
        # Gráfica principal: Consumo vs Costo
        ax1.plot(costos, consumos, 'b-', linewidth=2, label='Consumo vs Costo', marker='o', markersize=4)
        
        # Marcar puntos críticos
        for i, punto in enumerate(puntos_criticos):
            ax1.plot(punto['costo'], punto['consumo'], 'ro', markersize=10, 
                    label=f"Punto crítico {i+1}: ${punto['costo']:.0f}")
        
        ax1.set_xlabel('Costo Total ($)')
        ax1.set_ylabel('Consumo Total (W)')
        ax1.set_title('Optimización: Consumo Energético vs Costo', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Gráfica de derivadas
        if len(derivadas) > 2:
            ax2.plot(costos[1:-1], derivadas[1:-1], 'g-', linewidth=2, 
                    label='dConsumo/dCosto', marker='s', markersize=3)
            ax2.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Línea de referencia')
            ax2.set_xlabel('Costo Total ($)')
            ax2.set_ylabel('Derivada (W/$)')
            ax2.set_title('Análisis de Derivadas - Puntos Críticos', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        else:
            ax2.text(0.5, 0.5, 'Datos insuficientes para análisis de derivadas', 
                    ha='center', va='center', transform=ax2.transAxes)
        
        plt.tight_layout()
        plt.show()
        
        # Mostrar resumen
        if puntos_criticos:
            print(f"\n🎯 Puntos críticos encontrados: {len(puntos_criticos)}")
            for i, punto in enumerate(puntos_criticos[:3]):
                print(f"   {i+1}. Costo: ${punto['costo']:.2f}, Consumo: {punto['consumo']:.1f}W")
    
    def graficar_comparacion_configuraciones(self, configuraciones: List[Dict], nombres: List[str]):
        """Compara múltiples configuraciones en un gráfico de radar"""
        from math import pi
        
        categorias = ['Costo', 'Consumo', 'Eficiencia', 'Compatibilidad']
        num_vars = len(categorias)
        
        # Calcular ángulos para cada eje
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        angles += angles[:1]  # Completar el círculo
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(configuraciones)))
        
        for i, config in enumerate(configuraciones):
            # Obtener valores normalizados
            valores = [
                1 - config.get('costo_normalizado', 0),  # Invertir costo (menor es mejor)
                1 - config.get('consumo_normalizado', 0),  # Invertir consumo (menor es mejor)
                config.get('eficiencia_normalizada', 0),
                config.get('compatibilidad', 0)
            ]
            valores += valores[:1]
            
            ax.plot(angles, valores, 'o-', linewidth=2, label=nombres[i], color=colors[i])
            ax.fill(angles, valores, alpha=0.25, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categorias)
        ax.set_ylim(0, 1)
        ax.set_title('Comparación de Configuraciones de PC', size=16, fontweight='bold', y=1.1)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.show()
    
    def graficar_volumen_componentes(self, configuracion: Dict):
        """Gráfica de volúmenes de componentes vs espacio disponible"""
        nombres = []
        volumenes = []
        colores = ['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum']
        
        for i, (tipo, componente) in enumerate(configuracion.items()):
            if componente and hasattr(componente, 'volumen'):
                nombres.append(f"{tipo.upper()}")
                volumenes.append(componente.volumen() / 1000000)  # Convertir a cm³
        
        plt.figure(figsize=(12, 6))
        barras = plt.bar(nombres, volumenes, color=colores[:len(nombres)], 
                        edgecolor='navy', alpha=0.7, linewidth=1.5)
        
        # Agregar valores en las barras
        for barra, volumen in zip(barras, volumenes):
            height = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2., height + max(volumenes)*0.01,
                    f'{volumen:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Línea de referencia del volumen del gabinete
        if 'gabinete' in configuracion and configuracion['gabinete']:
            volumen_gabinete = configuracion['gabinete'].volumen_interno / 1000000
            limite_recomendado = volumen_gabinete * 0.8
            plt.axhline(y=limite_recomendado, color='red', linestyle='--', linewidth=2,
                       label=f'Límite recomendado: {limite_recomendado:.0f} cm³')
            plt.axhline(y=volumen_gabinete, color='orange', linestyle='-', alpha=0.7,
                       label=f'Volumen total gabinete: {volumen_gabinete:.0f} cm³')
        
        plt.xlabel('Componentes', fontsize=12, fontweight='bold')
        plt.ylabel('Volumen (cm³)', fontsize=12, fontweight='bold')
        plt.title('Análisis de Volúmenes - Compatibilidad Física', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.show()
        
        # Mostrar resumen
        volumen_total_componentes = sum(volumenes)
        if 'gabinete' in configuracion and configuracion['gabinete']:
            porcentaje_ocupado = (volumen_total_componentes / (configuracion['gabinete'].volumen_interno / 1000000)) * 100
            print(f"\n📊 Resumen de volúmenes:")
            print(f"   Total componentes: {volumen_total_componentes:.1f} cm³")
            print(f"   Porcentaje ocupado: {porcentaje_ocupado:.1f}%")
            print(f"   Estado: {'✅ Compatible' if porcentaje_ocupado <= 80 else '❌ Sobrecargado'}")
    
    def graficar_distribucion_precios(self):
        """Gráfica la distribución de precios por categoría"""
        plt.figure(figsize=(14, 8))
        
        categorias_datos = []
        precios_datos = []
        
        for categoria, componentes in self.optimizador.componentes_disponibles.items():
            if componentes:
                for comp in componentes:
                    categorias_datos.append(categoria.replace('_', ' ').title())
                    precios_datos.append(comp.get('precio', 0))
        
        if not precios_datos:
            print("❌ No hay datos de precios disponibles")
            return
        
        # Crear boxplot
        categorias_unicas = list(set(categorias_datos))
        precios_por_categoria = []
        
        for categoria in categorias_unicas:
            precios_cat = [precio for cat, precio in zip(categorias_datos, precios_datos) if cat == categoria]
            precios_por_categoria.append(precios_cat)
        
        plt.boxplot(precios_por_categoria, labels=categorias_unicas)
        plt.xlabel('Categorías', fontsize=12, fontweight='bold')
        plt.ylabel('Precio ($)', fontsize=12, fontweight='bold')
        plt.title('Distribución de Precios por Categoría', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def graficar_analisis_consumo(self):
        """Gráfica análisis de consumo energético"""
        configuraciones = self.optimizador.generar_configuraciones_posibles(20)
        
        if not configuraciones:
            print("❌ No hay configuraciones disponibles")
            return
        
        consumos = [self.optimizador.calcular_consumo_total(config) for config in configuraciones]
        costos = [self.optimizador.calcular_costo_total(config) for config in configuraciones]
        eficiencias = [self.optimizador.calcular_eficiencia_energetica(config) for config in configuraciones]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Histograma de consumos
        ax1.hist(consumos, bins=10, alpha=0.7, color='lightblue', edgecolor='black')
        ax1.set_xlabel('Consumo (W)')
        ax1.set_ylabel('Frecuencia')
        ax1.set_title('Distribución de Consumo Energético')
        ax1.grid(True, alpha=0.3)
        
        # Scatter plot consumo vs costo
        ax2.scatter(costos, consumos, alpha=0.7, color='green')
        ax2.set_xlabel('Costo ($)')
        ax2.set_ylabel('Consumo (W)')
        ax2.set_title('Relación Costo vs Consumo')
        ax2.grid(True, alpha=0.3)
        
        # Eficiencia energética
        indices = range(len(eficiencias))
        ax3.bar(indices, eficiencias, alpha=0.7, color='orange')
        ax3.set_xlabel('Configuración')
        ax3.set_ylabel('Eficiencia')
        ax3.set_title('Índice de Eficiencia Energética')
        ax3.grid(True, alpha=0.3)
        
        # Recomendaciones de fuente
        fuentes_recomendadas = [self.optimizador.recomendar_fuente_poder(consumo) for consumo in consumos]
        fuentes_unicas, conteos = np.unique(fuentes_recomendadas, return_counts=True)
        ax4.pie(conteos, labels=[f'{f}W' for f in fuentes_unicas], autopct='%1.1f%%')
        ax4.set_title('Distribución de Fuentes Recomendadas')
        
        plt.tight_layout()
        plt.show()
    
    def crear_dashboard_completo(self):
        """Crea un dashboard completo con múltiples métricas"""
        print("\n🏆 Generando dashboard completo...")
        
        configuraciones = self.optimizador.generar_configuraciones_posibles(15)
        
        if len(configuraciones) < 5:
            print("❌ Necesitas al menos 5 configuraciones para el dashboard")
            return
        
        # Calcular todas las métricas
        metricas = []
        for config in configuraciones:
            metricas.append({
                'costo': self.optimizador.calcular_costo_total(config),
                'consumo': self.optimizador.calcular_consumo_total(config),
                'eficiencia': self.optimizador.calcular_eficiencia_energetica(config),
                'volumen': sum(comp.volumen() for comp in config.values() if comp and hasattr(comp, 'volumen')) / 1000000,
                'fuente_rec': self.optimizador.recomendar_fuente_poder(self.optimizador.calcular_consumo_total(config))
            })
        
        # Crear dashboard
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Consumo vs Costo
        ax1 = fig.add_subplot(gs[0, 0])
        costos = [m['costo'] for m in metricas]
        consumos = [m['consumo'] for m in metricas]
        ax1.scatter(costos, consumos, alpha=0.7, s=50)
        ax1.set_xlabel('Costo ($)')
        ax1.set_ylabel('Consumo (W)')
        ax1.set_title('Costo vs Consumo')
        ax1.grid(True, alpha=0.3)
        
        # 2. Distribución de eficiencia
        ax2 = fig.add_subplot(gs[0, 1])
        eficiencias = [m['eficiencia'] for m in metricas]
        ax2.hist(eficiencias, bins=8, alpha=0.7, color='lightgreen', edgecolor='black')
        ax2.set_xlabel('Eficiencia')
        ax2.set_ylabel('Frecuencia')
        ax2.set_title('Distribución de Eficiencia')
        ax2.grid(True, alpha=0.3)
        
        # 3. Top 5 configuraciones por eficiencia
        ax3 = fig.add_subplot(gs[0, 2])
        indices_top = sorted(range(len(eficiencias)), key=lambda i: eficiencias[i], reverse=True)[:5]
        top_configs = [f'Config {i+1}' for i in indices_top]
        top_eficiencias = [eficiencias[i] for i in indices_top]
        ax3.barh(top_configs, top_eficiencias, color='gold', alpha=0.7)
        ax3.set_xlabel('Eficiencia')
        ax3.set_title('Top 5 Configuraciones')
        ax3.grid(True, alpha=0.3)
        
        # 4. Relación volumen vs costo
        ax4 = fig.add_subplot(gs[1, 0])
        volumenes = [m['volumen'] for m in metricas]
        ax4.scatter(volumenes, costos, alpha=0.7, color='purple')
        ax4.set_xlabel('Volumen Total (cm³)')
        ax4.set_ylabel('Costo ($)')
        ax4.set_title('Volumen vs Costo')
        ax4.grid(True, alpha=0.3)
        
        # 5. Fuentes recomendadas
        ax5 = fig.add_subplot(gs[1, 1])
        fuentes = [m['fuente_rec'] for m in metricas]
        fuentes_unicas, conteos = np.unique(fuentes, return_counts=True)
        ax5.pie(conteos, labels=[f'{f}W' for f in fuentes_unicas], autopct='%1.1f%%')
        ax5.set_title('Fuentes Recomendadas')
        
        # 6. Matriz de correlación
        ax6 = fig.add_subplot(gs[1, 2])
        datos_matriz = np.array([costos, consumos, eficiencias, volumenes])
        correlacion = np.corrcoef(datos_matriz)
        im = ax6.imshow(correlacion, cmap='coolwarm', aspect='auto')
        ax6.set_xticks(range(4))
        ax6.set_yticks(range(4))
        ax6.set_xticklabels(['Costo', 'Consumo', 'Eficiencia', 'Volumen'], rotation=45)
        ax6.set_yticklabels(['Costo', 'Consumo', 'Eficiencia', 'Volumen'])
        ax6.set_title('Correlaciones')
        plt.colorbar(im, ax=ax6)
        
        # 7. Resumen estadístico (texto)
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('off')
        
        # Calcular estadísticas
        costo_promedio = np.mean(costos)
        consumo_promedio = np.mean(consumos)
        eficiencia_promedio = np.mean(eficiencias)
        
        mejor_config_idx = indices_top[0]
        mejor_config = configuraciones[mejor_config_idx]
        
        texto_resumen = f"""
📊 RESUMEN EJECUTIVO DEL ANÁLISIS
{'='*80}
📈 Configuraciones analizadas: {len(configuraciones)}
💰 Costo promedio: ${costo_promedio:.2f} (rango: ${min(costos):.2f} - ${max(costos):.2f})
⚡ Consumo promedio: {consumo_promedio:.1f}W (rango: {min(consumos):.1f}W - {max(consumos):.1f}W)
📊 Eficiencia promedio: {eficiencia_promedio:.2f}

🏆 MEJOR CONFIGURACIÓN (Config {mejor_config_idx + 1}):
   💰 Costo: ${metricas[mejor_config_idx]['costo']:.2f}
   ⚡ Consumo: {metricas[mejor_config_idx]['consumo']:.1f}W
   📊 Eficiencia: {metricas[mejor_config_idx]['eficiencia']:.2f}
   🔌 Fuente recomendada: {metricas[mejor_config_idx]['fuente_rec']}W
        """
        
        ax7.text(0.05, 0.95, texto_resumen, transform=ax7.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')
        
        plt.suptitle('🖥️ DASHBOARD COMPLETO - OPTIMIZACIÓN DE PC', fontsize=16, fontweight='bold')
        plt.show()
        
        print("✅ Dashboard generado exitosamente")

def main():
    """Función principal para visualizaciones"""
    print("📊 Iniciando Visualizador de Análisis PC...")
    
    # Crear optimizador y visualizador
    optimizador = OptimizadorPC("data.json")
    visualizador = VisualizadorPC(optimizador)
    
    # Mostrar menú
    visualizador.menu_principal()

if __name__ == "__main__":
    main()