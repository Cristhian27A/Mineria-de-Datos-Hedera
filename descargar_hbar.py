import os
import pandas as pd
import yfinance as yf

def descargar_datos_hbar():
    print("[+] Descargando velas H1 reales de Hedera (HBAR-USD)...")
    
    # Descarga datos de los últimos 60 días en temporalidad de 1 hora
    ticker = yf.Ticker("HBAR-USD")
    df = ticker.history(period="60d", interval="1h")

    if df.empty:
        print("[-] Error: No se recibieron datos de Yahoo Finance.")
        return None

    # Adaptar formato de columnas para que coincida exactamente con MT5
    df = df.reset_index()
    df = df.rename(columns={
        'Datetime': 'time',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'tick_volume'
    })

    # Ajustar fecha y columna spread
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)
    df['spread'] = 1

    # Filtrar solo las columnas necesarias para el pipeline
    df_mt5_compat = df[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread']]

    # Guardar en carpeta data/
    os.makedirs("data", exist_ok=True)
    ruta_csv = os.path.join("data", "HBARUSD_H1.csv")
    df_mt5_compat.to_csv(ruta_csv, index=False)

    print(f"[✓] Archivo CSV generado en: {ruta_csv}")
    print(f"[i] Total de registros cargados: {len(df_mt5_compat)}")
    print(f"[i] Precios reales HBAR: Mínimo ${df_mt5_compat['low'].min():.4f} | Máximo ${df_mt5_compat['high'].max():.4f}\n")

    return df_mt5_compat

if __name__ == "__main__":
    descargar_datos_hbar()