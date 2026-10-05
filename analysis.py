"""
Módulo de Análisis Estadístico y Financiero (BTCUSD)
Cubre la lógica de procesamiento para las 30 actividades de la guía.
"""

import pandas as pd
import numpy as np

# FUNCIONES AUXILIARES Y METADATOS

def obtener_periodo_utc_str(df: pd.DataFrame) -> str:
    """Retorna una cadena con el rango de fechas en UTC para encabezados y títulos."""
    if 'time' not in df.columns or df.empty:
        return "Período: N/A"
    fechas = pd.to_datetime(df['time'], utc=True)
    f_min = fechas.min().strftime('%Y-%m-%d %H:%M UTC')
    f_max = fechas.max().strftime('%Y-%m-%d %H:%M UTC')
    return f"Período analizado (UTC): {f_min} a {f_max}"


def obtener_estadisticas_clave(df: pd.DataFrame) -> dict:
    """Calcula las métricas principales para el Dashboard del Excel."""
    cambios = (df['close'].pct_change() * 100.0).dropna()
    return {
        'total_registros': len(df),
        'max_precio': float(df['high'].max()),
        'min_precio': float(df['low'].min()),
        'promedio_cierre': float(df['close'].mean()),
        'mediana_cambio_pct': float(cambios.median()) / 100.0,
        'std_precio': float(df['close'].std())
    }


# BLOQUE 1: OBTENCIÓN Y CALIDAD DE DATOS (Actividades 4 y 5)

def actividad_5_calidad_datos(df: pd.DataFrame) -> dict:
    """
    Actividad 5: Detecta valores vacíos, fechas duplicadas e intervalos horarios faltantes.
    """
    df_temp = df.copy()
    if 'time' in df_temp.columns:
        df_temp['time'] = pd.to_datetime(df_temp['time'])
        df_temp = df_temp.sort_values('time')
    
    nulos = df_temp.isnull().sum().to_dict()
    duplicados = df_temp['time'].duplicated().sum() if 'time' in df_temp.columns else 0
    
    saltos_horarios = 0
    if 'time' in df_temp.columns and len(df_temp) > 1:
        diferencia_horas = df_temp['time'].diff().dt.total_seconds() / 3600.0
        saltos_horarios = int((diferencia_horas > 1.0).sum())
        
    explicacion_causas = (
        "Los saltos en los intervalos de tiempo corresponden al cierre de mercado "
        "durante fines de semana o periodos de baja liquidez."
    )
    
    return {
        "valores_nulos_por_columna": nulos,
        "fechas_duplicadas": int(duplicados),
        "intervalos_faltantes_saltos_1h": saltos_horarios,
        "explicacion_causas": explicacion_causas
    }


# BLOQUE 2: CONSULTAS Y VISUALIZACIONES DEL PRECIO (Actividades 6 a 18)

def actividad_7_top_rangos_vela(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Actividad 7: Identifica las N velas con mayor rango (High - Low).
    """
    df_calc = df.copy()
    df_calc['rango'] = df_calc['high'] - df_calc['low']
    top_df = df_calc.sort_values(by='rango', ascending=False).head(top_n)
    return top_df[['time', 'open', 'high', 'low', 'close', 'rango']]


def actividad_8_top_subidas(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Actividad 8: Encuentra las N horas con mayor aumento porcentual.
    """
    df_calc = df.copy()
    df_calc['cambio_pct'] = df_calc['close'].pct_change() * 100.0
    top_subidas = df_calc.sort_values(by='cambio_pct', ascending=False).head(top_n)
    return top_subidas[['time', 'open', 'close', 'cambio_pct']]


def actividad_9_top_caidas(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Actividad 9: Encuentra las N horas con mayor disminución porcentual.
    """
    df_calc = df.copy()
    df_calc['cambio_pct'] = df_calc['close'].pct_change() * 100.0
    top_caidas = df_calc.sort_values(by='cambio_pct', ascending=True).head(top_n)
    return top_caidas[['time', 'open', 'close', 'cambio_pct']]


def obtener_top_movimientos(df: pd.DataFrame, top_n: int = 10):
    """Auxiliar para el reporte Excel"""
    return actividad_8_top_subidas(df, top_n), actividad_9_top_caidas(df, top_n)


def actividad_10_clasificacion_velas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 10: Clasifica las velas en Alcista, Bajista o Doji.
    """
    df_calc = df.copy()
    condiciones = [
        df_calc['close'] > df_calc['open'],
        df_calc['close'] < df_calc['open']
    ]
    elecciones = ['Alcista', 'Bajista']
    df_calc['tipo_vela'] = np.select(condiciones, elecciones, default='Doji')
    
    conteo = df_calc['tipo_vela'].value_counts().reset_index()
    conteo.columns = ['Tipo_Vela', 'Cantidad']
    conteo['Proporcion_Pct'] = (conteo['Cantidad'] / len(df_calc)) * 100.0
    return conteo


def clasificar_velas(df: pd.DataFrame) -> pd.DataFrame:
    """Alias para el reporte Excel"""
    return actividad_10_clasificacion_velas(df)


def actividad_11_resumen_diario(df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 11: Resumen por día de Apertura, Máximo, Mínimo, Cierre y Cambio (%).
    """
    df_calc = df.copy()
    df_calc['fecha'] = pd.to_datetime(df_calc['time']).dt.date
    
    resumen = df_calc.groupby('fecha').agg(
        Apertura=('open', 'first'),
        Máximo=('high', 'max'),
        Mínimo=('low', 'min'),
        Cierre=('close', 'last')
    ).reset_index()
    
    resumen['Rango'] = resumen['Máximo'] - resumen['Mínimo']
    resumen['Cambio (%)'] = ((resumen['Cierre'] - resumen['Apertura']) / resumen['Apertura']) * 100.0
    return resumen


def obtener_resumen_diario(df: pd.DataFrame) -> pd.DataFrame:
    """Alias para el reporte Excel"""
    return actividad_11_resumen_diario(df)


def actividad_12_comparacion_dias(resumen_diario_df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 12: Identifica el día con mayor subida, mayor caída y mayor rango.
    """
    res = resumen_diario_df.copy()
    
    dia_mayor_subida = res.loc[res['Cambio (%)'].idxmax()]
    dia_mayor_caida = res.loc[res['Cambio (%)'].idxmin()]
    dia_mayor_rango = res.loc[res['Rango'].idxmax()]
    
    coinciden = (dia_mayor_subida['fecha'] == dia_mayor_rango['fecha']) or (dia_mayor_caida['fecha'] == dia_mayor_rango['fecha'])
    
    return pd.DataFrame([
        {"Criterio": "Mayor Subida", "Fecha": dia_mayor_subida['fecha'], "Valor": dia_mayor_subida['Cambio (%)'], "Unidad": "%"},
        {"Criterio": "Mayor Caída", "Fecha": dia_mayor_caida['fecha'], "Valor": dia_mayor_caida['Cambio (%)'], "Unidad": "%"},
        {"Criterio": "Mayor Rango (Volatilidad)", "Fecha": dia_mayor_rango['fecha'], "Valor": dia_mayor_rango['Rango'], "Unidad": "USD"},
        {"Criterio": "Coincidencia con Extremos", "Fecha": "N/A", "Valor": str(coinciden), "Unidad": "Booleano"}
    ])


def actividad_13_promedio_por_hora(df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 13: Movimiento porcentual promedio por hora del día en UTC (0-23h).
    """
    df_calc = df.copy()
    df_calc['time'] = pd.to_datetime(df_calc['time'], utc=True)
    df_calc['hora_utc'] = df_calc['time'].dt.hour
    df_calc['cambio_abs_pct'] = df_calc['close'].pct_change().abs() * 100.0
    
    promedio_hora = df_calc.groupby('hora_utc')['cambio_abs_pct'].mean().reset_index()
    promedio_hora.columns = ['Hora_UTC', 'Movimiento_Promedio_Pct']
    return promedio_hora


def actividad_14_comportamiento_dia_semana(df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 14: Comparación de movimiento promedio por día de la semana.
    """
    df_calc = df.copy()
    df_calc['time'] = pd.to_datetime(df_calc['time'], utc=True)
    df_calc['dia_nombre'] = df_calc['time'].dt.day_name()
    df_calc['dia_num'] = df_calc['time'].dt.dayofweek
    df_calc['rango_pct'] = ((df_calc['high'] - df_calc['low']) / df_calc['open']) * 100.0
    
    comp_dias = df_calc.groupby(['dia_num', 'dia_nombre'])['rango_pct'].agg(['mean', 'count']).reset_index()
    comp_dias.columns = ['Dia_Num', 'Dia_Semana', 'Rango_Promedio_Pct', 'Registros']
    return comp_dias.sort_values('Dia_Num')


def actividad_15_media_movil_y_cruces(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Actividad 15: Calcula SMA 20 e identifica puntos de cruce alcista.
    """
    df_calc = df.copy()
    df_calc[f'SMA_{window}'] = df_calc['close'].rolling(window=window).mean()
    
    prev_close = df_calc['close'].shift(1)
    prev_sma = df_calc[f'SMA_{window}'].shift(1)
    
    df_calc['cruce_alcista'] = (prev_close <= prev_sma) & (df_calc['close'] > df_calc[f'SMA_{window}'])
    return df_calc


def actividad_16_variaciones_elevadas(df: pd.DataFrame, umbral_std: float = 2.0) -> pd.DataFrame:
    """
    Actividad 16: Detecta horas con variación elevada (> media + N std dev).
    """
    df_calc = df.copy()
    df_calc['cambio_abs_pct'] = df_calc['close'].pct_change().abs() * 100.0
    
    media = df_calc['cambio_abs_pct'].mean()
    std = df_calc['cambio_abs_pct'].std()
    criterio_corte = media + (umbral_std * std)
    
    elevadas = df_calc[df_calc['cambio_abs_pct'] > criterio_corte].sort_values(by='cambio_abs_pct', ascending=False)
    return elevadas[['time', 'open', 'close', 'cambio_abs_pct']].head(10)


def actividad_17_top_volumen_ticks(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Actividad 17: Identifica las N velas con mayor volumen de ticks.
    """
    df_calc = df.copy()
    df_calc['movimiento_pct'] = ((df_calc['close'] - df_calc['open']) / df_calc['open']) * 100.0
    top_ticks = df_calc.sort_values(by='tick_volume', ascending=False).head(top_n)
    return top_ticks[['time', 'close', 'tick_volume', 'movimiento_pct']]


# BLOQUE 3: CONSULTAS ADICIONALES Y AVANZADAS (Actividades 21 a 30)

def actividad_21_cambio_acumulado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 21: Cambio porcentual acumulado desde la primera vela.
    """
    df_calc = df.copy()
    precio_inicial = df_calc['close'].iloc[0]
    df_calc['cambio_acumulado_pct'] = ((df_calc['close'] - precio_inicial) / precio_inicial) * 100.0
    return df_calc[['time', 'close', 'cambio_acumulado_pct']]


def actividad_22_rachas_consecutivas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 22: Identifica las rachas más largas de velas alcistas y bajistas.
    """
    df_calc = df.copy()
    df_calc['ret'] = df_calc['close'].diff()
    df_calc['direccion'] = np.where(df_calc['ret'] > 0, 1, np.where(df_calc['ret'] < 0, -1, 0))
    
    df_calc['streak_id'] = (df_calc['direccion'] != df_calc['direccion'].shift(1)).cumsum()
    
    streaks = []
    for _, group in df_calc.groupby('streak_id'):
        direccion = group['direccion'].iloc[0]
        if direccion == 0:
            continue
        duracion = len(group)
        p_inicio = group['open'].iloc[0]
        p_fin = group['close'].iloc[-1]
        cambio_pct = ((p_fin - p_inicio) / p_inicio) * 100.0
        
        streaks.append({
            'Tipo_Racha': 'Alcista' if direccion == 1 else 'Bajista',
            'Fecha_Inicio': group['time'].iloc[0],
            'Fecha_Fin': group['time'].iloc[-1],
            'Duracion_Horas': duracion,
            'Precio_Inicio': p_inicio,
            'Precio_Fin': p_fin,
            'Cambio_Pct': cambio_pct
        })
        
    df_streaks = pd.DataFrame(streaks)
    if df_streaks.empty:
        return pd.DataFrame()
        
    racha_max_alcista = df_streaks[df_streaks['Tipo_Racha'] == 'Alcista'].sort_values('Duracion_Horas', ascending=False).head(1)
    racha_max_bajista = df_streaks[df_streaks['Tipo_Racha'] == 'Bajista'].sort_values('Duracion_Horas', ascending=False).head(1)
    
    return pd.concat([racha_max_alcista, racha_max_bajista], ignore_index=True)


def actividad_23_distancia_maximo_24h(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Actividad 23: Distancia porcentual del cierre al máximo de las 24h previas.
    """
    df_calc = df.copy()
    df_calc['max_24h'] = df_calc['high'].shift(1).rolling(window=24, min_periods=1).max()
    df_calc['distancia_max_24h_pct'] = ((df_calc['close'] - df_calc['max_24h']) / df_calc['max_24h']) * 100.0
    
    top_distancias = df_calc.dropna(subset=['distancia_max_24h_pct']).sort_values('distancia_max_24h_pct', ascending=True).head(top_n)
    return top_distancias[['time', 'close', 'max_24h', 'distancia_max_24h_pct']]


def actividad_24_recuperacion_caidas(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Actividad 24: Evalúa el comportamiento 1h, 6h y 24h después de caídas.
    """
    df_calc = df.copy()
    df_calc['time'] = pd.to_datetime(df_calc['time'])
    df_calc['cambio_pct'] = df_calc['close'].pct_change() * 100.0
    
    top_caidas = df_calc.sort_values(by='cambio_pct', ascending=True).head(top_n)
    
    recuperacion = []
    for _, row in top_caidas.iterrows():
        f_caida = row['time']
        p_caida = row['close']
        c_pct = row['cambio_pct']
        
        p_1h = df_calc.loc[df_calc['time'] == f_caida + pd.Timedelta(hours=1), 'close']
        p_6h = df_calc.loc[df_calc['time'] == f_caida + pd.Timedelta(hours=6), 'close']
        p_24h = df_calc.loc[df_calc['time'] == f_caida + pd.Timedelta(hours=24), 'close']
        
        val_1h = ((p_1h.values[0] - p_caida) / p_caida * 100.0) if len(p_1h) > 0 else np.nan
        val_6h = ((p_6h.values[0] - p_caida) / p_caida * 100.0) if len(p_6h) > 0 else np.nan
        val_24h = ((p_24h.values[0] - p_caida) / p_caida * 100.0) if len(p_24h) > 0 else np.nan
        
        recuperacion.append({
            'Fecha_Hora_UTC': f_caida,
            'Precio_Cierre': p_caida,
            'Caida_Pct': c_pct,
            'Cambio_1h_Post_Pct': val_1h,
            'Cambio_6h_Post_Pct': val_6h,
            'Cambio_24h_Post_Pct': val_24h
        })
        
    return pd.DataFrame(recuperacion)


def actividad_25_distribucion_cambios(df: pd.DataFrame) -> dict:
    """
    Actividad 25: Distribución de cambios porcentuales horarios.
    """
    cambios = (df['close'].pct_change() * 100.0).dropna()
    mediana = float(cambios.median())
    promedio = float(cambios.mean())
    desviacion = float(cambios.std())
    
    # Corrección: Uso de abs() de Python para float escalar de NumPy
    extremos = int((cambios.abs() > (abs(promedio) + 2 * desviacion)).sum())
    
    return {
        "Mediana_Pct": mediana,
        "Promedio_Pct": promedio,
        "Desviacion_Std_Pct": desviacion,
        "Cantidad_Cambios_Extremos": extremos,
        "Frecuencia_Extremos": "Poco común" if extremos < (len(cambios) * 0.05) else "Frecuente"
    }


def actividad_26_movimiento_vs_ticks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 26: Relación entre movimiento absoluto (%) y volumen de ticks.
    """
    df_calc = df.copy()
    df_calc['movimiento_abs_pct'] = (df_calc['close'].pct_change().abs()) * 100.0
    return df_calc[['time', 'movimiento_abs_pct', 'tick_volume']].dropna()


def actividad_28_comparacion_semanas(df_4w: pd.DataFrame) -> pd.DataFrame:
    """
    Actividad 28: Comparación de semanas ISO.
    """
    df_calc = df_4w.copy()
    df_calc['time'] = pd.to_datetime(df_calc['time'])
    df_calc['semana_iso'] = df_calc['time'].dt.isocalendar().week
    
    semanal = []
    for sem, grp in df_calc.groupby('semana_iso'):
        f_open = grp['open'].iloc[0]
        l_close = grp['close'].iloc[-1]
        chg_pct = ((l_close - f_open) / f_open) * 100.0
        rango = grp['high'].max() - grp['low'].min()
        std_close = grp['close'].std()
        sum_ticks = grp['tick_volume'].sum()
        
        semanal.append({
            'Semana_ISO': f"Semana {sem}",
            'Fecha_Inicio': grp['time'].iloc[0].strftime("%Y-%m-%d"),
            'Fecha_Fin': grp['time'].iloc[-1].strftime("%Y-%m-%d"),
            'Cambio_Precio_Pct': chg_pct,
            'Rango_Max_Min': rango,
            'Std_Precio_Cierre': std_close,
            'Total_Ticks': sum_ticks
        })
        
    return pd.DataFrame(semanal)