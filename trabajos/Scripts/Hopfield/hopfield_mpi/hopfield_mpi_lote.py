#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import time
from mpi4py import MPI


# ============================================================
# PARÁMETROS DEL CÓDIGO DE COLAB
# ============================================================

N = 40
P = 2
prob_activa = 0.25
T = 1e-4
num_pasos_mc = 50
fraccion_ruido = 0.2

M = N * N

# Número total de simulaciones independientes del lote.
# Tiene que ser el mismo cuando luego lo comparemos en Colab.
num_simulaciones = 16

seed_base = 123


# ============================================================
# FUNCIONES DEL MODELO DE HOPFIELD
# ============================================================

def crear_rng(seed=None):
    return np.random.default_rng(seed)


def crear_patron_aleatorio(N, prob_activa=0.3, rng=None):
    if rng is None:
        rng = crear_rng()

    patron = rng.random((N, N)) < prob_activa
    return patron.astype(np.float64)


def deformar_patron(patron, fraccion_ruido=0.2, rng=None):
    if rng is None:
        rng = crear_rng()

    patron_deformado = patron.copy()
    N = patron.shape[0]

    numero_neuronas = N * N
    numero_cambios = int(fraccion_ruido * numero_neuronas)

    indices = rng.choice(numero_neuronas, size=numero_cambios, replace=False)

    patron_plano = patron_deformado.ravel()
    patron_plano[indices] = 1.0 - patron_plano[indices]

    return patron_deformado


def calcular_bias(patrones):
    return np.mean(patrones)


def calcular_pesos(patrones):
    patrones = np.array(patrones, dtype=np.float64)

    P, N, _ = patrones.shape
    M = N * N

    a = calcular_bias(patrones)

    if a == 0 or a == 1:
        raise ValueError("El bias no puede ser 0 ni 1.")

    patrones_planos = patrones.reshape(P, M)
    patrones_centrados = patrones_planos - a

    pesos = (patrones_centrados.T @ patrones_centrados) / (a * (1 - a) * M)

    np.fill_diagonal(pesos, 0.0)

    return pesos.astype(np.float64), a


def calcular_umbrales(pesos):
    return (0.5 * np.sum(pesos, axis=1)).astype(np.float64)


def calcular_energia_numpy(estado_plano, pesos, umbrales):
    """
    Misma energía del código original, pero usando operaciones vectorizadas de NumPy.
    """
    energia_interaccion = -0.5 * estado_plano @ pesos @ estado_plano
    energia_umbral = np.sum(umbrales * estado_plano)

    return energia_interaccion + energia_umbral


def evolucionar_numpy(estado_inicial, pesos, umbrales, T, num_pasos_mc,
                      indices_random, numeros_random):
    """
    Misma dinámica Monte Carlo que en el código de Colab, pero usando np.dot
    para el campo local. No usa Numba.
    """
    estado = estado_inicial.copy()
    estado_plano = estado.ravel()

    M = estado_plano.size

    energias = np.zeros(num_pasos_mc + 1)
    aceptaciones = np.zeros(num_pasos_mc + 1)

    energias[0] = calcular_energia_numpy(estado_plano, pesos, umbrales)
    aceptaciones[0] = 0.0

    contador_random = 0

    for paso in range(1, num_pasos_mc + 1):

        aceptados = 0

        for _ in range(M):

            indice = indices_random[contador_random]
            numero_aleatorio = numeros_random[contador_random]
            contador_random += 1

            valor_actual = estado_plano[indice]
            valor_nuevo = 1.0 - valor_actual

            delta_s = valor_nuevo - valor_actual

            campo = np.dot(pesos[indice, :], estado_plano)

            delta_H = -delta_s * campo + umbrales[indice] * delta_s

            if delta_H <= 0:
                aceptar = True
            else:
                probabilidad = np.exp(-delta_H / T)
                aceptar = numero_aleatorio < probabilidad

            if aceptar:
                estado_plano[indice] = valor_nuevo
                aceptados += 1

        energias[paso] = calcular_energia_numpy(estado_plano, pesos, umbrales)
        aceptaciones[paso] = aceptados / M

    return estado, energias, aceptaciones


def ejecutar_simulacion_independiente(id_simulacion):
    """
    Ejecuta una simulación completa independiente.

    Cada simulación usa una semilla distinta, pero mantiene:
    N, P, prob_activa, T, num_pasos_mc y fraccion_ruido.
    """
    seed = seed_base + id_simulacion
    rng = crear_rng(seed=seed)

    patrones = np.array([
        crear_patron_aleatorio(N, prob_activa, rng)
        for _ in range(P)
    ], dtype=np.float64)

    patron_objetivo = patrones[0]

    pesos, a = calcular_pesos(patrones)
    umbrales = calcular_umbrales(pesos)

    estado_inicial = deformar_patron(
        patron_objetivo,
        fraccion_ruido=fraccion_ruido,
        rng=rng
    ).astype(np.float64)

    total_intentos = num_pasos_mc * M

    indices_random = rng.integers(0, M, size=total_intentos).astype(np.int64)
    numeros_random = rng.random(total_intentos).astype(np.float64)

    estado_final, energias, aceptaciones = evolucionar_numpy(
        estado_inicial,
        pesos,
        umbrales,
        T,
        num_pasos_mc,
        indices_random,
        numeros_random
    )

    energia_final = energias[-1]
    aceptacion_final = aceptaciones[-1]
    suma_estado_final = np.sum(estado_final)

    return {
        "id": id_simulacion,
        "seed": seed,
        "energia_final": energia_final,
        "aceptacion_final": aceptacion_final,
        "suma_estado_final": suma_estado_final
    }


# ============================================================
# PROGRAMA PRINCIPAL MPI
# ============================================================

def main():

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Lista de simulaciones independientes
    ids_simulaciones = list(range(num_simulaciones))

    # Reparto simple: cada proceso hace ids rank, rank+size, rank+2size...
    ids_locales = ids_simulaciones[rank::size]

    comm.Barrier()
    t0 = time.perf_counter()

    resultados_locales = []

    for id_sim in ids_locales:
        resultado = ejecutar_simulacion_independiente(id_sim)
        resultados_locales.append(resultado)

    resultados_todos = comm.gather(resultados_locales, root=0)

    comm.Barrier()
    t1 = time.perf_counter()

    tiempo_total = t1 - t0

    if rank == 0:

        resultados_finales = []

        for bloque in resultados_todos:
            resultados_finales.extend(bloque)

        resultados_finales.sort(key=lambda x: x["id"])

        energias = np.array([r["energia_final"] for r in resultados_finales])
        aceptaciones = np.array([r["aceptacion_final"] for r in resultados_finales])
        sumas_estado = np.array([r["suma_estado_final"] for r in resultados_finales])

        print()
        print("=================================================")
        print("RESULTADO HOPFIELD MPI POR LOTES")
        print("=================================================")
        print(f"N = {N}")
        print(f"P = {P}")
        print(f"M = {M}")
        print(f"T = {T}")
        print(f"Pasos Monte Carlo = {num_pasos_mc}")
        print(f"Fraccion de ruido = {fraccion_ruido}")
        print(f"Numero total de simulaciones = {num_simulaciones}")
        print(f"Procesos MPI = {size}")
        print("-------------------------------------------------")
        print(f"TIEMPO_TOTAL_SEGUNDOS = {tiempo_total:.6f}")
        print(f"ENERGIA_MEDIA_FINAL = {np.mean(energias):.12f}")
        print(f"ENERGIA_STD_FINAL = {np.std(energias):.12f}")
        print(f"ACEPTACION_MEDIA_FINAL = {np.mean(aceptaciones):.12f}")
        print(f"SUMA_ESTADO_MEDIA_FINAL = {np.mean(sumas_estado):.12f}")
        print("-------------------------------------------------")
        print("LINEA_RESUMEN_COPIAR_EN_COLAB")
        print(
            f"{size}, {tiempo_total:.6f}, "
            f"{np.mean(energias):.12f}, {np.std(energias):.12f}, "
            f"{np.mean(aceptaciones):.12f}, {np.mean(sumas_estado):.12f}"
        )
        print("-------------------------------------------------")
        print("Resultados individuales:")
        print("id, seed, energia_final, aceptacion_final, suma_estado_final")

        for r in resultados_finales:
            print(
                f"{r['id']}, {r['seed']}, "
                f"{r['energia_final']:.12f}, "
                f"{r['aceptacion_final']:.12f}, "
                f"{r['suma_estado_final']:.12f}"
            )

        print("=================================================")
        print()


if __name__ == "__main__":
    main()
