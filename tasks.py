"""
Módulo de Tareas Asíncronas (Tasks) para Celery
Gestión de procesamiento intensivo, generación de gráficas y reportes en segundo plano.
"""

import os
import traceback
from celery_app import app
import pandas as pd

# Importación de los módulos internos del proyecto
import analysis
import visualization
import report


@app.task(bind=True, name="tasks.tarea_procesar_y_graficar_actividades")
def tarea_procesar_y_graficar_actividades(self, ruta_csv_h1: str, ruta_csv_d1: str = None, carpeta_salida_graficas="graficas"):
    """
    Tarea asíncrona principal que ejecuta la secuencia de análisis y generación de
    las gráficas requeridas, notificando el estado del progreso.
    """
    try:
        # Paso 1: Carga de datos
        self.update_state(state="PROGRESS", meta={"paso": 1, "total_pasos": 5, "mensaje": "Cargando datos CSV en memoria..."})
        if not os.path.exists(ruta_csv_h1):
            raise FileNotFoundError(f"No se encontró el archivo de datos: {ruta_csv_h1}")
            
        df_h1 = pd.read_csv(ruta_csv_h1)
        if not pd.api.types.is_datetime64_any_dtype(df_h1['time']):
            df_h1['time'] = pd.to_datetime(df_h1['time'])
        
        # Paso 2: Ejecución de cálculos analíticos
        self.update_state(state="PROGRESS", meta={"paso": 2, "total_pasos": 5, "mensaje": "Calculando métricas analíticas y estadísticas..."})
        resumen_diario = analysis.actividad_11_resumen_diario(df_h1)
        top_subidas = analysis.actividad_8_top_subidas(df_h1)
        top_caidas = analysis.actividad_9_top_caidas(df_h1)
        clasificacion_velas = analysis.actividad_10_clasificacion_velas(df_h1)
        comportamiento_hora = analysis.actividad_13_promedio_por_hora(df_h1)
        volatilidad_dia = analysis.actividad_14_comportamiento_dia_semana(df_h1)
        df_sma = analysis.actividad_15_media_movil_y_cruces(df_h1, window=20)
        df_elevadas = analysis.actividad_16_variaciones_elevadas(df_h1)
        df_acumulado = analysis.actividad_21_cambio_acumulado(df_h1)
        df_dist_max = analysis.actividad_23_distancia_maximo_24h(df_h1)
        comp_semanal = analysis.actividad_28_comparacion_semanas(df_h1)
        
        if hasattr(analysis, 'obtener_periodo_utc_str'):
            periodo_str = analysis.obtener_periodo_utc_str(df_h1)
        else:
            periodo_str = f"Período (UTC): {df_h1['time'].min().strftime('%Y-%m-%d %H:%M')} a {df_h1['time'].max().strftime('%Y-%m-%d %H:%M')}"

        # Paso 3: Generación de gráficos (Visualización)
        self.update_state(state="PROGRESS", meta={"paso": 3, "total_pasos": 5, "mensaje": "Generando gráficas estandarizadas..."})
        os.makedirs(carpeta_salida_graficas, exist_ok=True)
        
        visualization.graficar_actividad_6_evolucion_precio(df_h1, carpeta_salida_graficas)
        visualization.graficar_actividad_7_top_rangos(analysis.actividad_7_top_rangos_vela(df_h1), periodo_str, carpeta_salida_graficas)
        visualization.graficar_actividad_8_9_top_cambios(top_subidas, top_caidas, periodo_str, carpeta_salida_graficas)
        visualization.graficar_actividad_10_clasificacion_velas(clasificacion_velas, periodo_str, carpeta_salida_graficas)
        visualization.graficar_actividad_11_12_resumen_diario(resumen_diario, carpeta_salida_graficas)
        visualization.graficar_actividad_13_promedio_por_hora(comportamiento_hora, periodo_str, carpeta_salida_graficas)
        visualization.graficar_actividad_14_dia_semana(volatilidad_dia, periodo_str, carpeta_salida_graficas)
        visualization.graficar_actividad_15_media_movil(df_sma, 20, carpeta_salida_graficas)
        visualization.graficar_actividad_16_variaciones_elevadas(df_h1, df_elevadas, carpeta_salida_graficas)
        visualization.graficar_actividad_17_volumen_ticks(df_h1, carpeta_salida_graficas)
        
        if ruta_csv_d1 and os.path.exists(ruta_csv_d1):
            df_d1 = pd.read_csv(ruta_csv_d1)
            visualization.graficar_actividad_18_comparar_escalas(df_h1, df_d1, carpeta_salida_graficas)
            
        visualization.graficar_actividad_21_cambio_acumulado(df_acumulado, carpeta_salida_graficas)
        visualization.graficar_actividad_23_distancia_maximo_24h(df_dist_max, periodo_str, carpeta_salida_graficas)
        
        distribucion = analysis.actividad_25_distribucion_cambios(df_h1)
        mediana_pct = distribucion.get('Mediana_Pct', 0) if isinstance(distribucion, dict) else 0
        visualization.graficar_actividad_25_distribucion_cambios(df_h1, mediana_pct, periodo_str, carpeta_salida_graficas)
        
        df_rel = analysis.actividad_26_movimiento_vs_ticks(df_h1)
        visualization.graficar_actividad_26_movimiento_vs_ticks(df_rel, periodo_str, carpeta_salida_graficas)
        visualization.graficar_actividad_28_comparacion_semanas(comp_semanal, carpeta_salida_graficas)

        # Paso 4: Finalización
        self.update_state(state="PROGRESS", meta={"paso": 4, "total_pasos": 5, "mensaje": "Gráficas generadas exitosamente."})
        
        return {
            "estado": "COMPLETADO",
            "mensaje": "Pipeline de análisis y visualización asíncrono completado.",
            "graficas_generadas": len(os.listdir(carpeta_salida_graficas)) if os.path.exists(carpeta_salida_graficas) else 0
        }

    except Exception as exc:
        err_msg = f"Error en la tarea asíncrona: {str(exc)}\n{traceback.format_exc()}"
        self.update_state(state="FAILURE", meta={"error": str(exc), "traceback": traceback.format_exc()})
        raise Exception(err_msg)


@app.task(bind=True, name="tasks.tarea_generar_reporte_excel")
def tarea_generar_reporte_excel(self, ruta_csv_h1: str, ruta_excel_salida="Reporte_HBARUSD_30_Actividades.xlsx", carpeta_graficas="graficas"):
    """
    Tarea asíncrona dedicada a la compilación del libro Excel.
    """
    try:
        self.update_state(state="PROGRESS", meta={"paso": 1, "total_pasos": 2, "mensaje": "Construyendo estructuras Excel..."})
        report.generar_reporte_excel_completo(
            ruta_csv_h1=ruta_csv_h1, 
            ruta_salida_excel=ruta_excel_salida, 
            carpeta_graficas=carpeta_graficas
        )
        self.update_state(state="PROGRESS", meta={"paso": 2, "total_pasos": 2, "mensaje": "Reporte Excel finalizado."})
        return {
            "estado": "COMPLETADO",
            "archivo_generado": ruta_excel_salida
        }
    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        raise exc