#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import time
from mpi4py import MPI


# ============================================================
# FUNCIONES ORIGINALES DEL CÓDIGO DE COLAB
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


# ============================================================
# FUNCIONES MPI
# ============================================================

def intervalo_local(M, rank, size):
    """
    Divide M elementos entre size procesos.
    Devuelve el intervalo [inicio, fin) correspondiente al proceso rank.
    """
    base = M // size
    resto = M % size

    if rank < resto:
        inicio = rank * (base + 1)
        fin = inicio + base + 1
    else:
        inicio = resto * (base + 1) + (rank - resto) * base
        fin = inicio + base

    return inicio, fin


def calcular_energia_mpi(estado_plano, pesos, umbrales, comm, rank, size):
    """
    Calcula la misma energía que la función calcular_energia_python_bucles,
    pero repartiendo las filas de la matriz de pesos entre procesos MPI.
    """
    M = estado_plano.size
    i0, i1 = intervalo_local(M, rank, size)

    energia_local = 0.0

    for i in range(i0, i1):
        suma_i = 0.0

        for j in range(M):
            suma_i += pesos[i, j] * estado_plano[i] * estado_plano[j]

        energia_local += -0.5 * suma_i + umbrales[i] * estado_plano[i]

    energia_total = comm.allreduce(energia_local, op=MPI.SUM)

    return energia_total


def evolucionar_mpi(estado_inicial, pesos, umbrales, T, num_pasos_mc,
                   indices_random, numeros_random, comm, rank, size):
    """
    Evolución Monte Carlo equivalente a evolucionar_python/evolucionar_numba,
    pero paralelizando con MPI el cálculo del campo local.

    Cada proceso tiene el estado completo, pero calcula una parte del producto
    escalar y luego se suma todo con allreduce.
    """
    estado = estado_inicial.copy()
    estado_plano = estado.ravel()

    M = estado_plano.size

    energias = np.zeros(num_pasos_mc + 1)
    aceptaciones = np.zeros(num_pasos_mc + 1)

    j0, j1 = intervalo_local(M, rank, size)

    energias[0] = calcular_energia_mpi(
        estado_plano, pesos, umbrales, comm, rank, size
    )
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

            # Cada proceso calcula una parte del campo local
            campo_local = 0.0
            for j in range(j0, j1):
                campo_local += pesos[indice, j] * estado_plano[j]

            # Se suma el campo total entre todos los procesos
            campo = comm.allreduce(campo_local, op=MPI.SUM)

            delta_H = -delta_s * campo + umbrales[indice] * delta_s

            if delta_H <= 0:
                aceptar = True
            else:
                probabilidad = np.exp(-delta_H / T)
                aceptar = numero_aleatorio < probabilidad

            if aceptar:
                estado_plano[indice] = valor_nuevo
                aceptados += 1

        energias[paso] = calcular_energia_mpi(
            estado_plano, pesos, umbrales, comm, rank, size
        )
        aceptaciones[paso] = aceptados / M

    return estado, energias, aceptaciones


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # ========================================================
    # PARÁMETROS EXACTOS DEL CÓDIGO DE COLAB
    # ========================================================

    N = 40
    P = 2
    prob_activa = 0.25
    T = 1e-4
    num_pasos_mc = 50
    fraccion_ruido = 0.2
    seed = 123

    M = N * N

    # ========================================================
    # GENERACIÓN DE DATOS EN EL PROCESO 0
    # ========================================================

    if rank == 0:

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

    else:
        patrones = None
        pesos = None
        umbrales = None
        estado_inicial = None
        indices_random = None
        numeros_random = None
        a = None

    # ========================================================
    # ENVÍO DE DATOS A TODOS LOS PROCESOS
    # ========================================================

    patrones = comm.bcast(patrones, root=0)
    pesos = comm.bcast(pesos, root=0)
    umbrales = comm.bcast(umbrales, root=0)
    estado_inicial = comm.bcast(estado_inicial, root=0)
    indices_random = comm.bcast(indices_random, root=0)
    numeros_random = comm.bcast(numeros_random, root=0)
    a = comm.bcast(a, root=0)

    # ========================================================
    # EJECUCIÓN Y MEDIDA DE TIEMPO
    # ========================================================

    comm.Barrier()
    t0 = time.perf_counter()

    estado_mpi, energias_mpi, aceptaciones_mpi = evolucionar_mpi(
        estado_inicial,
        pesos,
        umbrales,
        T,
        num_pasos_mc,
        indices_random,
        numeros_random,
        comm,
        rank,
        size
    )

    comm.Barrier()
    t1 = time.perf_counter()

    tiempo_mpi = t1 - t0

    # ========================================================
    # SALIDA FINAL
    # ========================================================

    if rank == 0:

        energia_final = energias_mpi[-1]
        aceptacion_final = aceptaciones_mpi[-1]
        suma_estado_final = np.sum(estado_mpi)

        print()
        print("=================================================")
        print("RESULTADO HOPFIELD MPI - MISMAS CONDICIONES COLAB")
        print("=================================================")
        print(f"N = {N}")
        print(f"P = {P}")
        print(f"M = {M}")
        print(f"Bias a = {a}")
        print(f"T = {T}")
        print(f"Pasos Monte Carlo = {num_pasos_mc}")
        print(f"Fraccion de ruido = {fraccion_ruido}")
        print(f"Seed = {seed}")
        print(f"Procesos MPI = {size}")
        print("-------------------------------------------------")
        print(f"TIEMPO_TOTAL_SEGUNDOS = {tiempo_mpi:.6f}")
        print(f"ENERGIA_FINAL = {energia_final:.12f}")
        print(f"ACEPTACION_FINAL = {aceptacion_final:.12f}")
        print(f"SUMA_ESTADO_FINAL = {suma_estado_final:.12f}")
        print("-------------------------------------------------")
        print("LINEA_RESUMEN_COPIAR_EN_COLAB")
        print(f"{size}, {tiempo_mpi:.6f}, {energia_final:.12f}, {aceptacion_final:.12f}, {suma_estado_final:.12f}")
        print("=================================================")
        print()


if __name__ == "__main__":
    main()
