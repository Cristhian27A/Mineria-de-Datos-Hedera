"""
Módulo de Generación de Reportes Excel (.xlsx)
==============================================
Compila los resultados de las 30 actividades de análisis del par HBARUSD 
en un libro de cálculo estilizado y profesional utilizando openpyxl.

Incluye:
- Paleta de colores corporativa (Azul Marino / Gris / Verde / Rojo suave).
- Formatos numéricos automáticos (moneda de precisión crypto, porcentajes, enteros).
- Paneles congelados, auto-ajuste de columnas y sombreado cebra.
- Pestañas independientes para Dashboard, Datos Horarios, Resumen Diario,
  Top Movimientos y Estadísticas de Patrones.
- Incrustación de gráficos generados por el módulo de visualización.
"""

import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image

import analysis

# =============================================================================
# ESTILOS CORPORATIVOS GLOBALES
# =============================================================================
COLOR_HEADER_BG = "1F4E78"       # Azul Marino Profundo
COLOR_HEADER_TEXT = "FFFFFF"     # Blanco
COLOR_ZEBRA = "F2F5F9"           # Gris-Azul Suave
COLOR_DESTACADO_BG = "E2EFDA"   # Verde Claro Suave
COLOR_ALCISTA_TEXT = "375623"   # Verde Oscuro
COLOR_BAJISTA_TEXT = "C00000"   # Rojo Oscuro
COLOR_BORDER = "D9D9D9"         # Gris Claro para bordes

FONT_TITULO = Font(name="Calibri", size=15, bold=True, color="1F4E78")
FONT_SUBTITULO = Font(name="Calibri", size=11, italic=True, color="595959")
FONT_HEADER = Font(name="Calibri", size=11, bold=True, color=COLOR_HEADER_TEXT)
FONT_BOLD = Font(name="Calibri", size=11, bold=True)
FONT_REGULAR = Font(name="Calibri", size=11)

FILL_HEADER = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
FILL_ZEBRA = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")
FILL_DESTACADO = PatternFill(start_color=COLOR_DESTACADO_BG, end_color=COLOR_DESTACADO_BG, fill_type="solid")

BORDER_THIN = Border(
    left=Side(style='thin', color=COLOR_BORDER),
    right=Side(style='thin', color=COLOR_BORDER),
    top=Side(style='thin', color=COLOR_BORDER),
    bottom=Side(style='thin', color=COLOR_BORDER)
)

ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")


# =============================================================================
# FUNCIONES AUXILIARES DE FORMATO
# =============================================================================
def _aplicar_formato_tabla(ws, min_row, max_row, min_col, max_col, es_zebra=True):
    """Aplica bordes, fuente estándar y alineación/sombreado cebra a un rango de celdas."""
    for row_idx in range(min_row, max_row + 1):
        es_fila_par = (row_idx % 2 == 0)
        for col_idx in range(min_col, max_col + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = BORDER_THIN
            if not cell.font.bold:
                cell.font = FONT_REGULAR
            
            if es_zebra and es_fila_par and cell.fill.fill_type is None:
                cell.fill = FILL_ZEBRA


def _ajustar_ancho_columnas(ws, min_width=12, padding=4):
    """Ajusta automáticamente el ancho de cada columna según la longitud de su contenido."""
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str:
                val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + padding, min_width)


# =============================================================================
# GENERADOR PRINCIPAL DEL REPORTE
# =============================================================================
def generar_reporte_excel_completo(
    ruta_csv_h1: str, 
    ruta_salida_excel: str = "Reporte_HBARUSD_30_Actividades.xlsx", 
    carpeta_graficas: str = "graficas"
) -> str:
    """
    Genera un libro de Excel interactivo (.xlsx) estructurado en 5 pestañas:
    1. Resumen_General (KPIs, métricas clave y gráfico evolutivo principal)
    2. Datos_Horarios (Serie temporal completa de velas H1 con volúmenes)
    3. Resumen_Diario (Consolidado OHLC y retornos diarios UTC)
    4. Mayores_Movimientos (Ranking Top 10 subidas y caídas horarias)
    5. Patrones_y_Estadisticas (Distribución de velas y patrones temporales)
    """
    if not os.path.exists(ruta_csv_h1):
        raise FileNotFoundError(f"No se encontró el archivo de datos de origen: {ruta_csv_h1}")
        
    df_h1 = pd.read_csv(ruta_csv_h1)
    df_h1['time'] = pd.to_datetime(df_h1['time'], utc=True)
    
    dir_salida = os.path.dirname(ruta_salida_excel)
    if dir_salida and not os.path.exists(dir_salida):
        os.makedirs(dir_salida, exist_ok=True)
        
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Eliminar hoja en blanco inicial

    FMT_MONEDA = "$#,##0.0000" if df_h1['close'].mean() < 1.0 else "$#,##0.00"

    # -------------------------------------------------------------------------
    # PESTAÑA 1: Resumen_General (Dashboard)
    # -------------------------------------------------------------------------
    ws_dash = wb.create_sheet(title="Resumen_General")
    ws_dash.views.sheetView[0].showGridLines = True
    
    ws_dash.cell(row=2, column=2, value="ANÁLISIS TÉCNICO Y ESTADÍSTICO INTEGRAL DE HEDERA (HBARUSD)").font = FONT_TITULO
    ws_dash.cell(row=3, column=2, value=analysis.obtener_periodo_utc_str(df_h1)).font = FONT_SUBTITULO
    
    stats = analysis.obtener_estadisticas_clave(df_h1)
    kpis = [
        ("Total Registros Horarios (H1)", stats['total_registros'], "#,##0"),
        ("Precio Máximo Histórico (USD)", stats['max_precio'], FMT_MONEDA),
        ("Precio Mínimo Histórico (USD)", stats['min_precio'], FMT_MONEDA),
        ("Precio Promedio Cierre (USD)", stats['promedio_cierre'], FMT_MONEDA),
        ("Mediana Cambio Horario (%)", stats['mediana_cambio_pct'], "0.000%"),
        ("Volatilidad Horaria (Desv. Est.)", stats['std_precio'], FMT_MONEDA)
    ]
    
    ws_dash.cell(row=5, column=2, value="Métrica Indicadora").font = FONT_HEADER
    ws_dash.cell(row=5, column=2).fill = FILL_HEADER
    ws_dash.cell(row=5, column=3, value="Valor").font = FONT_HEADER
    ws_dash.cell(row=5, column=3).fill = FILL_HEADER
    
    row_curr = 6
    for label, val, num_fmt in kpis:
        c1 = ws_dash.cell(row=row_curr, column=2, value=label)
        c2 = ws_dash.cell(row=row_curr, column=3, value=val)
        c1.font = FONT_BOLD
        c2.font = FONT_BOLD
        c2.number_format = num_fmt
        c1.border = BORDER_THIN
        c2.border = BORDER_THIN
        if row_curr % 2 == 0:
            c1.fill = FILL_ZEBRA
            c2.fill = FILL_ZEBRA
        row_curr += 1

    img_main = os.path.join(carpeta_graficas, "actividad_06_evolucion_precio.png")
    if os.path.exists(img_main):
        img = Image(img_main)
        img.width = 650
        img.height = 320
        ws_dash.add_image(img, "E5")
        
    _ajustar_ancho_columnas(ws_dash)

    # -------------------------------------------------------------------------
    # PESTAÑA 2: Datos_Horarios
    # -------------------------------------------------------------------------
    ws_data = wb.create_sheet(title="Datos_Horarios")
    ws_data.views.sheetView[0].showGridLines = True
    
    headers_h1 = ["Fecha y Hora (UTC)", "Open (USD)", "High (USD)", "Low (USD)", "Close (USD)", "Tick Volume", "Spread"]
    for col_idx, h_text in enumerate(headers_h1, start=1):
        cell = ws_data.cell(row=1, column=col_idx, value=h_text)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        
    for row_idx, row in df_h1.iterrows():
        r = row_idx + 2
        ws_data.cell(row=r, column=1, value=row['time'].strftime('%Y-%m-%d %H:%M')).alignment = ALIGN_CENTER
        ws_data.cell(row=r, column=2, value=row['open']).number_format = FMT_MONEDA
        ws_data.cell(row=r, column=3, value=row['high']).number_format = FMT_MONEDA
        ws_data.cell(row=r, column=4, value=row['low']).number_format = FMT_MONEDA
        ws_data.cell(row=r, column=5, value=row['close']).number_format = FMT_MONEDA
        ws_data.cell(row=r, column=6, value=row['tick_volume']).number_format = "#,##0"
        ws_data.cell(row=r, column=7, value=row.get('spread', 0)).number_format = "#,##0"
        
    _aplicar_formato_tabla(ws_data, 2, len(df_h1) + 1, 1, len(headers_h1))
    ws_data.freeze_panes = "A2"
    _ajustar_ancho_columnas(ws_data)

    # -------------------------------------------------------------------------
    # PESTAÑA 3: Resumen_Diario
    # -------------------------------------------------------------------------
    ws_diario = wb.create_sheet(title="Resumen_Diario")
    ws_diario.views.sheetView[0].showGridLines = True
    
    df_res_diario = analysis.obtener_resumen_diario(df_h1)
    headers_diario = ["Fecha (UTC)", "Apertura (USD)", "Máximo (USD)", "Mínimo (USD)", "Cierre (USD)", "Rango (USD)", "Cambio (%)"]
    
    for col_idx, h_text in enumerate(headers_diario, start=1):
        cell = ws_diario.cell(row=1, column=col_idx, value=h_text)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        
    for row_idx, row in df_res_diario.iterrows():
        r = row_idx + 2
        ws_diario.cell(row=r, column=1, value=str(row['fecha'])).alignment = ALIGN_CENTER
        ws_diario.cell(row=r, column=2, value=row['Apertura']).number_format = FMT_MONEDA
        ws_diario.cell(row=r, column=3, value=row['Máximo']).number_format = FMT_MONEDA
        ws_diario.cell(row=r, column=4, value=row['Mínimo']).number_format = FMT_MONEDA
        ws_diario.cell(row=r, column=5, value=row['Cierre']).number_format = FMT_MONEDA
        ws_diario.cell(row=r, column=6, value=row['Rango']).number_format = FMT_MONEDA
        
        c_pct = ws_diario.cell(row=r, column=7, value=row['Cambio (%)'] / 100.0)
        c_pct.number_format = "0.00%"
        c_pct.font = Font(name="Calibri", size=11, bold=True, color=COLOR_ALCISTA_TEXT if row['Cambio (%)'] >= 0 else COLOR_BAJISTA_TEXT)

    _aplicar_formato_tabla(ws_diario, 2, len(df_res_diario) + 1, 1, len(headers_diario))
    ws_diario.freeze_panes = "A2"
    
    img_diario = os.path.join(carpeta_graficas, "actividad_11_12_resumen_diario.png")
    if os.path.exists(img_diario):
        img = Image(img_diario)
        img.width = 620
        img.height = 300
        ws_diario.add_image(img, "I2")
        
    _ajustar_ancho_columnas(ws_diario)

    # -------------------------------------------------------------------------
    # PESTAÑA 4: Mayores_Movimientos
    # -------------------------------------------------------------------------
    ws_mov = wb.create_sheet(title="Mayores_Movimientos")
    ws_mov.views.sheetView[0].showGridLines = True
    
    top_subidas, top_caidas = analysis.obtener_top_movimientos(df_h1)
    headers_top = ["Fecha y Hora (UTC)", "Cierre (USD)", "Cambio (%)"]

    # Tabla Top Subidas
    ws_mov.cell(row=1, column=1, value="Top 10 Mayores Subidas Horarias (%)").font = FONT_TITULO
    for col_idx, h_text in enumerate(headers_top, start=1):
        cell = ws_mov.cell(row=3, column=col_idx, value=h_text)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        
    for r_idx, row in top_subidas.reset_index(drop=True).iterrows():
        r = r_idx + 4
        ws_mov.cell(row=r, column=1, value=pd.to_datetime(row['time'], utc=True).strftime('%Y-%m-%d %H:%M')).alignment = ALIGN_CENTER
        ws_mov.cell(row=r, column=2, value=row['close']).number_format = FMT_MONEDA
        c_p = ws_mov.cell(row=r, column=3, value=row['cambio_pct'] / 100.0)
        c_p.number_format = "0.00%"
        c_p.font = Font(name="Calibri", size=11, bold=True, color=COLOR_ALCISTA_TEXT)
        
    _aplicar_formato_tabla(ws_mov, 4, 3 + len(top_subidas), 1, 3)

    # Tabla Top Caídas
    ws_mov.cell(row=1, column=5, value="Top 10 Mayores Caídas Horarias (%)").font = FONT_TITULO
    for col_idx, h_text in enumerate(headers_top, start=5):
        cell = ws_mov.cell(row=3, column=col_idx, value=h_text)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        
    for r_idx, row in top_caidas.reset_index(drop=True).iterrows():
        r = r_idx + 4
        ws_mov.cell(row=r, column=5, value=pd.to_datetime(row['time'], utc=True).strftime('%Y-%m-%d %H:%M')).alignment = ALIGN_CENTER
        ws_mov.cell(row=r, column=6, value=row['close']).number_format = FMT_MONEDA
        c_p = ws_mov.cell(row=r, column=7, value=row['cambio_pct'] / 100.0)
        c_p.number_format = "0.00%"
        c_p.font = Font(name="Calibri", size=11, bold=True, color=COLOR_BAJISTA_TEXT)
        
    _aplicar_formato_tabla(ws_mov, 4, 3 + len(top_caidas), 5, 7)
    
    img_sub_cai = os.path.join(carpeta_graficas, "actividad_08_09_top_subidas_caidas.png")
    if os.path.exists(img_sub_cai):
        img = Image(img_sub_cai)
        img.width = 650
        img.height = 290
        ws_mov.add_image(img, "A16")
        
    _ajustar_ancho_columnas(ws_mov)

    # -------------------------------------------------------------------------
    # PESTAÑA 5: Patrones_y_Estadisticas
    # -------------------------------------------------------------------------
    ws_pat = wb.create_sheet(title="Patrones_y_Estadisticas")
    ws_pat.views.sheetView[0].showGridLines = True
    
    df_clasif = analysis.clasificar_velas(df_h1)
    ws_pat.cell(row=1, column=1, value="Distribución por Tipo de Vela").font = FONT_TITULO
    ws_pat.cell(row=3, column=1, value="Tipo de Vela").font = FONT_HEADER
    ws_pat.cell(row=3, column=1).fill = FILL_HEADER
    ws_pat.cell(row=3, column=2, value="Cantidad").font = FONT_HEADER
    ws_pat.cell(row=3, column=2).fill = FILL_HEADER
    ws_pat.cell(row=3, column=3, value="Proporción (%)").font = FONT_HEADER
    ws_pat.cell(row=3, column=3).fill = FILL_HEADER
    
    for r_idx, row in df_clasif.iterrows():
        r = r_idx + 4
        ws_pat.cell(row=r, column=1, value=row['Tipo_Vela']).alignment = ALIGN_LEFT
        ws_pat.cell(row=r, column=2, value=row['Cantidad']).number_format = "#,##0"
        c_pr = ws_pat.cell(row=r, column=3, value=row['Proporcion_Pct'] / 100.0)
        c_pr.number_format = "0.00%"
        
    _aplicar_formato_tabla(ws_pat, 4, 3 + len(df_clasif), 1, 3)
    
    img_hora = os.path.join(carpeta_graficas, "actividad_13_comportamiento_hora_utc.png")
    if os.path.exists(img_hora):
        img = Image(img_hora)
        img.width = 560
        img.height = 270
        ws_pat.add_image(img, "E1")
        
    img_dia = os.path.join(carpeta_graficas, "actividad_14_comportamiento_dia_semana.png")
    if os.path.exists(img_dia):
        img = Image(img_dia)
        img.width = 560
        img.height = 270
        ws_pat.add_image(img, "E15")
        
    _ajustar_ancho_columnas(ws_pat)

    # Guardar reporte en disco
    wb.save(ruta_salida_excel)
    return ruta_salida_excel


if __name__ == "__main__":
    ruta_datos = os.path.join("data", "HBARUSD_H1_actual.csv")
    if os.path.exists(ruta_datos):
        salida = generar_reporte_excel_completo(ruta_datos)
        print(f"Reporte generado exitosamente en: {salida}")
    else:
        print(f"No se encontró el archivo de datos por defecto en {ruta_datos}. Ejecute main.py primero.")