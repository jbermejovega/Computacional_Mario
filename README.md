# Física Computacional

**Autor:** Mario Hernández Cuéllar
**Asignatura:** Física Computacional
**Curso:** 2025/2026
**Universidad:** Universidad de Granada

---

## Descripción general

Este repositorio contiene el trabajo desarrollado a lo largo de la asignatura **Física Computacional**. Su objetivo principal es reunir de forma organizada los códigos, notebooks, simulaciones, resultados y materiales generados durante el curso, utilizando herramientas de programación científica para resolver y analizar distintos problemas físicos.

Los contenidos del repositorio combinan programación en Python, simulación numérica, representación gráfica de resultados y redacción de informes o notebooks explicativos. El trabajo se ha realizado principalmente con **Visual Studio Code**, **Python 3.14.3** y **Google Colab** para la visualización y ejecución de notebooks de Jupyter.

Además, los códigos e informes del los contenidos obligatorios se han realizado en conjunto con el grupo "aretes". Cuyos miembros son: Carmen Bonal de Manuel, Pau Gomila Tarongí, Claudia González Arnaiz, Mario Hernández Cuéllar, María Dolores Navarro Ortiz y Clara Piñero García.

---

## Índice de contenidos del repositorio

El repositorio se organiza en dos bloques principales: `contenidos`, donde se incluyen materiales generales de la asignatura, herramientas y scripts de apoyo, y `trabajos`, donde se recogen los proyectos y notebooks desarrollados durante el curso.

```text
Computacional_Mario/
│
├── README.md
│
├── contenidos/
│
└── trabajos/
    ├── laboratorio/
    │   ├── COMPU_SISTEMA_SOLAR.ipynb
    │   ├── ISING.ipynb
    │   ├── Jup_voluntario_hopfield_mariohc.ipynb
    │   └── Jup_voluntario_shrodinger_mariohc.ipynb
    │
    └── Scripts/
        ├── Sistema solar/
        │
        ├── Ising/
        │
        ├── Hopfield/
        │
        └── VolShro/
```

De forma general, el repositorio contiene:

* **Scripts de Python (`.py`)** para simulación, análisis de datos y generación de animaciones.
* **Notebooks de Jupyter (`.ipynb`)** utilizados como informes interactivos y para visualizar resultados en Google Colab.
* **Archivos de datos (`.dat`)** generados por las simulaciones.
* **Figuras, animaciones y vídeos (`.png`, `.gif`, `.mp4`)** empleados para representar la evolución de los sistemas físicos estudiados.
* **Material de apoyo** relacionado con herramientas de programación, Python, C/C++, depuración, máquina virtual y números aleatorios.

---

## Herramientas utilizadas

Para el desarrollo del repositorio se han utilizado principalmente las siguientes herramientas:

* **Python 3.14.3** como lenguaje principal de programación.
* **Visual Studio Code** como entorno de desarrollo.
* **Google Colab** para ejecutar y visualizar notebooks de Jupyter.
* **Git y GitHub** para el control de versiones y almacenamiento del trabajo.

Las librerías de Python utilizadas dependen de cada práctica, pero de forma general se han empleado herramientas habituales de cálculo científico, como:

```text
numpy
matplotlib
pandas
scipy
numba
```

> Algunas prácticas pueden requerir solo una parte de estas librerías.

---

## Descripción de algunos contenidos trabajados

A lo largo del curso se han abordado diferentes problemas de física mediante métodos computacionales. Entre los contenidos trabajados se incluyen:

### Simulación del Sistema Solar

Se han utilizado métodos numéricos para simular el movimiento orbital de varios planetas alrededor del Sol. El objetivo principal ha sido estudiar la evolución temporal de las posiciones y velocidades, comparar los periodos orbitales simulados con los valores esperados y analizar los errores relativos obtenidos.

### Modelo de Ising

Se ha trabajado con el modelo de Ising como ejemplo de sistema de espines en mecánica estadística. Mediante simulaciones de Monte Carlo, se ha estudiado la evolución del sistema para distintas temperaturas, observando la aparición de regiones ordenadas, estados de equilibrio y dependencia del comportamiento colectivo con la temperatura.

### Modelo de Hopfield

Se ha implementado una red de Hopfield como modelo de memoria asociativa. El trabajo ha consistido en almacenar patrones, analizar la recuperación de dichos patrones a partir de estados iniciales perturbados y estudiar cómo afecta el número de patrones almacenados a la capacidad de recuperación de la red.

### Ecuación de Schrödinger unidimensional

Se han realizado simulaciones de la evolución temporal de paquetes de onda en una dimensión. En particular, se ha estudiado la interacción de un paquete de onda con una barrera de potencial cuadrada, analizando los fenómenos de reflexión, transmisión y dependencia con la energía del paquete incidente.


**Mario Hernández Cuéllar**
Grado en Física
Universidad de Granada
