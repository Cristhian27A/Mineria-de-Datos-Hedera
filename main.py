"""
===============================================================================
PROYECTO INTEGRAL DE MINERÍA DE DATOS Y ANÁLISIS TÉCNICO DE HEDERA (HBARUSD)
===============================================================================
Orquestador Principal (main.py) con integración Celery / Redis
Cubre la invocación asíncrona de las 30 actividades del pipeline.
"""

import os
import pandas as pd
from descargar_hbar import descargar_datos_hbar
from tasks import tarea_procesar_y_graficar_actividades, tarea_generar_reporte_excel


def ejecutar_pipeline_con_celery():
    print("=" * 80)
    print(" INICIANDO PIPELINE DE ANÁLISIS DE HEDERA (HBARUSD) VIA CELERY ".center(80, "="))
    print("=" * 80)

    # --------------------------------------------------------------------------
    # [FASE 1] Cargar / Descargar datos reales de Hedera
    # --------------------------------------------------------------------------
    print("\n[FASE 1] Obtención de datos spot de Hedera (HBAR)...")
    ruta_csv_datos = os.path.join("data", "HBARUSD_H1.csv")

    df = descargar_datos_hbar()
    if df is None or df.empty:
        raise ValueError("[-] No se pudieron obtener los datos de Hedera.")

    print(f"[+] Datos guardados/verificados exitosamente en '{ruta_csv_datos}'.")

    # --------------------------------------------------------------------------
    # [FASE 2 & 3] Disparar Tarea Asíncrona de Análisis y Gráficas a Celery
    # --------------------------------------------------------------------------
    print("\n[FASE 2 & 3] Enviando tarea de análisis y gráficos a Celery worker...")
    async_result_1 = tarea_procesar_y_graficar_actividades.delay(
        ruta_csv_h1=ruta_csv_datos,
        carpeta_salida_graficas="graficas"
    )
    print(f"[+] Tarea #1 enviada a Celery (ID: {async_result_1.id})")
    print("    Esperando a que el Worker procese las gráficas...")

    res1 = async_result_1.get(timeout=300)
    print(f"[✓] Tarea #1 completada: {res1.get('mensaje')} ({res1.get('graficas_generadas')} gráficas generadas).")

    # --------------------------------------------------------------------------
    # [FASE 4] Disparar Tarea Asíncrona de Compilación de Excel
    # --------------------------------------------------------------------------
    ruta_excel = "Reporte_HBARUSD_30_Actividades.xlsx"
    print("\n[FASE 4] Enviando tarea de reporte Excel a Celery worker...")
    async_result_2 = tarea_generar_reporte_excel.delay(
        ruta_csv_h1=ruta_csv_datos,
        ruta_excel_salida=ruta_excel,
        carpeta_graficas="graficas"
    )
    print(f"[+] Tarea #2 enviada a Celery (ID: {async_result_2.id})")
    print("    Esperando a que el Worker genere el archivo Excel...")

    res2 = async_result_2.get(timeout=300)
    print(f"[✓] Tarea #2 completada: {res2.get('archivo_generado')} generado exitosamente.")

    # --------------------------------------------------------------------------
    # [FASE 5] Verificación de integridad local
    # --------------------------------------------------------------------------
    print("\n[FASE 5] Comprobación de integridad del archivo Excel con Pandas...")
    if os.path.exists(ruta_excel):
        xls = pd.ExcelFile(ruta_excel)
        print(f"[+] Archivo leíble correctamente: '{ruta_excel}'")
        print("    Pestañas encontradas:")
        for sheet in xls.sheet_names:
            df_temp = pd.read_excel(xls, sheet_name=sheet)
            print(f"      - {sheet:<25}: {len(df_temp)} registros leídos")

    print("\n" + "=" * 80)
    print(" PIPELINE COMPLETADO EXITOSAMENTE PARA HEDERA (HBAR) ".center(80, "="))
    print("=" * 80)


if __name__ == "__main__":
    ejecutar_pipeline_con_celery()