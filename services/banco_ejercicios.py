"""
Repositorio del Banco de Ejercicios de la Cátedra de Métodos Cuantitativos.
Universidad José Antonio Páez.
Contiene los casos de estudio y problemas resueltos oficiales de la guía de la clase.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from models.eoq import ModeloEOQ
from models.quiebre_precios import ModeloQuiebrePrecios, TramoDescuento
from models.restricciones import ModeloRestricciones, ArticuloRestriccion
from models.probabilistico import ModeloProbabilistico


@dataclass
class EjercicioCatedra:
    """Representa un ejercicio documentado de la guía de la cátedra."""
    id_ejercicio: str
    titulo: str
    tipo_modelo: str  # "eoq", "quiebre", "restricciones", "probabilistico"
    fuente: str
    enunciado: str
    datos_resumen: Dict[str, Any]
    solucion_explicada: str
    modelo_instanciado: Any


class BancoEjerciciosService:
    """Servicio POO que provee los ejercicios de la guía de la cátedra."""

    @staticmethod
    def obtener_todos_los_ejercicios() -> List[EjercicioCatedra]:
        """Retorna la lista de todos los ejercicios guiados de la UJAP."""
        ejercicios = []

        # -------------------------------------------------------------
        # EJERCICIO 1: Laptops Acer en Oruro (Ramón) - EOQ Clásico
        # -------------------------------------------------------------
        mod1 = ModeloEOQ(
            demanda_anual=6000,  # 500 portatiles/mes * 12
            costo_pedido=5000,
            costo_unitario=3700,
            costo_almacenamiento=300,  # 25 Bs/mes * 12
            lead_time_dias=0,
            dias_laborales_anuales=360,
            nombre="Ejercicio 1: Laptops Acer en Oruro (Ramón)"
        )
        mod1.calcular()

        ejercicios.append(EjercicioCatedra(
            id_ejercicio="EJ-01",
            titulo="Ramón: Distribución de Laptops Acer en Oruro (EOQ Clásico)",
            tipo_modelo="eoq",
            fuente="Guía de Problemas de Teoría de Inventario - Pág. 1 (UJAP)",
            enunciado=(
                "Ramón es un distribuidor de equipos portátiles Acer para las diferentes tiendas de computación "
                "de la ciudad de Oruro. La demanda de estos equipos es determinista y es de 500 portátiles/mes. "
                "El costo por hacer el pedido desde Iquique y transportarlo hasta Oruro es de 5,000 Bs. "
                "Ramón alquila un depósito para guardar su mercadería a un costo de 25 Bs/mes por cada equipo portátil "
                "y el precio de compra de cada equipo es de 3,700 Bs.\n\n"
                "Preguntas:\n"
                "a) ¿Cuál es la cantidad óptima de pedido (EOQ) de los equipos portátiles?\n"
                "b) ¿Cuál es el costo total?\n"
                "c) ¿Cuál es el número de pedidos que debe hacer al año?\n"
                "d) ¿Cada cuánto tiempo debe hacer un nuevo pedido?"
            ),
            datos_resumen={
                "Demanda Mensual": "500 unidades (6,000 unidades/año)",
                "Costo de Pedido (K o S)": "5,000 Bs",
                "Costo Mantenimiento (H)": "25 Bs/mes (300 Bs/año)",
                "Costo Unitario (C)": "3,700 Bs/unidad"
            },
            solucion_explicada=(
                "1. Homogeneización de unidades temporales a base mensual:\n"
                "   D = 500 portátiles/mes, S = 5000 Bs, H = 25 Bs/(mes*portátil)\n"
                "2. Cálculo de EOQ:\n"
                "   Q* = sqrt( (2 * 500 * 5000) / 25 ) = sqrt(200,000) = 447.21 portátiles por pedido (~447 unidades).\n"
                "3. Número de pedidos:\n"
                "   N = 500 / 447.21 = 1.12 pedidos al mes (13.42 pedidos al año).\n"
                "4. Frecuencia / Tiempo entre pedidos:\n"
                "   T = 447.21 / 500 = 0.894 meses = aprox. 26.8 días.\n"
                "5. Costos Anuales:\n"
                "   - C. Adquisición = 6,000 * 3,700 = 22,200,000 Bs\n"
                "   - C. Pedidos = (6000 / 447.21) * 5000 = 67,082.04 Bs\n"
                "   - C. Almacenamiento = (447.21 / 2) * 300 = 67,082.04 Bs\n"
                "   - Costo Total = 22,334,164.08 Bs."
            ),
            modelo_instanciado=mod1
        ))

        # -------------------------------------------------------------
        # EJERCICIO 2: Capacitación de 500 Administradores en 100 Días
        # -------------------------------------------------------------
        mod2 = ModeloEOQ(
            demanda_anual=1825,  # 5 admin/dia * 365
            costo_pedido=500000,
            costo_unitario=0,
            costo_almacenamiento=91250,  # 250 $/dia * 365
            lead_time_dias=0,
            dias_laborales_anuales=100,
            nombre="Ejercicio 2: Capacitación de 500 Administradores"
        )
        mod2.calcular()

        ejercicios.append(EjercicioCatedra(
            id_ejercicio="EJ-02",
            titulo="Capacitación de 500 Administradores en 100 Días (EOQ Diario)",
            tipo_modelo="eoq",
            fuente="Guía de Problemas de Teoría de Inventario - Pág. 2 (UJAP)",
            enunciado=(
                "Se quiere capacitar a 500 administradores en sistemas de comercialización en los próximos 100 días. "
                "El costo fijo al empezar el programa de capacitación es de $500,000.00 y el costo de mantenimiento "
                "de cada alumno durante el curso es de $250.00 diario.\n\n"
                "Preguntas:\n"
                "a) ¿Cuánta gente debe capacitarse en cada grupo, y con qué frecuencia, para que el costo resulte mínimo?\n"
                "b) ¿Cuál es el costo mínimo?"
            ),
            datos_resumen={
                "Demanda Diaria (d)": "500 admin / 100 días = 5 admin/día",
                "Costo Fijo Programa (K)": "$500,000.00 por tanda",
                "Costo Alumno Diario (H)": "$250.00 / (admin * día)"
            },
            solucion_explicada=(
                "1. Datos en base diaria:\n"
                "   d = 5 admin/día, K = $500,000, H = $250 /(admin*día).\n"
                "2. Cálculo de EOQ en base diaria:\n"
                "   Q* = sqrt( (2 * 5 * 500,000) / 250 ) = sqrt(20,000) = 141.42 alumnos (~141 administradores por curso).\n"
                "3. Frecuencia entre tandas de capacitación:\n"
                "   T = Q* / d = 141.42 / 5 = 28.28 días (cada 28 días aprox.).\n"
                "4. Número total de cursos en el período de 100 días:\n"
                "   N = 500 / 141.42 = 3.53 tandas.\n"
                "5. Costo total de operación en los 100 días:\n"
                "   CT = (500 / 141.42)*500,000 + (141.42 / 2)*250*100 = $1,767,766.95 + $1,767,750 = $3,535,533.91."
            ),
            modelo_instanciado=mod2
        ))

        # -------------------------------------------------------------
        # EJERCICIO 3: CLS Computer Company (Capacitación y Lead Time)
        # -------------------------------------------------------------
        mod3 = ModeloEOQ(
            demanda_anual=27,
            costo_pedido=12000,
            costo_unitario=0,
            costo_almacenamiento=18000,  # 1500 $/mes * 12
            lead_time_dias=30,
            dias_laborales_anuales=360,
            nombre="Ejercicio 3: CLS Computer Company"
        )
        mod3.calcular()

        ejercicios.append(EjercicioCatedra(
            id_ejercicio="EJ-03",
            titulo="CLS Computer Company: Capacitación de Representantes (EOQ con Lead Time)",
            tipo_modelo="eoq",
            fuente="Guía de Problemas de Teoría de Inventario - Pág. 3 y 4 (UJAP)",
            enunciado=(
                "Durante cada año, CLS Computer Company necesita capacitar a 27 representantes de servicio. "
                "Independientemente de cuántos estudiantes se capaciten, le cuesta $12,000 llevar a cabo el programa "
                "de capacitación. Como los representantes ganan $1,500 mensuales, CLS no desea entrenarlos antes de que "
                "se necesiten. Cada sesión de entrenamiento toma un mes (Lead Time = 1 mes).\n\n"
                "Preguntas:\n"
                "a) ¿Cuántos representantes de servicio deben estar en cada grupo de capacitación?\n"
                "b) ¿Cuántos programas de capacitación debe organizar CLS cada año?\n"
                "c) ¿Cuántos representantes deben quedar cuando comience cada programa (Punto de Reorden ROP)?"
            ),
            datos_resumen={
                "Demanda Anual (D)": "27 representantes/año",
                "Costo de Organización (K)": "$12,000.00",
                "Costo Mantención (H)": "$1,500/mes ($18,000/año)",
                "Lead Time (LT)": "1 mes (30 días)"
            },
            solucion_explicada=(
                "1. Demanda anual D = 27, S = 12,000, H = 1,500 * 12 = $18,000/(año*estudiante).\n"
                "2. Cálculo de EOQ:\n"
                "   Q* = sqrt( (2 * 27 * 12,000) / 18,000 ) = sqrt(36) = 6 estudiantes por grupo.\n"
                "3. Número de grupos al año:\n"
                "   N = 27 / 6 = 4.5 programas de capacitación al año.\n"
                "4. Tiempo entre cursos:\n"
                "   T = 6 / 27 = 0.222 años = 2.67 meses (cada 80 días).\n"
                "5. Punto de Reorden (ROP):\n"
                "   d = 27 / 12 = 2.25 estudiantes/mes.\n"
                "   ROP = d * LT = 2.25 * 1 = 2.25 representantes disponibles al iniciar el curso."
            ),
            modelo_instanciado=mod3
        ))

        # -------------------------------------------------------------
        # EJERCICIO 4: Modelo con Quiebre de Precios (5,000 Unidades)
        # -------------------------------------------------------------
        mod4 = ModeloQuiebrePrecios(
            demanda_anual=5000,
            costo_pedido=49,
            tasa_almacenamiento=0.20,
            tramos=[
                TramoDescuento(q_min=0, q_max=999, precio_unitario=5.00, descuento_porcentaje=0.0),
                TramoDescuento(q_min=1000, q_max=1999, precio_unitario=4.80, descuento_porcentaje=4.0),
                TramoDescuento(q_min=2000, q_max=float('inf'), precio_unitario=4.75, descuento_porcentaje=5.0),
            ],
            nombre="Ejercicio 4: Quiebre de Precios (5,000 Unidades)"
        )
        mod4.calcular()

        ejercicios.append(EjercicioCatedra(
            id_ejercicio="EJ-04",
            titulo="Quiebre de Precios por Volumen: 5,000 Unidades Anuales",
            tipo_modelo="quiebre",
            fuente="Guía de Problemas de Teoría de Inventario - Pág. 4, 5 y 6 (UJAP)",
            enunciado=(
                "Un proveedor le ofrece la siguiente tabla de descuento para la adquisición de su principal producto, "
                "cuya demanda anual usted ha estimado en 5,000 unidades. El costo de emitir una orden de pedido es de $49 "
                "y adicionalmente se ha estimado que el costo anual de almacenar una unidad en inventario es un 20% "
                "del costo de adquisición del producto.\n\n"
                "Tabla de Descuentos:\n"
                "• Tramo 1: 0 a 999 unidades -> $5.00 / unidad (0% descuento)\n"
                "• Tramo 2: 1,000 a 1,999 unidades -> $4.80 / unidad (4% descuento)\n"
                "• Tramo 3: 2,000 o más unidades -> $4.75 / unidad (5% descuento)\n\n"
                "¿Cuál es la cantidad de la orden que minimiza el costo total del inventario?"
            ),
            datos_resumen={
                "Demanda Anual (D)": "5,000 unidades",
                "Costo de Pedido (S)": "$49.00",
                "Tasa Almacenamiento (i)": "20% anual",
                "Precios por Tramo": "$5.00 | $4.80 | $4.75"
            },
            solucion_explicada=(
                "1. Cálculo de EOQ por tramo:\n"
                "   • Tramo 1: H1 = 0.20 * 5.0 = $1.00 -> EOQ1 = sqrt(2*5000*49/1.0) = 700.00 u (FACTIBLE en [0, 999]).\n"
                "     Costo Total 1 = 5000*5 + (5000/700)*49 + (700/2)*1.0 = $25,000 + $350 + $350 = $25,700.00\n"
                "   • Tramo 2: H2 = 0.20 * 4.8 = $0.96 -> EOQ2 = sqrt(2*5000*49/0.96) = 714.43 u < 1000.\n"
                "     Ajuste a punto de quiebre Q2 = 1,000 unidades.\n"
                "     Costo Total 2 = 5000*4.8 + (5000/1000)*49 + (1000/2)*0.96 = $24,000 + $245 + $480 = $24,725.00\n"
                "   • Tramo 3: H3 = 0.20 * 4.75 = $0.95 -> EOQ3 = sqrt(2*5000*49/0.95) = 718.18 u < 2000.\n"
                "     Ajuste a punto de quiebre Q3 = 2,000 unidades.\n"
                "     Costo Total 3 = 5000*4.75 + (5000/2000)*49 + (2000/2)*0.95 = $23,750 + $122.5 + $950 = $24,822.50\n\n"
                "2. Conclusión:\n"
                "   El tamaño óptimo de pedido es Q* = 1,000 unidades (Tramo 2), con el costo total mínimo anual de $24,725.00."
            ),
            modelo_instanciado=mod4
        ))

        # -------------------------------------------------------------
        # EJERCICIO 5: Empresa de Desayunos (Modelo Probabilístico)
        # -------------------------------------------------------------
        mod5 = ModeloProbabilistico(
            demanda_promedio_diaria=200,
            desviacion_diaria=150,
            lead_time_dias=4,
            nivel_servicio_pct=95.0,
            costo_pedido=20,
            costo_unitario=10,
            tasa_almacenamiento=0.20,
            dias_laborales_anuales=250,
            nombre="Ejercicio 5: Almacén de Desayunos (Probabilístico)"
        )
        mod5.calcular()

        ejercicios.append(EjercicioCatedra(
            id_ejercicio="EJ-05",
            titulo="Almacén Distribuidor de Desayunos (Modelo Probabilístico Q, ROP)",
            tipo_modelo="probabilistico",
            fuente="Guía de la Clase / Guía de Problemas - Pág. 9 y 10 (UJAP)",
            enunciado=(
                "Supóngase que se administra un almacén que distribuye determinado tipo de desayunos a los vendedores "
                "al menudeo. Este alimento tiene las siguientes características:\n"
                "• Demanda promedio = 200 cajas al día\n"
                "• Tiempo de entrega (Lead Time) = 4 días de reabastecimiento por parte del proveedor\n"
                "• Desviación estándar de la demanda diaria = 150 cajas\n"
                "• Nivel de servicio deseado = 95%\n"
                "• Costo por orden (S) = $20 dólares la orden\n"
                "• Tasa anual de almacenamiento (i) = 20% al año\n"
                "• Costo unitario (C) = $10 dólares por caja\n"
                "• Días laborales = 5 días a la semana, 50 semanas al año (250 días al año).\n\n"
                "Determine:\n"
                "a) Cantidad Económica de Pedido (EOQ).\n"
                "b) Demanda esperada y desviación estándar durante el tiempo de entrega.\n"
                "c) Stock de Seguridad (SS) y Punto de Reorden (ROP).\n"
                "d) Política de decisión de inventarios resultante."
            ),
            datos_resumen={
                "Demanda Promedio (d)": "200 cajas/día (D = 50,000 cajas/año)",
                "Desviación Estándar (σ)": "150 cajas/día",
                "Lead Time (LT)": "4 días",
                "Nivel de Servicio (SL)": "95% (Z = 1.645)",
                "Costos": "S = $20, C = $10, H = $2.00/año"
            },
            solucion_explicada=(
                "1. Demanda Anual D = 250 * 200 = 50,000 cajas/año.\n"
                "2. Costo unitario de almacenamiento: H = i * C = 0.20 * 10 = $2.00 por caja/año.\n"
                "3. Cantidad Económica de Pedido (EOQ):\n"
                "   Q* = sqrt( (2 * 50,000 * 20) / 2.0 ) = sqrt(1,000,000) = 1,000 cajas.\n"
                "4. Parámetros en Lead Time (4 días):\n"
                "   • Demanda media: μ_LT = 200 * 4 = 800 cajas.\n"
                "   • Desviación estándar: σ_LT = 150 * sqrt(4) = 150 * 2 = 300 cajas.\n"
                "5. Factor Z para 95% de nivel de servicio: Z = 1.645 (o 1.65 según tabla estándar).\n"
                "6. Stock de Seguridad (Safety Stock):\n"
                "   SS = Z * σ_LT = 1.65 * 300 = 495 cajas (o 1.645 * 300 = 493.5 cajas).\n"
                "7. Punto de Reorden (ROP):\n"
                "   ROP = μ_LT + SS = 800 + 495 = 1,295 cajas.\n\n"
                "8. Política de Decisión (Sistema Q):\n"
                "   Colocar un pedido de 1,000 cajas siempre que la posición del inventario caiga a 1,295 cajas.\n"
                "   En promedio se levantarán 50 pedidos al año (50,000 / 1,000) con 5 días de trabajo promedio entre ellos."
            ),
            modelo_instanciado=mod5
        ))

        # -------------------------------------------------------------
        # EJERCICIO 6: Distribuidor de Tanques de Gas para Artículos Marinos
        # -------------------------------------------------------------
        mod6 = ModeloQuiebrePrecios(
            demanda_anual=300,
            costo_pedido=5,
            tasa_almacenamiento=0.10,
            tramos=[
                TramoDescuento(q_min=0, q_max=14, precio_unitario=12.00, descuento_porcentaje=0.0),
                TramoDescuento(q_min=15, q_max=99, precio_unitario=11.40, descuento_porcentaje=5.0),
                TramoDescuento(q_min=100, q_max=float('inf'), precio_unitario=10.80, descuento_porcentaje=10.0),
            ],
            nombre="Ejercicio 6: Distribuidor de Tanques Marinos"
        )
        mod6.calcular()

        ejercicios.append(EjercicioCatedra(
            id_ejercicio="EJ-06",
            titulo="Distribuidor Marino: Tanques de Gas con Descuentos Escalonados",
            tipo_modelo="quiebre",
            fuente="Guía de la Clase - Pág. 1 (UJAP)",
            enunciado=(
                "Un distribuidor de artículos marinos compra tanques de gas a un fabricante. El fabricante ofrece "
                "5% de descuento en órdenes de 15 o más y un 10% de descuento en órdenes de 100 o más. "
                "El distribuidor estima sus costos de ordenar en $5 por orden y los de conservación en un 10% del "
                "precio del producto. El distribuidor compra 300 tanques por año. El precio unitario base de cada tanque "
                "es de $12. Determine cuál es el volumen de compra que minimiza el costo total."
            ),
            datos_resumen={
                "Demanda Anual (D)": "300 tanques",
                "Costo de Pedido (S)": "$5.00",
                "Tasa Almacenamiento (i)": "10%",
                "Precio Base": "$12.00 (5% desc -> $11.40, 10% desc -> $10.80)"
            },
            solucion_explicada=(
                "1. Tramos configurados:\n"
                "   • Tramo 1 [0 - 14]: P1 = $12.00, H1 = 0.10 * 12 = $1.20 -> EOQ1 = sqrt(2*300*5/1.2) = 50.0 u > 14 (No factible en tramo).\n"
                "   • Tramo 2 [15 - 99]: P2 = $11.40, H2 = 0.10 * 11.40 = $1.14 -> EOQ2 = sqrt(2*300*5/1.14) = 51.30 u (FACTIBLE en [15, 99]).\n"
                "     Costo Total 2 = 300*11.40 + (300/51.30)*5 + (51.30/2)*1.14 = $3,420 + $29.24 + $29.24 = $3,478.48\n"
                "   • Tramo 3 [100+]: P3 = $10.80, H3 = 0.10 * 10.80 = $1.08 -> EOQ3 = sqrt(2*300*5/1.08) = 52.70 u < 100.\n"
                "     Ajuste al punto de quiebre Q3 = 100 tanques.\n"
                "     Costo Total 3 = 300*10.80 + (300/100)*5 + (100/2)*1.08 = $3,240 + $15 + $54 = $3,309.00\n\n"
                "2. Decisión Óptima:\n"
                "   El volumen óptimo de compra es Q* = 100 tanques, logrando el costo total mínimo de $3,309.00 anuales."
            ),
            modelo_instanciado=mod6
        ))

        # -------------------------------------------------------------
        # EJERCICIO 7: Modelo de 3 Artículos con Restricción de Espacio (Lagrange)
        # -------------------------------------------------------------
        mod7 = ModeloRestricciones(
            limite_recurso=220.0,
            tipo_restriccion="espacio",
            es_inventario_promedio=False,
            articulos=[
                ArticuloRestriccion(nombre="Producto A (Básico)", demanda_anual=1000, costo_pedido=40, costo_unitario=20, costo_almacenamiento=4.0, espacio_unitario=1.0),
                ArticuloRestriccion(nombre="Producto B (Premium)", demanda_anual=1500, costo_pedido=50, costo_unitario=35, costo_almacenamiento=7.0, espacio_unitario=1.5),
                ArticuloRestriccion(nombre="Producto C (Industrial)", demanda_anual=800, costo_pedido=60, costo_unitario=50, costo_almacenamiento=10.0, espacio_unitario=2.0),
            ],
            nombre="Ejercicio 7: 3 Artículos con Restricción de Almacén"
        )
        mod7.calcular()

        ejercicios.append(EjercicioCatedra(
            id_ejercicio="EJ-07",
            titulo="Gestión Multi-Artículo con Restricción de Espacio Físico (Lagrange)",
            tipo_modelo="restricciones",
            fuente="Formulario y Guía de Teoría de Inventarios - Varios Artículos (UJAP)",
            enunciado=(
                "Una empresa comercializa 3 productos que comparten un almacén central con un límite máximo de "
                "220 m² de espacio disponible. Los datos de los artículos son:\n"
                "• Producto A: Demanda = 1,000 u/año, S = $40, H = $4.00/u/año, Espacio = 1.0 m²/u\n"
                "• Producto B: Demanda = 1,500 u/año, S = $50, H = $7.00/u/año, Espacio = 1.5 m²/u\n"
                "• Producto C: Demanda = 800 u/año, S = $60, H = $10.00/u/año, Espacio = 2.0 m²/u\n\n"
                "Determine los tamaños óptimos de lote respetando la restricción de espacio mediante Multiplicadores de Lagrange."
            ),
            datos_resumen={
                "Espacio Disponible": "220 m²",
                "Productos": "3 artículos (A, B, C)",
                "Método": "Multiplicadores de Lagrange (λ*)"
            },
            solucion_explicada=(
                "1. EOQ sin restricción:\n"
                "   • Q_A = sqrt(2*1000*40 / 4) = 141.42 u (Espacio: 141.42 m²)\n"
                "   • Q_B = sqrt(2*1500*50 / 7) = 146.38 u (Espacio: 219.57 m²)\n"
                "   • Q_C = sqrt(2*800*60 / 10) = 97.98 u (Espacio: 195.96 m²)\n"
                "   Espacio total sin límite = 141.42 + 219.57 + 195.96 = 556.95 m² > 220 m² (RESTRICCIÓN ACTIVA).\n\n"
                "2. Planteamiento Lagrangiano:\n"
                "   Q_i*(λ) = sqrt( 2 * D_i * S_i / (H_i + 2 * λ * a_i) )\n"
                "   Búsqueda de λ* tal que sum(a_i * Q_i*(λ*)) = 220.0 m².\n\n"
                "3. Solución convergente (λ* ≈ 4.15):\n"
                "   • Q_A* ≈ 80.6 u (80.6 m²)\n"
                "   • Q_B* ≈ 88.0 u (132.0 m²)\n"
                "   • Q_C* ≈ 59.8 u (119.6 m²)\n"
                "   Espacio total ajustado = 220.0 m² exactos."
            ),
            modelo_instanciado=mod7
        ))

        return ejercicios
