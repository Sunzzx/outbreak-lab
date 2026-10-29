import math
from outbreak_lab import Person, simulate, compare_interventions


def test_seeded_simulation_is_reproducible():
    people = [Person(i) for i in range(80)]
    a = simulate(people, days=20, beta=.22, seed=7)
    b = simulate(people, days=20, beta=.22, seed=7)
    assert a == b


def test_zero_transmission_stops_after_seed_infectiousness():
    result = simulate([Person(i) for i in range(20)], days=10, beta=0, seed=1, initial_infected=1)
    assert result[-1].cumulative_infections == 1


def test_population_accounting_and_monotonic_cumulative():
    result = simulate([Person(i) for i in range(100)], days=25, beta=.3, seed=4)
    assert all(x.susceptible + x.infectious + x.recovered == 100 for x in result)
    assert all(b.cumulative_infections >= a.cumulative_infections for a, b in zip(result, result[1:]))


def test_infection_counts_nonnegative_and_bounded():
    result = simulate([Person(i) for i in range(60)], days=35, beta=.8, seed=2)
    assert all(0 <= x.cumulative_infections <= 60 for x in result)
    assert all(math.isfinite(x.reproduction_estimate) for x in result)


def test_intervention_comparison_reproducible_and_reduces_contact_rate():
    outcomes = compare_interventions(250, days=40, beta=.24, seed=22)
    assert outcomes['baseline'] == compare_interventions(250, days=40, beta=.24, seed=22)['baseline']
    assert outcomes['distancing']['peak_infectious'] <= outcomes['baseline']['peak_infectious']


def test_invalid_parameters_rejected():
    try:
        simulate([Person(i) for i in range(4)], days=-1, beta=.2, seed=0)
    except ValueError:
        pass
    else:
        raise AssertionError('negative duration must fail')
