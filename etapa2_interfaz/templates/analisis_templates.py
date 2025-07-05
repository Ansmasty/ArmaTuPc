"""
Templates HTML y formateo de texto para el análisis matemático
Contiene templates que se usan para generar la presentación de los análisis
"""

def generar_resumen_html(params):
    """
    Genera el HTML para el resumen matemático
    
    Args:
        params: Diccionario con todos los parámetros necesarios para el template
    
    Returns:
        Cadena con el HTML formateado
    """
    return f"""<h2 style='text-align:center;'>ANÁLISIS MATEMÁTICO DEL BUILD</h2>
                        
<h3>📊 PARÁMETROS FÍSICOS DEL SISTEMA:</h3>
• <b>Potencia Total:</b> {params['potencia_total']:.1f} W
• <b>Temperatura Ambiente:</b> {params['temp_ambiente']:.1f} °C
• <b>Volumen del Gabinete:</b> {params['volumen_case']:.1f} L
• <b>Ventiladores:</b> {params['fan_count']} ({params['fan_capacity']:.1f} CFM estimado)

<h3>🧮 MODELO TÉRMICO DIFERENCIAL:</h3>
<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>
    <p style='font-family: monospace; font-size: 14px;'>T(P) = Tₐ + (P·k) / (V^(1/3)·F)</p>
    <p>Donde:</p>
    <ul>
        <li>T: Temperatura interna (°C)</li>
        <li>Tₐ: Temperatura ambiente ({params['temp_ambiente']:.1f}°C)</li>
        <li>P: Potencia disipada ({params['potencia_total']:.1f}W)</li>
        <li>V: Volumen normalizado del gabinete</li>
        <li>F: Factor de ventilación ({params['f_factor']:.2f})</li>
    </ul>
</div>

<h3>🔥 ANÁLISIS DE TEMPERATURA:</h3>
• <b>Temperatura Actual:</b> {params['temp_actual']:.1f} °C
• <b>Δ Temperatura:</b> +{params['delta_t']:.1f} °C sobre ambiente
• <b>Derivada (∂T/∂P):</b> {params['sensibilidad_termica']:.3f} °C/W
<div style='background-color: #f9f9f9; padding: 8px; margin-left: 15px; border-left: 3px solid #007bff;'>
    <i>La derivada representa la sensibilidad térmica: por cada watt adicional, 
    la temperatura aumenta {params['sensibilidad_termica']:.3f}°C.</i>
</div>

<h3>⚡ ANÁLISIS DE EFICIENCIA:</h3>
• <b>Modelo:</b> η(T) = 1/(1 + e^((T-Tₐ)/10))
• <b>Eficiencia Térmica:</b> {params['eficiencia']*100:.1f}%
• <b>Derivada (∂η/∂P):</b> {params['sensibilidad_eficiencia']:.6f} %/W
• <b>Punto Óptimo Teórico:</b> {params['potencia_optima']:.1f} W
<div style='background-color: #f9f9f9; padding: 8px; margin-left: 15px; border-left: 3px solid #ff9800;'>
    <i>La derivada de eficiencia negativa significa que al aumentar la potencia,
    la eficiencia disminuye a razón de {abs(params['sensibilidad_eficiencia']*100):.4f}% por watt.</i>
</div>

<h3>📈 INTERPRETACIÓN MATEMÁTICA:</h3>
• El sistema opera al {params['relacion_potencia']:.1f}% de su capacidad óptima.
• La curva térmica muestra {params['interpretacion_curva']}
• La eficiencia del sistema es {params['interpretacion_eficiencia']}

<div style='text-align: right; font-style: italic; margin-top: 20px; color: #666;'>
Análisis basado en cálculo diferencial aplicado a sistemas termofísicos
</div>
"""

def generar_resumen_simple(params):
    """
    Genera un resumen matemático en texto plano sin HTML
    
    Args:
        params: Diccionario con los parámetros necesarios
    
    Returns:
        Cadena con el resumen en texto plano
    """
    return f"""ANÁLISIS MATEMÁTICO DEL BUILD
=================================

PARÁMETROS FÍSICOS DEL SISTEMA:
• Potencia Total: {params['potencia_total']:.1f} W
• Temperatura Ambiente: {params['temp_ambiente']:.1f} °C
• Volumen del Gabinete: {params['volumen_case']:.1f} L
• Ventiladores: {params['fan_count']} ({params['fan_capacity']:.1f} CFM estimado)

MODELO TÉRMICO DIFERENCIAL:
T(P) = Tₐ + (P·k) / (V^(1/3)·F)

ANÁLISIS DE TEMPERATURA:
• Temperatura Actual: {params['temp_actual']:.1f} °C
• Δ Temperatura: +{params['delta_t']:.1f} °C sobre ambiente
• Derivada (∂T/∂P): {params['sensibilidad_termica']:.3f} °C/W

ANÁLISIS DE EFICIENCIA:
• Modelo: η(T) = 1/(1 + e^((T-Tₐ)/10))
• Eficiencia Térmica: {params['eficiencia']*100:.1f}%
• Derivada (∂η/∂P): {params['sensibilidad_eficiencia']:.6f} %/W
• Punto Óptimo Teórico: {params['potencia_optima']:.1f} W

INTERPRETACIÓN MATEMÁTICA:
• El sistema opera al {params['relacion_potencia']:.1f}% de su capacidad óptima.
• {params['interpretacion_curva']}
• {params['interpretacion_eficiencia']}
"""
