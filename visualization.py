"""
Módulo de Visualización de Datos Financieros (BTCUSD)
Genera gráficos estandarizados con matplotlib/seaborn cumpliendo los
requisitos de título, unidades, ejes y período expresado en UTC.
"""

import os
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para segundo plano
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Configuración de estilo global
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
COLOR_PRINCIPAL = '#1f77b4'
COLOR_ALCISTA = '#2ca02c'
COLOR_BAJISTA = '#d62728'
COLOR_DESTACADO = '#ff7f0e'


def _obtener_string_periodo(df: pd.DataFrame) -> str:
    """Extrae el rango de fechas en UTC para incrustar en los títulos/subtítulos."""
    if 'time' not in df.columns or df.empty:
        return "Período: N/A"
    
    fechas = pd.to_datetime(df['time'], utc=True)
    f_min = fechas.min().strftime('%Y-%m-%d %H:%M UTC')
    f_max = fechas.max().strftime('%Y-%m-%d %H:%M UTC')
    return f"Período analizado (UTC): {f_min} a {f_max}"


def _asegurar_directorio(carpeta: str):
    """Crea la carpeta de destino si no existe."""
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)


# ==============================================================================
# ACTIVIDADES DE PRECIO Y TENDENCIA (Actividades 6, 7, 8, 9, 10, 11, 12)
# ==============================================================================

def graficar_actividad_6_evolucion_precio(df: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividad 6: Evolución del precio de cierre con señalamiento de Máximo y Mínimo.
    """
    _asegurar_directorio(carpeta_salida)
    df_calc = df.copy()
    df_calc['time'] = pd.to_datetime(df_calc['time'], utc=True)
    
    idx_max = df_calc['high'].idxmax()
    idx_min = df_calc['low'].idxmin()
    
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df_calc['time'], df_calc['close'], label='Precio Cierre (USD)', color=COLOR_PRINCIPAL, linewidth=1.5)
    
    # Destacar Máximo y Mínimo
    ax.scatter(df_calc.loc[idx_max, 'time'], df_calc.loc[idx_max, 'high'], color=COLOR_ALCISTA, s=100, zorder=5, label=f"Máximo: ${df_calc.loc[idx_max, 'high']:.2f}")
    ax.scatter(df_calc.loc[idx_min, 'time'], df_calc.loc[idx_min, 'low'], color=COLOR_BAJISTA, s=100, zorder=5, label=f"Mínimo: ${df_calc.loc[idx_min, 'low']:.2f}")
    
    periodo = _obtener_string_periodo(df_calc)
    ax.set_title(f"Actividad 6: Evolución del Precio de Cierre de Hedera (HBARUSD)\n{periodo}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Fecha y Hora (UTC)", fontsize=10)
    ax.set_ylabel("Precio de Cierre (USD)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_06_evolucion_precio.png"), dpi=120)
    plt.close()


def graficar_actividad_7_top_rangos(df_top: pd.DataFrame, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividad 7: Las 10 velas con mayor rango (High - Low).
    """
    _asegurar_directorio(carpeta_salida)
    df_plot = df_top.copy()
    df_plot['fecha_str'] = pd.to_datetime(df_plot['time'], utc=True).dt.strftime('%m-%d %H:%M')
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(df_plot['fecha_str'], df_plot['rango'], color=COLOR_PRINCIPAL, edgecolor='black', alpha=0.8)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
        
    ax.set_title(f"Actividad 7: Top 10 Velas con Mayor Rango (High - Low)\n{periodo_str}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Fecha y Hora (UTC)", fontsize=10)
    ax.set_ylabel("Rango de Precio (USD)", fontsize=10)
    plt.xticks(rotation=45)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_07_top_rangos.png"), dpi=120)
    plt.close()


def graficar_actividad_8_9_top_cambios(df_subidas: pd.DataFrame, df_caidas: pd.DataFrame, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividades 8 y 9: Top 10 mayores subidas y mayores caídas porcentuales.
    """
    _asegurar_directorio(carpeta_salida)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Subidas
    sub = df_subidas.copy()
    sub['fecha_str'] = pd.to_datetime(sub['time'], utc=True).dt.strftime('%m-%d %H:%M')
    ax1.bar(sub['fecha_str'], sub['cambio_pct'], color=COLOR_ALCISTA, edgecolor='black')
    ax1.set_title("Actividad 8: Top 10 Mayores Subidas Horarias (%)", fontsize=10, fontweight='bold')
    ax1.set_xlabel("Fecha y Hora (UTC)", fontsize=9)
    ax1.set_ylabel("Cambio Porcentual (%)", fontsize=9)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    # Caídas
    cai = df_caidas.copy()
    cai['fecha_str'] = pd.to_datetime(cai['time'], utc=True).dt.strftime('%m-%d %H:%M')
    ax2.bar(cai['fecha_str'], cai['cambio_pct'], color=COLOR_BAJISTA, edgecolor='black')
    ax2.set_title("Actividad 9: Top 10 Mayores Caídas Horarias (%)", fontsize=10, fontweight='bold')
    ax2.set_xlabel("Fecha y Hora (UTC)", fontsize=9)
    ax2.set_ylabel("Cambio Porcentual (%)", fontsize=9)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    fig.suptitle(f"Análisis de Movimientos Extremos Porcentuales\n{periodo_str}", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_08_09_top_subidas_caidas.png"), dpi=120)
    plt.close()


def graficar_actividad_10_clasificacion_velas(df_clasif: pd.DataFrame, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividad 10: Distribución de Velas Alcistas vs Bajistas vs Doji.
    """
    _asegurar_directorio(carpeta_salida)
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colores = {'Alcista': COLOR_ALCISTA, 'Bajista': COLOR_BAJISTA, 'Doji': 'gray'}
    bars_colors = [colores.get(tipo, COLOR_PRINCIPAL) for tipo in df_clasif['Tipo_Vela']]
    
    bars = ax.bar(df_clasif['Tipo_Vela'], df_clasif['Cantidad'], color=bars_colors, edgecolor='black', alpha=0.85)
    
    for bar, prop in zip(bars, df_clasif['Proporcion_Pct']):
        height = bar.get_height()
        ax.annotate(f"{height} ({prop:.1f}%)",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    ax.set_title(f"Actividad 10: Clasificación de Velas Horarias\n{periodo_str}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Tipo de Vela", fontsize=10)
    ax.set_ylabel("Cantidad de Velas (Unidades)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_10_clasificacion_velas.png"), dpi=120)
    plt.close()


def graficar_actividad_11_12_resumen_diario(df_resumen: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividades 11 y 12: Evolución del cierre diario y variación porcentual por día.
    """
    _asegurar_directorio(carpeta_salida)
    df_p = df_resumen.copy()
    df_p['fecha_str'] = pd.to_datetime(df_p['fecha']).dt.strftime('%Y-%m-%d')
    
    fig, ax1 = plt.subplots(figsize=(11, 5))
    
    color_bar = [COLOR_ALCISTA if c >= 0 else COLOR_BAJISTA for c in df_p['Cambio (%)']]
    ax1.bar(df_p['fecha_str'], df_p['Cambio (%)'], color=color_bar, alpha=0.6, label='Cambio Diario (%)')
    ax1.set_xlabel("Fecha (UTC)", fontsize=10)
    ax1.set_ylabel("Cambio Porcentual Diario (%)", fontsize=10, color='black')
    ax1.tick_params(axis='x', rotation=45)
    
    ax2 = ax1.twinx()
    ax2.plot(df_p['fecha_str'], df_p['Cierre'], color=COLOR_PRINCIPAL, marker='o', linewidth=2, label='Precio Cierre (USD)')
    ax2.set_ylabel("Precio de Cierre (USD)", fontsize=10, color=COLOR_PRINCIPAL)
    
    f_min = df_p['fecha_str'].iloc[0]
    f_max = df_p['fecha_str'].iloc[-1]
    
    plt.title(f"Actividades 11 y 12: Evolución y Rendimiento Diario de HBAR\nPeríodo (UTC): {f_min} a {f_max}", fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_11_12_resumen_diario.png"), dpi=120)
    plt.close()


# ==============================================================================
# ACTIVIDADES PATRONES TEMPORALES Y TECNICOS (Actividades 13, 14, 15, 16, 17, 18)
# ==============================================================================

def graficar_actividad_13_promedio_por_hora(df_hora: pd.DataFrame, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividad 13: Movimiento porcentual promedio por hora del día (0 a 23h UTC).
    """
    _asegurar_directorio(carpeta_salida)
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(df_hora['Hora_UTC'], df_hora['Movimiento_Promedio_Pct'], marker='s', color=COLOR_PRINCIPAL, linewidth=2)
    
    # Destacar hora pico
    idx_pico = df_hora['Movimiento_Promedio_Pct'].idxmax()
    hora_pico = df_hora.loc[idx_pico, 'Hora_UTC']
    val_pico = df_hora.loc[idx_pico, 'Movimiento_Promedio_Pct']
    ax.scatter(hora_pico, val_pico, color=COLOR_DESTACADO, s=120, zorder=5, label=f"Pico: Hora {int(hora_pico)}:00 UTC ({val_pico:.2f}%)")
    
    ax.set_title(f"Actividad 13: Comportamiento Promedio por Hora del Día\n{periodo_str}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Hora del Día (Formato 24h UTC)", fontsize=10)
    ax.set_ylabel("Movimiento Absoluto Promedio (%)", fontsize=10)
    ax.set_xticks(range(0, 24))
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_13_comportamiento_hora_utc.png"), dpi=120)
    plt.close()


def graficar_actividad_14_dia_semana(df_dias: pd.DataFrame, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividad 14: Comparación del rango porcentual por día de la semana.
    """
    _asegurar_directorio(carpeta_salida)
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(df_dias['Dia_Semana'], df_dias['Rango_Promedio_Pct'], color=COLOR_PRINCIPAL, edgecolor='black', alpha=0.8)
    
    ax.set_title(f"Actividad 14: Volatilidad Promedio por Día de la Semana\n{periodo_str}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Día de la Semana", fontsize=10)
    ax.set_ylabel("Rango Promedio (High - Low) / Open (%)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_14_comportamiento_dia_semana.png"), dpi=120)
    plt.close()


def graficar_actividad_15_media_movil(df_sma: pd.DataFrame, window: int = 20, carpeta_salida="graficas"):
    """
    Actividad 15: Precio de Cierre + Media Móvil (SMA 20) y cruces alcistas.
    """
    _asegurar_directorio(carpeta_salida)
    df_p = df_sma.copy()
    df_p['time'] = pd.to_datetime(df_p['time'], utc=True)
    
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df_p['time'], df_p['close'], label='Precio Cierre (USD)', color='black', alpha=0.7, linewidth=1.2)
    ax.plot(df_p['time'], df_p[f'SMA_{window}'], label=f'Media Móvil (SMA {window})', color=COLOR_DESTACADO, linewidth=2)
    
    # Marcadores de cruce alcista
    cruces = df_p[df_p['cruce_alcista'] == True]
    ax.scatter(cruces['time'], cruces['close'], color=COLOR_ALCISTA, marker='^', s=90, zorder=5, label='Cruce Alcista (Cierre > SMA)')
    
    periodo = _obtener_string_periodo(df_p)
    ax.set_title(f"Actividad 15: Media Móvil Simple de {window} Periodos y Puntos de Cruce\n{periodo}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Fecha y Hora (UTC)", fontsize=10)
    ax.set_ylabel("Precio (USD)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_15_media_movil_sma20.png"), dpi=120)
    plt.close()


def graficar_actividad_16_variaciones_elevadas(df: pd.DataFrame, df_elevadas: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividad 16: Destacar sobre la serie temporal las horas de variación porcentual elevada.
    """
    _asegurar_directorio(carpeta_salida)
    df_p = df.copy()
    df_p['time'] = pd.to_datetime(df_p['time'], utc=True)
    
    df_e = df_elevadas.copy()
    df_e['time'] = pd.to_datetime(df_e['time'], utc=True)
    
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df_p['time'], df_p['close'], color=COLOR_PRINCIPAL, label='Precio Cierre (USD)', alpha=0.6)
    ax.scatter(df_e['time'], df_e['close'], color=COLOR_BAJISTA, s=80, zorder=5, label='Alta Variación (> 2 Std Dev)')
    
    periodo = _obtener_string_periodo(df_p)
    ax.set_title(f"Actividad 16: Detección de Velas Horarias con Variación Elevada\n{periodo}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Fecha y Hora (UTC)", fontsize=10)
    ax.set_ylabel("Precio (USD)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_16_variaciones_elevadas.png"), dpi=120)
    plt.close()


def graficar_actividad_17_volumen_ticks(df: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividad 17: Evolución del precio junto con el volumen de ticks (Doble eje).
    """
    _asegurar_directorio(carpeta_salida)
    df_p = df.copy()
    df_p['time'] = pd.to_datetime(df_p['time'], utc=True)
    
    fig, ax1 = plt.subplots(figsize=(11, 5))
    
    ax1.plot(df_p['time'], df_p['close'], color=COLOR_PRINCIPAL, linewidth=1.8, label='Precio Cierre (USD)')
    ax1.set_xlabel("Fecha y Hora (UTC)", fontsize=10)
    ax1.set_ylabel("Precio (USD)", fontsize=10, color=COLOR_PRINCIPAL)
    
    ax2 = ax1.twinx()
    ax2.bar(df_p['time'], df_p['tick_volume'], color='gray', alpha=0.3, label='Volumen de Ticks')
    ax2.set_ylabel("Volumen de Ticks (Conteo de Cambios)", fontsize=10, color='gray')
    
    periodo = _obtener_string_periodo(df_p)
    plt.title(f"Actividad 17: Relación entre Volumen de Ticks y Evolución del Precio\n{periodo}", fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_17_volumen_ticks_precio.png"), dpi=120)
    plt.close()


def graficar_actividad_18_comparar_escalas(df_h1: pd.DataFrame, df_d1: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividad 18: Comparación de escalas temporales Horaria (H1) vs Diaria (D1).
    """
    _asegurar_directorio(carpeta_salida)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=False)
    
    # H1
    h1_p = df_h1.copy()
    h1_p['time'] = pd.to_datetime(h1_p['time'], utc=True)
    ax1.plot(h1_p['time'], h1_p['close'], color=COLOR_PRINCIPAL, label='Cierre H1 (Horario)')
    ax1.set_title("Escala Horaria (H1) - Detalle Intra-diario", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Precio (USD)", fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    # D1
    d1_p = df_d1.copy()
    d1_p['time'] = pd.to_datetime(d1_p['time'], utc=True)
    ax2.plot(d1_p['time'], d1_p['close'], color=COLOR_DESTACADO, marker='o', label='Cierre D1 (Diario)')
    ax2.set_title("Escala Diaria (D1) - Perspectiva Consolidada", fontsize=10, fontweight='bold')
    ax2.set_xlabel("Fecha (UTC)", fontsize=9)
    ax2.set_ylabel("Precio (USD)", fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    periodo = _obtener_string_periodo(h1_p)
    fig.suptitle(f"Actividad 18: Comparación del Mismo Período en Dos Escalas Temporales\n{periodo}", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_18_comparacion_escalas_h1_d1.png"), dpi=120)
    plt.close()


# ==============================================================================
# ACTIVIDADES AVANZADAS (Actividades 21, 23, 25, 26, 27, 28)
# ==============================================================================

def graficar_actividad_21_cambio_acumulado(df_acum: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividad 21: Cambio porcentual acumulado desde la primera vela.
    """
    _asegurar_directorio(carpeta_salida)
    df_p = df_acum.copy()
    df_p['time'] = pd.to_datetime(df_p['time'], utc=True)
    
    idx_max = df_p['cambio_acumulado_pct'].idxmax()
    idx_min = df_p['cambio_acumulado_pct'].idxmin()
    
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df_p['time'], df_p['cambio_acumulado_pct'], color=COLOR_PRINCIPAL, linewidth=1.6)
    ax.axhline(0, color='black', linestyle='--', alpha=0.7)
    
    # Destacar máximo y mínimo acumulado
    ax.scatter(df_p.loc[idx_max, 'time'], df_p.loc[idx_max, 'cambio_acumulado_pct'], color=COLOR_ALCISTA, s=100, zorder=5, label=f"Máx Acumulado: +{df_p.loc[idx_max, 'cambio_acumulado_pct']:.2f}%")
    ax.scatter(df_p.loc[idx_min, 'time'], df_p.loc[idx_min, 'cambio_acumulado_pct'], color=COLOR_BAJISTA, s=100, zorder=5, label=f"Mín Acumulado: {df_p.loc[idx_min, 'cambio_acumulado_pct']:.2f}%")
    
    periodo = _obtener_string_periodo(df_p)
    ax.set_title(f"Actividad 21: Rendimiento Porcentual Acumulado de HBARUSD\n{periodo}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Fecha y Hora (UTC)", fontsize=10)
    ax.set_ylabel("Cambio Acumulado desde Inicio (%)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_21_cambio_acumulado.png"), dpi=120)
    plt.close()


def graficar_actividad_23_distancia_maximo_24h(df_dist: pd.DataFrame, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividad 23: Las 10 mayores distancias porcentuales respecto al máximo de 24h.
    """
    _asegurar_directorio(carpeta_salida)
    df_p = df_dist.copy()
    df_p['fecha_str'] = pd.to_datetime(df_p['time'], utc=True).dt.strftime('%m-%d %H:%M')
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(df_p['fecha_str'], df_p['distancia_max_24h_pct'], color=COLOR_BAJISTA, edgecolor='black', alpha=0.8)
    
    ax.set_title(f"Actividad 23: Top 10 Mayores Distancias Porcentuales al Máximo de 24 Horas\n{periodo_str}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Fecha y Hora (UTC)", fontsize=10)
    ax.set_ylabel("Distancia al Máximo 24h (%)", fontsize=10)
    plt.xticks(rotation=45)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_23_distancia_maximo_24h.png"), dpi=120)
    plt.close()


def graficar_actividad_25_distribucion_cambios(df: pd.DataFrame, mediana: float, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividad 25: Histograma de la distribución de cambios porcentuales con mediana señalada.
    """
    _asegurar_directorio(carpeta_salida)
    cambios = (df['close'].pct_change() * 100.0).dropna()
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(cambios, bins=25, color=COLOR_PRINCIPAL, edgecolor='black', alpha=0.7)
    ax.axvline(mediana, color=COLOR_DESTACADO, linestyle='--', linewidth=2, label=f"Mediana: {mediana:.3f}%")
    
    ax.set_title(f"Actividad 25: Histograma de Distribución de Cambios Porcentuales Horarios\n{periodo_str}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Cambio Porcentual Horario (%)", fontsize=10)
    ax.set_ylabel("Frecuencia (Número de Horas)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_25_distribucion_histograma.png"), dpi=120)
    plt.close()


def graficar_actividad_26_movimiento_vs_ticks(df_rel: pd.DataFrame, periodo_str: str, carpeta_salida="graficas"):
    """
    Actividad 26: Gráfica de dispersión entre Movimiento Absoluto (%) y Volumen de Ticks.
    """
    _asegurar_directorio(carpeta_salida)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(df_rel['tick_volume'], df_rel['movimiento_abs_pct'], color=COLOR_PRINCIPAL, alpha=0.7, edgecolors='none')
    
    ax.set_title(f"Actividad 26: Relación entre Movimiento Absoluto (%) y Volumen de Ticks\n{periodo_str}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Volumen de Ticks (Conteo de Actualizaciones de Precio)", fontsize=10)
    ax.set_ylabel("Movimiento Absoluto Horario (%)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_26_dispersion_ticks_movimiento.png"), dpi=120)
    plt.close()


def graficar_actividad_27_diferencia_spread(df_ticks: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividad 27: Evolución de la diferencia entre precio de Compra (Ask) y Venta (Bid) / Spread.
    """
    _asegurar_directorio(carpeta_salida)
    df_s = df_ticks.copy()
    df_s['time'] = pd.to_datetime(df_s['time'], utc=True)
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    
    if 'spread_abs' in df_s.columns:
        ax.plot(df_s['time'], df_s['spread_abs'], color=COLOR_DESTACADO, label='Spread Absoluto (Ask - Bid)')
        ax.set_ylabel("Diferencia de Precio (USD)", fontsize=10)
    else:
        ax.plot(df_s['time'], df_s['spread'], color=COLOR_DESTACADO, label='Spread en Puntos MT5')
        ax.set_ylabel("Spread (Puntos)", fontsize=10)
        
    periodo = _obtener_string_periodo(df_s)
    ax.set_title(f"Actividad 27: Monitoreo del Spread (Compra/Venta) en Tiempo Real\n{periodo}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Tiempo de Observación (UTC)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_27_diferencia_spread.png"), dpi=120)
    plt.close()


def graficar_actividad_28_comparacion_semanas(df_semanal: pd.DataFrame, carpeta_salida="graficas"):
    """
    Actividad 28: Comparativa de 4 Semanas (Rango de Precio y Volumen de Ticks).
    """
    _asegurar_directorio(carpeta_salida)
    df_p = df_semanal.copy()
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    ax1.bar(df_p['Semana_ISO'], df_p['Rango_Max_Min'], color=COLOR_PRINCIPAL, alpha=0.7, label='Rango (High - Low USD)')
    ax1.set_xlabel("Semana ISO", fontsize=10)
    ax1.set_ylabel("Rango de Precio (USD)", fontsize=10, color=COLOR_PRINCIPAL)
    
    ax2 = ax1.twinx()
    ax2.plot(df_p['Semana_ISO'], df_p['Total_Ticks'], color=COLOR_DESTACADO, marker='o', linewidth=2, label='Total Ticks')
    ax2.set_ylabel("Volumen Total de Ticks", fontsize=10, color=COLOR_DESTACADO)
    
    f_min = df_p['Fecha_Inicio'].iloc[0]
    f_max = df_p['Fecha_Fin'].iloc[-1]
    
    plt.title(f"Actividad 28: Comparación de Volatilidad y Volumen a lo largo de 4 Semanas\nPeríodo (UTC): {f_min} a {f_max}", fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.savefig(os.path.join(carpeta_salida, "actividad_28_comparacion_4_semanas.png"), dpi=120)
    plt.close()