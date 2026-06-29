# REVISION_PROFUNDA_NOTEBOOKS_MARIO_V1

Marker: `MARIO_FISICA_COMPUTACIONAL_DEEP_NOTEBOOK_REVIEW_V1`
Resource: `MCP_SCIKI_N8N_MARIO_COMPUTACIONAL_REVIEW_RESOURCE_V1`
Upstream repo: `marioehercue/Computacional_Mario`
Contribution repo: `jbermejovega/Computacional_Mario`
Mode: read-only static notebook review. Notebook code is not executed.

## Activation

This document deploys the deep review resource for Mario Hernandez Cuellar's Fisica Computacional notebooks as an invariant workflow:

- MCP resource active: true
- SCIKI map active: true
- N8N workflow exported: true
- GitHub Actions invariant workflow active: true
- Notebook-by-notebook review: true
- Replay-safe: true
- Contents read-only: true
- No notebook code execution during review: true

Canonical validator: `scripts/revision_fisica_computacional/notebook_deep_review.py`.
CI entrypoint: `.github/workflows/fisica-computacional-notebook-review.yml`.

## Notebook Inventory

| Path | Size | Cells | Markdown | Code | Review state |
| --- | ---: | ---: | ---: | ---: | --- |
| `trabajos/laboratorio/COMPU_SISTEMA_SOLAR.ipynb` | 78.13 MB | 41 | 32 | 9 | NEEDS_REVISION |
| `trabajos/laboratorio/ISING.ipynb` | 6.36 MB | 15 | 11 | 4 | NEEDS_REVISION |
| `trabajos/laboratorio/Jup_voluntario_hopfield_mariohc.ipynb` | 0.79 MB | 50 | 26 | 24 | NEEDS_REVISION |
| `trabajos/laboratorio/Jup_voluntario_shrodinger_mariohc.ipynb` | 100.66 MB | 57 | 23 | 34 | NEEDS_REVISION |

## Global Findings

### P0 - Notebooks are too large for stable review and archival

Two notebooks are very large:

- `COMPU_SISTEMA_SOLAR.ipynb`: about 78 MB.
- `Jup_voluntario_shrodinger_mariohc.ipynb`: about 100 MB.

This strongly indicates embedded rich outputs, animations, images, or large rendered payloads. These files become hard to diff, slow to review, and fragile near GitHub file-size limits.

Required action:

- Clear bulky notebook outputs before final archival, or externalize images/videos under a generated artifacts folder.
- Keep lightweight notebooks plus reproducible scripts/data contracts.
- Add a note describing which outputs are regenerated and which are intentionally tracked.

### P1 - Execution state is inconsistent

Detected execution counts:

- `COMPU_SISTEMA_SOLAR.ipynb`: 1 of 9 code cells executed; one saved error output.
- `ISING.ipynb`: 0 of 4 code cells executed.
- `Jup_voluntario_hopfield_mariohc.ipynb`: 1 of 24 code cells executed.
- `Jup_voluntario_shrodinger_mariohc.ipynb`: 34 of 34 code cells executed.

Required action:

- Choose one output policy: clean unexecuted notebooks, or fully executed notebooks from a fresh kernel.
- Remove saved error outputs before final submission.
- Run the notebooks in order after clearing the environment to prove reproducibility.

### P1 - Long code cells mix report and implementation

Detected long code cells:

- Sistema Solar: 3 long code cells, max source length about 120 lines.
- Ising: 3 long code cells, max source length about 123 lines.
- Hopfield: 12 long code cells, max source length about 193 lines.
- Schrodinger: 17 long code cells, max source length about 543 lines.

Required action:

- Move reusable simulation engines into tracked `.py` files under `trabajos/Scripts/`.
- Keep notebooks as report surfaces: parameters, method, execution calls, plots, interpretation, and conclusions.
- Add short validation cells that check output file existence and core invariants.

### P1 - Generated-file contracts are implicit

The notebooks mention generated files such as:

- `magnetizacion_vs_temperatura.dat`
- `magnetizacion_vs_temperatura.png`
- `datos/patrones.dat`
- `datos/estado_inicial.dat`
- `datos/estado_final.dat`
- `datos/energias.dat`
- `datos/aceptaciones.dat`
- `datos/solapamientos.dat`
- `datos/parametros.dat`
- `datos.dat`
- `normas.dat`
- `detectores.dat`
- `nD.dat`
- `coeficiente_transmision.dat`
- `observables.dat`
- `resultado_barrido_N.dat`
- `resultado_barrido_lambda.dat`
- `comparacion_teorica.dat`
- `resultado_observables_con_errores.dat`
- `resultado_multibarrera_K_n.dat`

Required action:

- Add a reproducibility cell to every notebook listing inputs, generated outputs, and expected execution order.
- Do not rely on hidden local state from a previous run.

## Notebook-by-Notebook Review

### `trabajos/laboratorio/COMPU_SISTEMA_SOLAR.ipynb`

Subject: Solar System simulation, orbital periods, energy conservation, animations, and variations such as Jupiter placement and masses.

Strengths:

- Clear section hierarchy: summary, theory, tools, processor model, code, functions, changes.
- Rich explanatory structure around simulator, period calculation, energy conservation, and animation.

Risks:

- Very large notebook, about 78 MB.
- One saved error output is present.
- One empty code cell.
- Three long code cells.
- Only 1 of 9 code cells has an execution count.
- Rich outputs are embedded in several cells.

Actions:

- Clear or externalize rich animation outputs.
- Remove the saved error output and empty code cell.
- Add a reproducibility cell naming simulation parameters and generated visual outputs.
- Split simulator/period/energy/animation code into smaller sections or scripts.

### `trabajos/laboratorio/ISING.ipynb`

Subject: Ising model, Monte Carlo evolution, magnetization versus temperature, critical temperature estimate.

Strengths:

- Has a compact report structure.
- Uses `numba`, `numpy`, `matplotlib`, timing, and generated magnetization data.
- Includes explicit comments about AI-assisted programming and semantic/meta-programming context.

Risks:

- One empty code cell.
- Three long code cells.
- No code cell has an execution count.
- Depends on `magnetizacion_vs_temperatura.dat` and `magnetizacion_vs_temperatura.png`.

Actions:

- Run from a clean kernel or clear all outputs consistently.
- Add parameter table: lattice size, temperature range, number of Monte Carlo steps, thermalization, seed.
- Add finite-size caveat around the critical temperature estimate.
- Split visualization and simulation into separate cells.

### `trabajos/laboratorio/Jup_voluntario_hopfield_mariohc.ipynb`

Subject: Hopfield network as associative memory, pattern storage, Metropolis dynamics, overlap, temperature dependence.

Strengths:

- Strong formal structure with introduction, theory, tools, procedure, results, and conclusions.
- Includes a section on AI tools and execution environment.
- Saves many intermediate outputs, which can support reproducibility if documented.

Risks:

- One empty code cell.
- Twelve long code cells.
- Only 1 of 24 code cells has an execution count.
- Depends on generated `datos/*.dat` files.
- Uses `pandas`, `numba`, parallel settings, and local data directories that should be declared.

Actions:

- Add a setup cell creating/checking `datos/`.
- Move core Hopfield/Metropolis functions into a tracked script.
- Add tests for pattern shape, weight matrix symmetry, energy decrease/acceptance behavior, and overlap range.
- Make execution policy consistent with the report state.

### `trabajos/laboratorio/Jup_voluntario_shrodinger_mariohc.ipynb`

Subject: 1D Schrodinger equation, Cayley method, barrier scattering, detectors, transmission coefficient, observables, parameter sweeps.

Strengths:

- Strong scientific outline and complete execution state: all 34 code cells have execution counts.
- Includes method, observables, transmission coefficient, comparisons, and sweep studies.
- Uses generated data tables to support results.

Risks:

- Extremely large notebook, about 100.66 MB.
- Seventeen long code cells; max source length about 543 lines.
- Rich outputs are embedded in many cells.
- Many generated `.dat` outputs need an explicit contract.
- Filename has `shrodinger`; consider whether this spelling should remain for compatibility or be documented.

Actions:

- Externalize rich outputs and generated videos/figures.
- Move Cayley solver, detector logic, observables, and sweep functions into scripts under `trabajos/Scripts/VolShro/`.
- Add a compact rerun checklist: parameters, generated files, expected norm conservation, and transmission coefficient sanity range.
- Keep one canonical spelling policy for Schrodinger/Schroedinger file and folder names.

## Invariant Review Contract

```yaml
MARIO_FISICA_COMPUTACIONAL_DEEP_NOTEBOOK_REVIEW_V1:
  notebook_by_notebook: true
  mcp_resource_active: true
  sciki_map_active: true
  n8n_workflow_exported: true
  no_notebook_code_execution: true
  read_only_static_review: true
  generated_witness: build/revision_fisica_computacional/notebook-review-witness.json
  human_summary: build/revision_fisica_computacional/notebook-review-witness.md
  blocked_findings_are_reported_not_hidden: true
```

## Next Canonical Fix Set

1. Clear or externalize bulky outputs in Sistema Solar and Schrodinger.
2. Remove saved error outputs and empty code cells.
3. Add generated-file contracts to all four notebooks.
4. Move long simulation engines into `trabajos/Scripts/` modules.
5. Run or clear notebooks consistently from a clean kernel before final submission.
