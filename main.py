"""
Punto de Entrada Principal (Main) para la Aplicación de Teoría de Inventarios.
Universidad José Antonio Páez - Facultad de Ingeniería - Escuela de Ingeniería en Computación
Cátedra: Métodos Cuantitativos / Teoría de Colas y Teoría de Inventarios

Paradigma: Programación Orientada a Objetos (POO)
GUI: CustomTkinter / Tkinter + Matplotlib
Exportación: Archivos de texto plano (.txt)
"""

import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def iniciar_interfaz_grafica():
    """Lanza la aplicación de escritorio con GUI moderna en CustomTkinter."""
    from gui.app import AplicacionInventarios
    app = AplicacionInventarios()
    app.mainloop()


def menu_consola_interactivo():
    """
    Modo consola interactivo (CLI) alternativo.
    Permite ejecutar y exportar todos los modelos directamente en terminal.
    """
    from models.eoq import ModeloEOQ
    from models.quiebre_precios import ModeloQuiebrePrecios, TramoDescuento
    from models.restricciones import ModeloRestricciones, ArticuloRestriccion
    from models.probabilistico import ModeloProbabilistico
    from services.exportador import ExportadorServicio
    from services.banco_ejercicios import BancoEjerciciosService
    from parcial.resolver_parcial import resolver_parcial_completo

    print("\n" + "=" * 80)
    print("  UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA")
    print("  CALCULADORA POO EN PYTHON PARA TEORÍA DE INVENTARIOS")
    print("=" * 80)

    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Modelo Clásico EOQ (Wilson)")
        print("2. Modelo con Quiebre de Precios (Descuentos por Volumen)")
        print("3. Modelo de Varios Artículos con Restricciones (Lagrange)")
        print("4. Modelo Probabilístico (Demanda Normal, Z, SS, ROP)")
        print("5. Banco de Ejercicios Guiados de la Cátedra UJAP")
        print("6. Ejecutar Solucionador del Parcial II (Generar TXT en reportes/)")
        print("7. Iniciar Interfaz Gráfica (GUI)")
        print("0. Salir")

        opc = input("\nSeleccione una opción: ").strip()

        if opc == "1":
            print("\n[EOQ CLÁSICO]")
            D = float(input("Demanda Anual (D): "))
            S = float(input("Costo por Pedido (S): "))
            C = float(input("Costo Unitario (C): "))
            i = float(input("Tasa Almacenamiento i en % (ej. 20): ")) / 100.0
            LT = float(input("Lead Time en días (ej. 5): "))
            
            modelo = ModeloEOQ(demanda_anual=D, costo_pedido=S, costo_unitario=C, tasa_almacenamiento=i, lead_time_dias=LT)
            modelo.calcular()
            print("\n" + modelo.generar_reporte_txt())
            
            guardar = input("\n¿Desea exportar a archivo .txt? (s/n): ").strip().lower()
            if guardar == "s":
                fname = input("Nombre del archivo (ej. reporte_eoq.txt): ").strip() or "reporte_eoq.txt"
                ruta = ExportadorServicio.exportar_modelo_a_txt(modelo, fname)
                print(f"Reporte exportado exitosamente en: {ruta}")

        elif opc == "2":
            print("\n[QUIEBRE DE PRECIOS]")
            D = float(input("Demanda Anual (D): "))
            S = float(input("Costo por Pedido (S): "))
            i = float(input("Tasa Almacenamiento i en % (ej. 20): ")) / 100.0
            num_tramos = int(input("Número de tramos de descuento: "))
            
            tramos = []
            for t_idx in range(1, num_tramos + 1):
                print(f"\n--- Tramo {t_idx} ---")
                q_min = float(input(f"Q Mínimo para tramo {t_idx}: "))
                q_max_str = input(f"Q Máximo para tramo {t_idx} (escriba 'inf' si no tiene límite): ").strip().lower()
                q_max = float('inf') if q_max_str in ['inf', 'infinito', ''] else float(q_max_str)
                precio = float(input(f"Precio Unitario para tramo {t_idx}: "))
                tramos.append(TramoDescuento(q_min=q_min, q_max=q_max, precio_unitario=precio))
            
            modelo = ModeloQuiebrePrecios(demanda_anual=D, costo_pedido=S, tasa_almacenamiento=i, tramos=tramos)
            modelo.calcular()
            print("\n" + modelo.generar_reporte_txt())

            guardar = input("\n¿Desea exportar a archivo .txt? (s/n): ").strip().lower()
            if guardar == "s":
                fname = input("Nombre del archivo (ej. reporte_quiebre.txt): ").strip() or "reporte_quiebre.txt"
                ruta = ExportadorServicio.exportar_modelo_a_txt(modelo, fname)
                print(f"Reporte exportado exitosamente en: {ruta}")

        elif opc == "3":
            print("\n[VARIOS ARTÍCULOS CON RESTRICCIONES]")
            tipo = input("Tipo de restricción ('espacio' o 'presupuesto'): ").strip().lower() or "espacio"
            limite = float(input("Límite máximo disponible del recurso: "))
            num_art = int(input("Número de artículos a gestionar: "))
            
            articulos = []
            for a_idx in range(1, num_art + 1):
                print(f"\n--- Artículo {a_idx} ---")
                nom = input("Nombre del artículo: ").strip() or f"Artículo {a_idx}"
                D_i = float(input("Demanda Anual (D): "))
                S_i = float(input("Costo de Pedido (S): "))
                C_i = float(input("Costo Unitario (C): "))
                H_i = float(input("Costo de Almacenamiento Unitario (H): "))
                esp_i = float(input("Espacio/Factor unitario (a): "))
                articulos.append(ArticuloRestriccion(nombre=nom, demanda_anual=D_i, costo_pedido=S_i, costo_unitario=C_i, costo_almacenamiento=H_i, espacio_unitario=esp_i))
            
            modelo = ModeloRestricciones(limite_recurso=limite, tipo_restriccion=tipo, articulos=articulos)
            modelo.calcular()
            print("\n" + modelo.generar_reporte_txt())

            guardar = input("\n¿Desea exportar a archivo .txt? (s/n): ").strip().lower()
            if guardar == "s":
                fname = input("Nombre del archivo (ej. reporte_restricciones.txt): ").strip() or "reporte_restricciones.txt"
                ruta = ExportadorServicio.exportar_modelo_a_txt(modelo, fname)
                print(f"Reporte exportado exitosamente en: {ruta}")

        elif opc == "4":
            print("\n[MODELO PROBABILÍSTICO]")
            d_media = float(input("Demanda Promedio Diaria (d): "))
            sigma_d = float(input("Desviación Estándar Diaria (σ): "))
            LT = float(input("Tiempo de Entrega (Lead Time en días): "))
            SL = float(input("Nivel de Servicio Deseado en % (ej. 95): "))
            S = float(input("Costo de Pedido (S): "))
            C = float(input("Costo Unitario (C): "))
            i = float(input("Tasa Almacenamiento i en % (ej. 20): ")) / 100.0
            
            modelo = ModeloProbabilistico(
                demanda_promedio_diaria=d_media,
                desviacion_diaria=sigma_d,
                lead_time_dias=LT,
                nivel_servicio_pct=SL,
                costo_pedido=S,
                costo_unitario=C,
                tasa_almacenamiento=i
            )
            modelo.calcular()
            print("\n" + modelo.generar_reporte_txt())

            guardar = input("\n¿Desea exportar a archivo .txt? (s/n): ").strip().lower()
            if guardar == "s":
                fname = input("Nombre del archivo (ej. reporte_probabilistico.txt): ").strip() or "reporte_probabilistico.txt"
                ruta = ExportadorServicio.exportar_modelo_a_txt(modelo, fname)
                print(f"Reporte exportado exitosamente en: {ruta}")

        elif opc == "5":
            print("\n[BANCO DE EJERCICIOS GUIADOS UJAP]")
            ejercicios = BancoEjerciciosService.obtener_todos_los_ejercicios()
            for idx, ej in enumerate(ejercicios, start=1):
                print(f"{idx}. {ej.titulo} ({ej.fuente})")
            
            sel = int(input(f"\nSeleccione un ejercicio (1-{len(ejercicios)}): "))
            if 1 <= sel <= len(ejercicios):
                ej_sel = ejercicios[sel - 1]
                print("\n" + "=" * 78)
                print(f"TÍTULO: {ej_sel.titulo}")
                print(f"FUENTE: {ej_sel.fuente}")
                print("=" * 78)
                print("\nENUNCIADO:\n" + ej_sel.enunciado)
                print("\nSOLUCIÓN PASO A PASO:\n" + ej_sel.solucion_explicada)
                print("\nREPORTE FORMAL:\n" + ej_sel.modelo_instanciado.generar_reporte_txt())

        elif opc == "6":
            resolver_parcial_completo()

        elif opc == "7":
            print("Iniciando Interfaz Gráfica (GUI)...")
            iniciar_interfaz_grafica()
            break

        elif opc == "0":
            print("\n¡Gracias por usar el Sistema de Teoría de Inventarios!")
            break
        else:
            print("Opción inválida. Intente de nuevo.")


if __name__ == "__main__":
    # Si se pasa el argumento --cli, se abre el menú de consola
    if "--cli" in sys.argv or "-c" in sys.argv:
        menu_consola_interactivo()
    else:
        try:
            iniciar_interfaz_grafica()
        except Exception as e:
            print(f"Error al iniciar la GUI: {e}")
            print("Iniciando modo consola interactivo...")
            menu_consola_interactivo()
