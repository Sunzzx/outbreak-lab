"""Zero-dependency epidemic scenario demo with Unicode sparkline plots."""
from . import Person, simulate, compare_interventions


def main():
    n, days = 500, 60
    track = simulate([Person(i) for i in range(n)], days=days, beta=.32, seed=42)
    print('OUTBREAK LAB | stochastic SIR + contact-policy comparison')
    print(f'Population {n:,} | duration {days} days | beta 0.32 | seed 42')
    print('\nDay  Infectious  New  Curve')
    peak = max(x.infectious for x in track)
    for x in track[::3]:
        bar = '█' * round(30*x.infectious/max(peak, 1))
        print(f'{x.day:>3}  {x.infectious:>10}  {x.new_infections:>3}  {bar}')
    print('\nCounterfactuals (common seed):')
    for name, stats in compare_interventions(n, days=days, beta=.32, seed=42).items():
        print(f"{name:>10}: attack rate {stats['final_attack_rate']:.1%}; peak {int(stats['peak_infectious'])} on day {int(stats['peak_day'])}")

if __name__ == '__main__': main()
