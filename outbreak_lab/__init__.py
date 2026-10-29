"""Deterministic-seed stochastic SIR simulator with contact interventions."""
from __future__ import annotations
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Person:
    id: int


@dataclass(frozen=True)
class Day:
    day: int
    susceptible: int
    infectious: int
    recovered: int
    new_infections: int
    cumulative_infections: int
    reproduction_estimate: float


def simulate(people: list[Person], *, days: int, beta: float, seed: int,
             initial_infected: int = 1, infectious_period: float = 5.0,
             contact_scale: float = 1.0) -> list[Day]:
    """Run a discrete-time stochastic SIR process over a closed population.

    Each infectious person makes one effective contact opportunity per day;
    beta is the per-contact transmission probability. Susceptible targets are
    sampled uniformly, and recovery is geometric with mean infectious_period.
    """
    n = len(people)
    if days < 0 or n == 0 or not 0 <= initial_infected <= n:
        raise ValueError('invalid population, duration, or initial infection count')
    if not 0 <= beta <= 1 or infectious_period <= 0 or not 0 <= contact_scale <= 1:
        raise ValueError('beta/contact_scale must be in [0,1] and infectious_period positive')
    rng = random.Random(seed)
    state = ['S'] * n
    infected_on = [None] * n
    for i in range(initial_infected):
        state[i] = 'I'; infected_on[i] = 0
    out = []
    cumulative = initial_infected
    prev_i = initial_infected
    for day in range(days + 1):
        s = state.count('S'); inf = state.count('I'); rec = n - s - inf
        new = cumulative - (out[-1].cumulative_infections if out else 0)
        r_eff = new / prev_i if prev_i else 0.0
        out.append(Day(day, s, inf, rec, new, cumulative, r_eff))
        if day == days: break
        infectious_ids = [i for i, x in enumerate(state) if x == 'I']
        susceptible_ids = [i for i, x in enumerate(state) if x == 'S']
        newly = set()
        if susceptible_ids and infectious_ids and contact_scale and beta:
            # Binomial contact pressure; multiple sources can target the same person.
            for source in infectious_ids:
                if rng.random() < contact_scale:
                    target = rng.choice(susceptible_ids)
                    if target not in newly and rng.random() < beta:
                        newly.add(target)
        for i in newly:
            state[i] = 'I'; infected_on[i] = day + 1
        cumulative += len(newly)
        recovery_p = 1.0 / infectious_period
        for i in infectious_ids:
            if rng.random() < recovery_p:
                state[i] = 'R'
        prev_i = inf
    return out


def compare_interventions(population: int, *, days: int, beta: float, seed: int) -> dict[str, dict[str, float]]:
    """Compare baseline with 50%-contact reduction under common random seeds."""
    if population <= 0: raise ValueError('population must be positive')
    results = {}
    for label, scale in [('baseline', 1.0), ('distancing', .5)]:
        trajectory = simulate([Person(i) for i in range(population)], days=days,
                              beta=beta, seed=seed, contact_scale=scale)
        results[label] = {
            'final_attack_rate': trajectory[-1].cumulative_infections / population,
            'peak_infectious': float(max(x.infectious for x in trajectory)),
            'peak_day': float(max(trajectory, key=lambda x: x.infectious).day),
        }
    return results
