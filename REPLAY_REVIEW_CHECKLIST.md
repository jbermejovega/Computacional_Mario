# Replay Review Checklist

## General

- [ ] Parameters logged
- [ ] Random seeds logged
- [ ] Units documented
- [ ] Runtime metadata preserved
- [ ] Reproducible notebook execution

## Schrödinger

- [ ] Probability norm conservation checked
- [ ] Unitarity discussed
- [ ] Potential barrier visualized clearly
- [ ] Reflection/transmission regimes distinguished

## Runge-Kutta / NBody

- [ ] Conserved quantity monitored
- [ ] dt convergence checked
- [ ] Coordinate system validated
- [ ] Close approach singularities handled

## Ising / Monte Carlo

- [ ] Magnetization plotted
- [ ] Susceptibility computed
- [ ] Thermalization discussed
- [ ] MPI/OpenMP scaling benchmarked
- [ ] Independent seeds per sampler

## HPC

- [ ] Serial vs parallel comparison
- [ ] Benchmark tables included
- [ ] Core/thread count documented
- [ ] Hardware documented

## PACAPDG replay

- [ ] notebook != canonical kernel
- [ ] same_content != same_provenance
- [ ] replay trace preserved
