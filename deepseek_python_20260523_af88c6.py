import hashlib
import numpy as np

# Wealth states (5 quintiles)
wealth_states = [
    {'name': 'Poorest 20%', 'farey': (1,5)},
    {'name': 'Second 20%', 'farey': (2,5)},
    {'name': 'Middle 20%', 'farey': (3,5)},
    {'name': 'Fourth 20%', 'farey': (4,5)},
    {'name': 'Richest 20%', 'farey': (1,1)}
]

# SDG thresholds
thresholds = {'min_pi': 0.03, 'max_gini': 0.4, 'min_gap': 0.1}

# Euler's totient function
def euler_phi(n):
    if n <= 1:
        return 1
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result

# Build transition matrix
def build_transition_matrix(states):
    m = len(states)
    P = np.zeros((m, m))
    denoms = [s['farey'][1] for s in states]
    phis = [euler_phi(d) for d in denoms]
    total_phi = sum(phis)
    for i in range(m):
        P[i] = np.array(phis) / total_phi
    return P

# Build the matrix
P_opt = build_transition_matrix(wealth_states)

# Simulate some values
current_dist = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
lumos = 0.7

# Lumos condition
if lumos > 0.6:
    new_dist = current_dist @ P_opt
    print("Lumos ON: distribution updated")
else:
    new_dist = current_dist
    print("Lumos OFF: distribution unchanged")

# Policy fingerprint
P_str = np.array_str(P_opt, precision=6, suppress_small=True)
fingerprint = hashlib.sha256(P_str.encode()).hexdigest()[:7].upper()
print(f"Policy fingerprint: {fingerprint}")

print("\nWealth distribution:")
for i, state in enumerate(wealth_states):
    print(f"  {state['name']}: {new_dist[i]:.4f}")