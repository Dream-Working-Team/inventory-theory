"""
Parcial II - Ejercicio 3: Modelo Multi-Artículo con Restricción de Recursos (Lagrange).
Universidad José Antonio Páez - Escuela de Ingeniería en Computación.

Enunciado:
- Artículo A: Demanda mensual 300 u (3,600 u/año), S = $30, H = $5/u/año, C = $30, d = 10 u/día, LT = 3 días
- Artículo B: Demanda mensual 250 u (3,000 u/año), S = $35, H = $6/u/año, C = $35, d = 8 u/día,  LT = 4 días
- Artículo C: Demanda mensual 400 u (4,800 u/año), S = $40, H = $7/u/año, C = $40, d = 15 u/día, LT = 5 días
- Límite de Capacidad de Almacén: 700 unidades
- Presupuesto Disponible de Capital: $8,000.00
"""

import sys
import os
import math

# Asegurar importación de la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.restricciones import ModeloRestricciones, ArticuloRestriccion
from services.exportador import ExportadorServicio


def resolver_ejercicio3(exportar: bool = True) -> ModeloRestricciones:
    """Resuelve el Ejercicio 3 del Parcial II con métricas mensuales y anuales."""
    articulos_data = [
        {"nombre": "Artículo A", "D_mes": 300, "D_anual": 3600, "S": 30.0, "H": 5.0, "C": 30.0, "d_dia": 10, "LT": 3},
        {"nombre": "Artículo B", "D_mes": 250, "D_anual": 3000, "S": 35.0, "H": 6.0, "C": 35.0, "d_dia": 8,  "LT": 4},
        {"nombre": "Artículo C", "D_mes": 400, "D_anual": 4800, "S": 40.0, "H": 7.0, "C": 40.0, "d_dia": 15, "LT": 5},
    ]

    limite_capacidad = 700.0
    presupuesto_capital = 8000.0

    articulos_poo = [
        ArticuloRestriccion(
            nombre=art["nombre"],
            demanda_anual=art["D_anual"],
            costo_pedido=art["S"],
            costo_unitario=art["C"],
            costo_almacenamiento=art["H"],
            espacio_unitario=1.0
        )
        for art in articulos_data
    ]

    modelo_presupuesto = ModeloRestricciones(
        limite_recurso=presupuesto_capital,
        tipo_restriccion="presupuesto",
        es_inventario_promedio=False,
        articulos=articulos_poo,
        nombre="Parcial II - Ejercicio 3: Multi-Artículo con Restricciones (Lagrange)"
    )
    modelo_presupuesto.calcular()

    # Construir reporte detallado con unidades de tiempo en meses y días
    lineas = [
        "=" * 84,
        "  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA",
        "  ESCUELA DE INGENIERÍA EN COMPUTACIÓN",
        "  CÁTEDRA: MÉTODOS CUANTITATIVOS / TEORÍA DE INVENTARIOS",
        "  PARCIAL II - EJERCICIO 3: GESTIÓN MULTI-ARTÍCULO CON RESTRICCIONES",
        "=" * 84,
        "",
        "1. PARÁMETROS INICIALES DE LOS ARTÍCULOS:",
        f"   {'Art.':<12}{'D (mes)':<10}{'D (año)':<10}{'S ($)':<8}{'H ($/u/año)':<12}{'C ($)':<8}{'d (u/día)':<10}{'LT (días)':<10}",
        "   " + "-" * 80,
    ]
    for art in articulos_data:
        lineas.append(
            f"   {art['nombre']:<12}{art['D_mes']:<10}{art['D_anual']:<10}{art['S']:<8.2f}{art['H']:<12.2f}{art['C']:<8.2f}{art['d_dia']:<10}{art['LT']:<10}"
        )
    lineas.append("   " + "-" * 80)
    lineas.append(f"   • Capacidad de Almacén:   {limite_capacidad:,.0f} unidades")
    lineas.append(f"   • Presupuesto Disponible: ${presupuesto_capital:,.2f}")
    lineas.append("")

    # Análisis sin restricción
    lineas.append("2. EVALUACIÓN DE FACTIBILIDAD Y OPTIMIZACIÓN (LAGRANGE):")
    lineas.append("   a) Solución Individual Libre (EOQ Clásico Wilson):")
    suma_eoq = 0.0
    inversion_eoq = 0.0
    costo_eoq_total = 0.0
    for art in articulos_data:
        q_eoq = math.sqrt((2 * art["D_anual"] * art["S"]) / art["H"])
        inv = q_eoq * art["C"]
        c_tot = (art["D_anual"] / q_eoq) * art["S"] + (q_eoq / 2.0) * art["H"]
        suma_eoq += q_eoq
        inversion_eoq += inv
        costo_eoq_total += c_tot
        lineas.append(f"      • {art['nombre']}: EOQ = {q_eoq:6.2f} u | Inversión = ${inv:8.2f} | Costo Ord+Mant = ${c_tot:7.2f}")

    lineas.append(f"      TOTALES SIN RESTRICCIÓN: Suma Lotes = {suma_eoq:6.2f} u | Inversión = ${inversion_eoq:8.2f} | CT = ${costo_eoq_total:7.2f}")
    lineas.append("")
    lineas.append("   b) Diagnóstico de Restricciones:")
    lineas.append(f"      • Restricción de Capacidad ({limite_capacidad:.0f} u):   {suma_eoq:.2f} <= {limite_capacidad:.0f} -> CUMPLE (Holgura: {limite_capacidad - suma_eoq:.2f} u)")
    lineas.append(f"      • Restricción de Presupuesto (${presupuesto_capital:.2f}): ${inversion_eoq:.2f} > ${presupuesto_capital:.2f} -> NO CUMPLE (RESTRICCIÓN ACTIVA)")
    lineas.append("")

    # Solución ajustada con Lagrange
    lambda_opt = modelo_presupuesto.lambda_opt
    lineas.append("3. SOLUCIÓN ÓPTIMA CON MULTIPLICADORES DE LAGRANGE:")
    lineas.append(f"   • Multiplicador de Lagrange Óptimo (λ*): {lambda_opt:.6f}")
    lineas.append("   • Fórmula: Q_i*(λ*) = sqrt( (2 * D_i * S_i) / (H_i + 2 * λ* * C_i) )")
    lineas.append("")
    lineas.append(f"   {'Art.':<12}{'Q* Óptimo':<11}{'ROP (u)':<9}{'N (ped/mes)':<13}{'N (ped/año)':<13}{'T (meses)':<11}{'T (días)':<10}{'Inversión ($)':<15}{'CT ($/año)':<10}")
    lineas.append("   " + "-" * 105)

    total_q_opt = 0.0
    total_inv_opt = 0.0
    total_ct = 0.0

    for res, art in zip(modelo_presupuesto.resultados_articulos, articulos_data):
        q_opt = res.q_con_restriccion
        rop = art["d_dia"] * art["LT"]
        n_ped_mes = art["D_mes"] / q_opt
        n_ped_ano = art["D_anual"] / q_opt
        t_meses = q_opt / art["D_mes"]
        t_dias = t_meses * 30.0
        inv = q_opt * art["C"]
        c_ord = (art["D_anual"] / q_opt) * art["S"]
        c_mant = (q_opt / 2.0) * art["H"]
        ct = c_ord + c_mant

        total_q_opt += q_opt
        total_inv_opt += inv
        total_ct += ct

        lineas.append(
            f"   {art['nombre']:<12}{q_opt:<11.2f}{rop:<9}{n_ped_mes:<13.2f}{n_ped_ano:<13.2f}{t_meses:<11.3f}{t_dias:<10.1f}${inv:<14.2f}${ct:<9.2f}"
        )

    lineas.append("   " + "-" * 105)
    lineas.append(
        f"   TOTALES:{'':<4}{total_q_opt:<11.2f}{'':<9}{'':<13}{'':<13}{'':<11}{'':<10}${total_inv_opt:<14.2f}${total_ct:<9.2f}"
    )
    lineas.append("")

    # Políticas operativas con unidades de tiempo en meses
    lineas.append("4. PUNTOS DE REORDEN (ROP) Y POLÍTICAS OPERATIVAS CON UNIDADES DE TIEMPO:")
    for art, res in zip(articulos_data, modelo_presupuesto.resultados_articulos):
        q_red = round(res.q_con_restriccion)
        rop = art["d_dia"] * art["LT"]
        t_m = res.q_con_restriccion / art["D_mes"]
        t_d = t_m * 30.0
        n_m = art["D_mes"] / res.q_con_restriccion
        lineas.append(
            f"   • {art['nombre']}:\n"
            f"     - Tamaño de Pedido Óptimo (Q*): {res.q_con_restriccion:.2f} unidades (~{q_red} u).\n"
            f"     - Frecuencia de Pedidos: {n_m:.2f} pedidos/mes ({n_m * 12:.2f} pedidos/año).\n"
            f"     - Tiempo entre Pedidos (T): {t_m:.3f} meses ({t_d:.1f} días).\n"
            f"     - Punto de Reorden (ROP): {rop} unidades (Demanda de {art['d_dia']} u/día x {art['LT']} días de Lead Time).\n"
            f"     - Política: Ordenar {q_red} unidades cada {t_m:.2f} meses ({t_d:.1f} días) cuando el stock llegue a {rop} unidades.\n"
        )

    lineas.append("=" * 84)
    lineas.append("5. CONCLUSIÓN DEL PROBLEMA (PARA HOJA DE EXAMEN):")
    lineas.append("=" * 84)
    lineas.append("a) RESTRICCIÓN DOMINANTE: El factor crítico limitante es el PRESUPUESTO de $8,000.00,")
    lineas.append(f"   el cual se agota al 100% (inversión total = ${total_inv_opt:,.2f}). La capacidad física")
    lineas.append(f"   de almacén de 700 unidades no se satura, utilizándose únicamente {total_q_opt:.2f} unidades")
    lineas.append(f"   (holgura de {limite_capacidad - total_q_opt:.2f} unidades disponibles).")
    lineas.append("")
    lineas.append("b) TAMAÑOS ÓPTIMOS DE PEDIDO AJUSTADOS (Q*):")
    for res in modelo_presupuesto.resultados_articulos:
        lineas.append(f"   • {res.nombre}: Q* = {res.q_con_restriccion:.2f} unidades (~{round(res.q_con_restriccion)} unidades).")
    lineas.append("")
    lineas.append("c) PUNTOS DE REORDEN (ROP):")
    for art in articulos_data:
        rop = art["d_dia"] * art["LT"]
        lineas.append(f"   • {art['nombre']}: ROP = {rop} unidades (Demanda de {art['d_dia']} u/día x {art['LT']} días de Lead Time).")
    lineas.append("")
    lineas.append(f"d) COSTO TOTAL ANUAL DE OPERACIÓN: ${total_ct:,.2f} anuales (pedidos + mantenimiento),")
    lineas.append(f"   presentando un sobrecosto por restricción de capital de ${total_ct - costo_eoq_total:,.2f} anuales.")
    lineas.append(f"   El multiplicador de Lagrange λ* = {lambda_opt:.6f} indica que cada dólar adicional de")
    lineas.append(f"   presupuesto reduciría el costo total de inventario en ${lambda_opt:.4f}.")
    lineas.append("=" * 84)

    texto_final = "\n".join(lineas)

    if exportar:
        ruta = ExportadorServicio.normalizar_ruta("salida_ejercicio3.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto_final)
            f.write("\n\n" + "=" * 84 + "\n")
            f.write("  Generado por el Sistema POO de Teoría de Inventarios - UJAP\n")
            f.write("=" * 84 + "\n")
        print(f"[OK] Ejercicio 3 exportado en: {ruta}")

    return modelo_presupuesto


if __name__ == "__main__":
    resolver_ejercicio3(exportar=True)
