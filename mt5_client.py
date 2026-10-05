"""
===============================================================================
MÓDULO DE INTERFAZ Y EXTRACCIÓN DE DATOS DESDE METATRADER 5 (MT5)
===============================================================================
Proyecto: Análisis Técnico y Estadístico de Hedera (HBAR) - 30 Actividades
Autor: Cristhian Alonso

Propósito del Módulo:
- Establecer comunicación directa mediante la API de MetaTrader 5 en Python.
- Localizar de forma dinámica el par de cotización de Hedera (HBARUSD / HBAR).
- Extraer precios Bid/Ask en tiempo real con sello de tiempo UTC.
- Descargar series temporales de velas (OHLCV) en temporalidades H1 y D1.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone


def inicializar_mt5() -> bool:
    """
    Inicializa la conexión con la terminal de MetaTrader 5 instalada en la PC.
    
    Explicación para la defensa:
    - mt5.initialize() abre el canal de comunicación (IPC) entre Python y MT5.
    - Si la terminal no está abierta o hay falla de licencia, retorna False.
    """
    if not mt5.initialize():
        print(f"[-] Error al inicializar MetaTrader 5: {mt5.last_error()}")
        return False
    print("[+] Conexión exitosa con MetaTrader 5")
    return True


def obtener_simbolo_hbar() -> str:
    """
    Busca y habilita de forma dinámica el símbolo exacto para Hedera en el bróker.
    
    Explicación para la defensa:
    - Los brókers nombran a Hedera de diferentes formas según el tipo de cuenta 
      (ejemplo: HBARUSD, HBARUSD.demo, HBAR, HBARUSD.a, #HBARUSD).
    - Esta función primero intenta una búsqueda directa en una lista de nombres comunes.
    - Si no lo encuentra, escanea todos los símbolos disponibles en el bróker 
      filtrando por el texto 'HBAR' o 'HEDERA'.
    - Una vez hallado, ejecuta `mt5.symbol_select(c, True)` para activarlo en 
      la ventana de 'Observación del Mercado'.
    """
    # 1. Lista de candidatos más habituales en brókers de Forex y Cripto
    candidatos = [
        "HBARUSD", "HBARUSD.demo", "HBARUSD.a", "HBARUSD_m", "HBARUSD.ecn",
        "HBARUSD_i", "HBARUSD_", "HBAR/USD", "HEDERA", "HBARUSD.micro",
        "HBAR", "#HBARUSD", "HBARUSD.p"
    ]
    
    # Búsqueda por coincidencia directa
    for c in candidatos:
        info = mt5.symbol_info(c)
        if info is not None:
            mt5.symbol_select(c, True)
            return c
            
    # Búsqueda dinámica en el catálogo general de símbolos del bróker
    simbolos = mt5.symbols_get()
    if simbolos:
        for s in simbolos:
            nombre = s.name.upper()
            desc = s.description.upper()
            if "HBAR" in nombre or "HEDERA" in nombre or "HBAR" in desc:
                mt5.symbol_select(s.name, True)
                return s.name
                
    return None


def info_digits_or_2(simbolo_nombre: str) -> int:
    """Retorna la precisión decimal del activo (por ejemplo, 4 o 5 decimales para HBAR)."""
    info = mt5.symbol_info(simbolo_nombre)
    return info.digits if info else 4


def actividad_1_identificacion_symbol(simbolo_nombre: str) -> dict:
    """
    ACTIVIDAD 1: Identificación y Metadatos del Activo Financiero.
    
    Explicación para la defensa:
    - Obtiene la ficha técnica del activo desde la plataforma.
    - Nos da la descripción oficial, moneda base (HBAR), moneda de cotización (USD)
      y el número de dígitos decimales que usa el bróker para cotizar.
    """
    info = mt5.symbol_info(simbolo_nombre)
    if info is None:
        return None
    
    return {
        "Nombre exacto": info.name,
        "Descripción": info.description,
        "Moneda de cotización": info.currency_profit,
        "Moneda base": info.currency_base,
        "Dígitos decimales": info.digits
    }


def actividad_2_precio_actual(simbolo_nombre: str) -> dict:
    """
    ACTIVIDAD 2: Cotización del Precio Actual en Tiempo Real.
    
    Explicación para la defensa:
    - `mt5.symbol_info_tick()` extrae el último tick negociado en el mercado.
    - Bid: Precio de Venta (al que venderías el activo).
    - Ask: Precio de Compra (al que comprarías el activo).
    - Spread: Es la comisión o diferencia entre Ask y Bid (`Ask - Bid`).
    - Convierte el timestamp Unix a formato estándar legible en UTC.
    """
    tick = mt5.symbol_info_tick(simbolo_nombre)
    if tick is None:
        return None
    
    fecha_utc = datetime.fromtimestamp(tick.time, tz=timezone.utc)
    bid = tick.bid
    ask = tick.ask
    digits = info_digits_or_2(simbolo_nombre)
    spread = round(ask - bid, digits)
    
    return {
        "Símbolo": simbolo_nombre,
        "Precio Venta (Bid)": bid,
        "Precio Compra (Ask)": ask,
        "Spread (Diferencia)": spread,
        "Fecha/Hora (UTC)": fecha_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    }


def actividad_3_ultimas_100_velas(simbolo_nombre: str) -> pd.DataFrame:
    """
    ACTIVIDAD 3: Descarga de la Serie Temporal de Velas Horarias (H1).
    
    Explicación para la defensa:
    - `mt5.copy_rates_from_pos()` descarga un arreglo estructurado con las 
      últimas 100 velas de 1 hora (`TIMEFRAME_H1`).
    - Las velas contienen la estructura estándar OHLCV:
        * Open  (Apertura)
        * High  (Máximo)
        * Low   (Mínimo)
        * Close (Cierre)
        * Tick Volume (Volumen de actualizaciones de precio)
    - Convertimos la columna de tiempo a un objeto `datetime` con zona horaria UTC.
    """
    rates = mt5.copy_rates_from_pos(simbolo_nombre, mt5.TIMEFRAME_H1, 1, 100)
    if rates is None or len(rates) == 0:
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
    return df


def actividad_4_consulta_por_fechas(simbolo_nombre: str, fecha_inicio: datetime, fecha_fin: datetime, timeframe=mt5.TIMEFRAME_H1) -> pd.DataFrame:
    """
    ACTIVIDADES 4 y 18: Extracción de Datos por Rango de Fechas Específico.
    
    Explicación para la defensa:
    - Permite consultar un intervalo de fechas exacto (por ejemplo, para comparar
      escalas de tiempo entre H1 y D1 en la Actividad 18).
    """
    rates = mt5.copy_rates_range(simbolo_nombre, timeframe, fecha_inicio, fecha_fin)
    if rates is None or len(rates) == 0:
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
    return df


# =============================================================================
# BLOQUE DE PRUEBA LOCAL DEL MÓDULO
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(" PRUEBA DE CONEXIÓN METATRADER 5 - HEDERA (HBAR) ".center(70, "="))
    print("=" * 70)
    
    if inicializar_mt5():
        simbolo_real = obtener_simbolo_hbar()
        
        if simbolo_real:
            print(f"\n[+] Símbolo de Hedera encontrado en el bróker: '{simbolo_real}'")
            
            # Prueba Actividad 1
            print(f"\n--- ACTIVIDAD 1: Identificación ({simbolo_real}) ---")
            info = actividad_1_identificacion_symbol(simbolo_real)
            if info:
                for k, v in info.items():
                    print(f"  * {k}: {v}")
            
            # Prueba Actividad 2
            print(f"\n--- ACTIVIDAD 2: Precio Actual ({simbolo_real}) ---")
            precio = actividad_2_precio_actual(simbolo_real)
            if precio:
                for k, v in precio.items():
                    print(f"  * {k}: {v}")
            
            # Prueba Actividad 3
            print(f"\n--- ACTIVIDAD 3: Últimas 100 Velas Horarias (H1) ---")
            velas_df = actividad_3_ultimas_100_velas(simbolo_real)
            if velas_df is not None:
                print(f"  * Total de registros recuperados: {len(velas_df)}")
                print("  * Columnas obtenidas:", list(velas_df.columns))
                print("\n  * Primeras 3 velas descargadas:")
                print(velas_df[['time', 'open', 'high', 'low', 'close', 'tick_volume']].head(3).to_string(index=False))
        else:
            print("\n[-] Error: No se encontró ningún símbolo válido de Hedera (HBAR) en esta cuenta.")
            print("[i] Sugerencia: Abre MT5, presiona Ctrl+U y activa 'HBARUSD' en la ventana de símbolos.")
            
        mt5.shutdown()
        print("\n[+] Conexión con MT5 finalizada.")