# 📦 Sistema POO en Python para Teoría de Inventarios
**Universidad José Antonio Páez (UJAP)**  
*Facultad de Ingeniería • Escuela de Ingeniería en Computación*  
*Cátedra: Métodos Cuantitativos / Teoría de Colas y Teoría de Inventarios*

---

## 🎯 Descripción del Proyecto

Aplicación de escritorio desarrollada bajo el paradigma de **Programación Orientada a Objetos (POO)** en **Python**, con interfaz gráfica moderna construida en **CustomTkinter / Tkinter** y generación de gráficos interactivos embebidos con **Matplotlib**.

El sistema procesa y resuelve todos los modelos teóricos y prácticos de la cátedra:
1. **Modelo Determinístico Clásico (EOQ / Modelo de Wilson)**
2. **Modelo con Quiebre de Precios (Descuentos por Volumen)**
3. **Modelo de Varios Artículos con Restricciones (Espacio / Capital con Multiplicadores de Lagrange)**
4. **Modelo Probabilístico (Demanda Normal, Lead Time, Nivel de Servicio $Z$, Stock de Seguridad $SS$, Punto de Reorden $ROP$ y Simulación Monte Carlo)**
5. **Banco de Ejercicios Guiados Oficiales de la Cátedra UJAP**
6. **Compendio Teórico y Formulario Interactivo**
7. **Exportación completa de resultados y cálculos a archivos de texto plano (`.txt`)**

---

## 🏛️ Arquitectura del Software (Paradigma POO)

El código fuente está estructurado siguiendo principios de alta cohesión, bajo acoplamiento y el patrón MVC:

```
inventory-theory/
│
├── main.py                          # Punto de entrada (Lanza GUI o CLI)
├── requirements.txt                 # Dependencias del proyecto
├── run_tests.py                     # Ejecutor de pruebas unitarias
├── README.md                        # Documentación técnica y manual de uso
│
├── models/                          # CAPA DE DOMINIO (Modelos Matemáticos POO)
│   ├── __init__.py
│   ├── base.py                      # Clase abstracta base ModeloInventario
│   ├── eoq.py                       # Clase ModeloEOQ
│   ├── quiebre_precios.py           # Clase ModeloQuiebrePrecios y TramoDescuento
│   ├── restricciones.py             # Clase ModeloRestricciones y ArticuloRestriccion
│   └── probabilistico.py            # Clase ModeloProbabilistico y Simulación Monte Carlo
│
├── parcial/                         # EVALUACIÓN PARCIAL II (Módulos de Resolución)
│   ├── __init__.py
│   ├── ejercicio1_eoq.py            # Resolución Ejercicio 1 (EOQ Clásico)
│   ├── ejercicio2_quiebre.py        # Resolución Ejercicio 2 (Quiebre de Precios)
│   ├── ejercicio3_restricciones.py  # Resolución Ejercicio 3 (Lagrange con unidades mes/día)
│   └── resolver_parcial.py          # Solucionador automatizado y exportador consolidado
│
├── reportes/                        # SALIDAS Y REPORTES EN TEXTO PLANO (.txt)
│   ├── .gitkeep
│   ├── salida_ejercicio1.txt
│   ├── salida_ejercicio2.txt
│   ├── salida_ejercicio3.txt
│   └── salida_parcial_completo.txt
│
├── gui/                             # CAPA DE PRESENTACIÓN (Tkinter / CustomTkinter)
│   ├── __init__.py
│   ├── app.py                       # Ventana Principal (AplicacionInventarios)
│   ├── theme.py                     # Sistema de diseño, temas y tokens de color
│   ├── components/                  # Componentes reutilizables
│   │   ├── plot_frame.py            # Canvas para figuras Matplotlib
│   │   ├── metric_card.py           # Tarjetas visuales de métricas KPI
│   │   └── table_editor.py          # Tabla dinámica interactiva para tramos/productos
│   └── views/                       # Vistas de cada modelo
│       ├── vista_eoq.py             # Vista EOQ Clásico
│       ├── vista_quiebre.py         # Vista Quiebre de Precios
│       ├── vista_restricciones.py   # Vista Multi-Artículos con Lagrange
│       ├── vista_probabilistico.py  # Vista Probabilística con Monte Carlo
│       ├── vista_ejercicios.py      # Vista del Banco de Problemas UJAP
│       └── vista_teoria.py          # Vista de Formulario Oficial
│
├── services/                        # CAPA DE SERVICIOS
│   ├── __init__.py
│   ├── exportador.py                # Servicio de generación y guardado de archivos .txt
│   └── banco_ejercicios.py          # Repositorio de problemas resueltos de la guía
│
└── tests/                           # PRUEBAS UNITARIAS
    ├── __init__.py
    └── test_modelos.py              # Suite de pruebas unitarias automatizadas
```

---

## 🚀 Instalación y Ejecución

### 1. Clonar o descargar el repositorio e instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la Aplicación en Modo Gráfico (GUI)
```bash
python main.py
```

### 3. Ejecutar en Modo Consola Interactivo (CLI)
```bash
python main.py --cli
```

### 4. Ejecutar el Solucionador Modular del Parcial II (Generar TXT en reportes/)
```bash
python -m parcial.resolver_parcial
```

### 5. Ejecutar la Suite de Pruebas Unitarias
```bash
python run_tests.py
```

---

## 📊 Modelos Matemáticos Implementados

### 1. Modelo EOQ Clásico
- **Cantidad Económica de Pedido**: $Q^* = \sqrt{\frac{2 D S}{H}}$
- **Demanda Diaria**: $d = \frac{D}{Días}$
- **Punto de Reorden**: $ROP = d \times LT$
- **Frecuencia Anual**: $N = \frac{D}{Q^*}$
- **Costo Total Anual**: $CT = D \cdot C + \frac{D}{Q^*} S + \frac{Q^*}{2} H$
- **Gráficos**: Curvas de Costo Anual vs $Q$ + Simulación Diente de Sierra $Q(t)$.

### 2. Modelo con Quiebre de Precios
- Algoritmo de evaluación por tramos $[Q_{min, k}, Q_{max, k}]$.
- Verificación de factibilidad y ajuste a puntos de quiebre.
- Selección del mínimo global de costo total anual y cálculo de ahorro.
- **Gráficos**: Comparativa de curvas de costo por tramo con resaltado del óptimo.

### 3. Modelo Multi-Artículo con Restricciones (Lagrange)
- Optimización con restricción de espacio $\sum a_i Q_i \le A$ o presupuesto $\sum C_i Q_i \le B$.
- Formulación analítica: $Q_i^*(\lambda) = \sqrt{\frac{2 D_i S_i}{H_i + 2 \lambda w_i}}$
- Búsqueda numérica de alta precisión del multiplicador de Lagrange $\lambda^*$.
- **Gráficos**: Comparación de lotes y asignación de capacidad.

### 4. Modelo Probabilístico
- Parámetros en Lead Time: $\mu_{LT} = \bar{d} \cdot LT$, $\sigma_{LT} = \sigma_d \sqrt{LT}$.
- Factor de Seguridad Normal: $Z = \Phi^{-1}(SL)$.
- **Stock de Seguridad**: $SS = Z \cdot \sigma_{LT}$
- **Punto de Reorden**: $ROP = \mu_{LT} + SS$
- **Gráficos**: Campana de Gauss con área sombreada de nivel de servicio $(1-\alpha)$ y riesgo de quiebre ($\alpha$) + Simulación temporal Monte Carlo estocástica día a día.

---

## 📥 Exportación a Texto Plano (.txt)

Cumpliendo con la pauta de evaluación de la cátedra:
> *"Finalmente, el programa deberá incluir una funcionalidad que permite exportar todos los resultados y cálculos generados a un archivo de texto plano (.txt) para su posterior análisis."*

La aplicación permite:
- Exportar reportes individuales de cada modelo desde cada vista mediante el botón **"📥 Exportar Reporte (.txt)"**.
- Exportar cualquier ejercicio del banco de problemas resueltos.
- Exportar un informe consolidado con todos los modelos resueltos desde el botón **"📑 Exportar Todo a (.txt)"** en la barra lateral.

---

## 👥 Créditos Académicos
- **Institución**: Universidad José Antonio Páez (UJAP)
- **Facultad**: Facultad de Ingeniería
- **Escuela**: Escuela de Ingeniería en Computación
- **Asignatura**: Métodos Cuantitativos / Teoría de Inventarios
