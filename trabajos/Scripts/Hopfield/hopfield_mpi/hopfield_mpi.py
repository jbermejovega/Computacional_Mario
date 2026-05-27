#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelo de Hopfield con MPI para ejecutar en JOEL.

Objetivo:
- Repartir simulaciones independientes entre procesos MPI.
- Medir el tiempo total de ejecución.
- Devolver una salida sencilla para copiar al informe/Colab.

Ejecución típica:
    mpirun -np 4 python hopfield_mpi.py

o:
    mpiexec -n 4 python hopfield_mpi.py
"""

import time
import numpy as np
from mpi4py import MPI


# ============================================================# PARÁMETROS DEL PROBLEMA
# ============================================================

N = 80                  # Número de neuronas
alpha = 0.10             # Capacidad relativa: p/N
n_pasos = 1000           # Pasos Monte Carlo por simulación
n_repeticiones = 5      # Repeticiones independientes por temperatura

temperaturas = np.linspace(0.2, 3.0, 20)

semilla_base = 12345


# ============================================================
# FUNCIONES DEL MODELO DE HOPFIELD
# ============================================================

def generar_patrones(N, p, rng):
    """
    Genera p patrones aleatorios de longitud N con valores ±1.
    """
    return rng.choice([-1, 1], size=(p, N))


def construir_pesos(patrones):
    """
    Construye la matriz de pesos de Hopfield:

        J_ij = (1/N) sum_mu xi_i^mu xi_j^mu

    con J_ii = 0.
    """
    p, N = patrones.shape
    J = patrones.T @ patrones
    J = J / N
    np.fill_diagonal(J, 0.0)
    return J


def solapamiento(estado, patron):
    """
    Calcula el solapamiento entre el estado actual y un patrón:

        m = (1/N) sum_i xi_i s_i
    """
    return np.sum(estado * patron) / len(estado)


def paso_monte_carlo(estado, J, beta, rng):
    """
    Realiza un barrido Monte Carlo:
    se intentan actualizar N neuronas elegidas al azar.
    """
    N = len(estado)

    for _ in range(N):
        i = rng.integers(0, N)

        campo_local = np.dot(J[i, :], estado)
        delta_E = 2.0 * estado[i] * campo_local

        if delta_E <= 0.0:
            estado[i] *= -1
        else:
            if rng.random() < np.exp(-beta * delta_E):
                estado[i] *= -1

    return estado


def simular_una_vez(T, N, alpha, n_pasos, semilla):
    """
    Ejecuta una simulación de Hopfield para una temperatura T.

    Devuelve el solapamiento final absoluto con el primer patrón.
    """
    rng = np.random.default_rng(semilla)

    p = max(1, int(alpha * N))

    patrones = generar_patrones(N, p, rng)
    J = construir_pesos(patrones)

    # Estado inicial: primer patrón con algo de ruido
    estado = patrones[0].copy()

    fraccion_ruido = 0.10
    n_flip = int(fraccion_ruido * N)
    indices = rng.choice(N, size=n_flip, replace=False)
    estado[indices] *= -1

    beta = 1.0 / T

    for _ in range(n_pasos):
        estado = paso_monte_carlo(estado, J, beta, rng)

    m_final = abs(solapamiento(estado, patrones[0]))

    return m_final


def simular_temperatura(T, N, alpha, n_pasos, n_repeticiones, semilla_base):
    """
    Ejecuta varias repeticiones independientes para una temperatura T.
    Devuelve media y desviación típica del solapamiento final.
    """
    resultados = []

    for r in range(n_repeticiones):
        semilla = semilla_base + int(100000 * T) + r
        m = simular_una_vez(T, N, alpha, n_pasos, semilla)
        resultados.append(m)

    resultados = np.array(resultados)

    media = np.mean(resultados)
    desviacion = np.std(resultados)

    return media, desviacion


# ============================================================
# PROGRAMA PRINCIPAL MPI
# ============================================================

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Sincronizamos antes de empezar a medir
    comm.Barrier()
    t0 = time.perf_counter()

    # Repartimos temperaturas entre procesos
    temperaturas_locales = temperaturas[rank::size]

    resultados_locales = []

    for T in temperaturas_locales:
        media, desviacion = simular_temperatura(
            T=T,
            N=N,
            alpha=alpha,
            n_pasos=n_pasos,
            n_repeticiones=n_repeticiones,
            semilla_base=semilla_base
        )

        resultados_locales.append((T, media, desviacion))

    # Reunimos resultados en el proceso 0
    resultados_todos = comm.gather(resultados_locales, root=0)

    comm.Barrier()
    t1 = time.perf_counter()

    if rank == 0:
        tiempo_total = t1 - t0

        resultados_finales = []

        for bloque in resultados_todos:
            resultados_finales.extend(bloque)

        resultados_finales.sort(key=lambda x: x[0])

        print()
        print("=================================================")
        print("RESULTADO HOPFIELD MPI")
        print("=================================================")
        print(f"N = {N}")
        print(f"alpha = {alpha}")
        print(f"patrones p = {max(1, int(alpha * N))}")
        print(f"pasos Monte Carlo = {n_pasos}")
        print(f"repeticiones por temperatura = {n_repeticiones}")
        print(f"numero de temperaturas = {len(temperaturas)}")
        print(f"procesos MPI = {size}")
        print("-------------------------------------------------")
        print(f"TIEMPO_TOTAL_SEGUNDOS = {tiempo_total:.6f}")
        print("-------------------------------------------------")
        print("T, m_media, m_desviacion")

        for T, media, desviacion in resultados_finales:
            print(f"{T:.6f}, {media:.6f}, {desviacion:.6f}")

        print("-------------------------------------------------")
        print("LINEA_RESUMEN_COPIAR_EN_COLAB")
        print(f"{size}, {tiempo_total:.6f}")
        print("=================================================")
        print()


if __name__ == "__main__":
    main()
