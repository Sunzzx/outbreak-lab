# Outbreak Lab

A dependency-free, reproducible stochastic SIR sandbox for exploring epidemic trajectories and comparing contact-reduction policies. It is an educational/research simulator, not a clinical or public-health forecasting product.

[![CI](https://github.com/Sunzzx/outbreak-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Sunzzx/outbreak-lab/actions)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-pink)](https://github.com/sponsors/Sunzzx)

## Why it matters

Rapid scenario exploration can help students and analysts understand how contact patterns affect epidemic peaks and cumulative attack rates. This small transparent model is useful for teaching, sensitivity experiments, and prototyping policy questions before investing in a calibrated model. It uses synthetic populations and makes no claim to represent any real pathogen or community.

## Model

Each individual occupies one of three states, susceptible $S$, infectious $I$, or recovered $R$. At day $t$, each infectious individual receives one effective contact opportunity with probability $c$ (the intervention's contact scale). The selected susceptible target is infected with probability $\beta$. New infections begin transmitting on the next day. Infectious individuals recover independently with probability $\gamma=1/D$, giving geometric mean infectious duration $D$.

For a susceptible individual $j$ and $I_t$ infectious people, the mean-field approximation to the daily infection hazard is

$$\lambda_t = 1 - (1-c\beta/N)^{I_t}, \qquad E[\Delta I_t] \approx S_t\lambda_t.$$

The stochastic simulator samples finite-population contacts directly rather than substituting this expectation. State conservation is exact:

$$S_t+I_t+R_t=N, \qquad C_{t+1}=C_t+\Delta I_t.$$

Effective reproduction estimate is reported as $\widehat R_t=\Delta I_t/I_{t-1}$ when $I_{t-1}>0$; it is a noisy descriptive statistic, not an estimator adjusted for generation intervals.

### Complexity

The reference implementation scans population state and infectious people each day. Runtime is $O(TN + \sum_t I_t)$ (worst case $O(TN)$), and memory is $O(N+T)$ for population states and the returned trajectory. Intervention counterfactuals run two simulations: same asymptotic order, roughly 2x the cost.

### Data flow

```text
seed + parameters -> seeded PRNG -> contact sampling -> S/I/R transitions
                                          |                     |
                                          +-> daily metrics <---+
                                                  |
                                  baseline vs contact reduction
                                                  |
                                      terminal trajectory plot
```

## Quickstart

```bash
uv run --with pytest pytest -q
uv run python -m outbreak_lab.demo
```

Demo is standard-library only; pytest is only needed for tests. Example run (CPython 3.13, 500 people, 60 days, beta=0.32, seed=42):

```text
6 passed in 0.01s
baseline: attack rate 1.2%; peak 2 on day 6
distancing: attack rate 0.2%; peak 1 on day 0
```

This low-incidence outcome is one stochastic realization, deliberately reproducible by seed; it is not a guaranteed policy effect. The demo plots every third day using Unicode bars. `compare_interventions(population, days=..., beta=..., seed=...)` returns final attack rate and peak size/day for baseline and 50% contact reduction.

## API

```python
from outbreak_lab import Person, simulate, compare_interventions
trajectory = simulate([Person(i) for i in range(500)], days=60,
                      beta=0.32, seed=42)
scenarios = compare_interventions(500, days=60, beta=0.32, seed=42)
```

`simulate` exposes `initial_infected`, `infectious_period`, and `contact_scale`. Results are immutable `Day` records. Reusing a seed and inputs reproduces the same run.

## License & support

MIT. For enterprise use, model calibration, or a commercial license, contact [Ayush Kandwal](mailto:ayushkandwal2007@gmail.com). GitHub Sponsors: [github.com/sponsors/Sunzzx](https://github.com/sponsors/Sunzzx). No payment checkout or paid service is implied by this repository.
