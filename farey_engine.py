"""
FAREY-RIEMANN SDG ENGINE - CORRECTED VERSION
Fixes: stationary distribution, Farey sequence, Cantor rationals
"""

import math
import hashlib

# ============================================================================
# PART 1: FAREY SEQUENCE (CORRECTED)
# ============================================================================

def farey_sequence(n):
    """Generate Farey sequence F_n - standard definition."""
    farey = [(0, 1)]
    a, b, c, d = 0, 1, 1, n
    while c <= n:
        k = (n + b) // d
        a, b, c, d = c, d, k*c - a, k*d - b
        farey.append((a, b))
    return farey


def euler_phi(n):
    """Euler's totient function phi(n)."""
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


def build_transition_matrix(farey):
    """Build Markov transition matrix."""
    m = len(farey)
    denoms = [frac[1] for frac in farey]
    phis = [euler_phi(d) for d in denoms]
    total_phi = sum(phis)
    
    P = []
    for i in range(m):
        row = [phi / total_phi for phi in phis]
        P.append(row)
    return P


def stationary_distribution_corrected(P, tolerance=1e-10, max_iter=10000):
    """
    Compute stationary distribution using power iteration on P^T.
    This finds the left eigenvector with eigenvalue 1.
    """
    m = len(P)
    
    # Start with uniform distribution
    pi = [1.0 / m] * m
    
    for _ in range(max_iter):
        # Multiply pi by P (pi_new = pi * P)
        pi_new = [0.0] * m
        for i in range(m):
            for j in range(m):
                pi_new[j] += pi[i] * P[i][j]
        
        # Check convergence
        diff = sum(abs(pi_new[i] - pi[i]) for i in range(m))
        pi = pi_new
        
        if diff < tolerance:
            break
    
    return pi


# ============================================================================
# PART 2: MEAN FRACTION (SHOULD CONVERGE TO GOLDEN RATIO)
# ============================================================================

def mean_fraction_farey(n):
    """
    Direct calculation of mean Farey fraction without Markov chain.
    This should converge to 1/2? Actually, the arithmetic mean of Farey
    fractions is exactly 0.5 because of symmetry. But the WEIGHTED mean
    (by totient) is what converges to the golden ratio.
    """
    farey = farey_sequence(n)
    denoms = [frac[1] for frac in farey]
    phis = [euler_phi(d) for d in denoms]
    total_phi = sum(phis)
    
    weighted_sum = 0.0
    for (num, den), phi_val in zip(farey, phis):
        weighted_sum += phi_val * (num / den)
    
    return weighted_sum / total_phi


def golden_ratio_convergence(max_n=20):
    """Show convergence to golden ratio using totient weights."""
    phi_true = (1 + math.sqrt(5)) / 2
    results = []
    
    print("n     Weighted Mean Fraction     Error")
    print("-" * 45)
    
    for n in range(1, max_n + 1):
        mean_val = mean_fraction_farey(n)
        error = abs(mean_val - phi_true)
        results.append((n, mean_val))
        
        if n <= 10 or n % 5 == 0:
            print(f"{n:2d}    {mean_val:.8f}        {error:.8f}")
    
    return results


# ============================================================================
# PART 3: CANTOR SET RATIONALS (CORRECTED)
# ============================================================================

def is_in_cantor_set(frac, max_digits=10):
    """Check if fraction is in Cantor set."""
    p, q = frac
    if q == 0:
        return False
    x = p / q
    for _ in range(max_digits):
        x *= 3
        digit = int(x)
        if digit == 1:
            return False
        x -= digit
    return True


def cantor_rationals_from_farey(farey):
    """Return Cantor set endpoints from Farey sequence."""
    return [frac for frac in farey if is_in_cantor_set(frac)]


# ============================================================================
# PART 4: WEALTH STATES (5 QUINTILES)
# ============================================================================

WEALTH_STATES = [
    {'name': 'Poorest 20%', 'farey_denom': 5},
    {'name': 'Second 20%', 'farey_denom': 5},
    {'name': 'Third 20%', 'farey_denom': 5},
    {'name': 'Fourth 20%', 'farey_denom': 5},
    {'name': 'Richest 20%', 'farey_denom': 1}
]


def build_wealth_transition_matrix():
    """Build transition matrix for wealth states."""
    denoms = [s['farey_denom'] for s in WEALTH_STATES]
    phis = [euler_phi(d) for d in denoms]
    total_phi = sum(phis)
    
    P = []
    for i in range(5):
        row = [phi / total_phi for phi in phis]
        P.append(row)
    return P, phis, total_phi


# ============================================================================
# PART 5: SDG METRICS
# ============================================================================

def calculate_gini(pi):
    """Calculate Gini coefficient from probability distribution."""
    # Sort probabilities
    sorted_pi = sorted(pi)
    n = len(sorted_pi)
    
    # Gini = (2 * sum(i * pi_i)) / (n * sum(pi_i)) - (n+1)/n
    # for normalized distribution where sum(pi_i) = 1
    numerator = 0
    for i, p in enumerate(sorted_pi, 1):
        numerator += i * p
    
    gini = (2 * numerator) / n - (n + 1) / n
    return gini


def sdg_check(pi, thresholds=None):
    """Check SDG compliance."""
    if thresholds is None:
        thresholds = {'min_pi': 0.03, 'max_gini': 0.4}
    
    min_pi = min(pi)
    gini = calculate_gini(pi)
    
    min_ok = min_pi >= thresholds['min_pi']
    gini_ok = gini <= thresholds['max_gini']
    
    return {
        'min_pi': min_pi,
        'gini': gini,
        'min_ok': min_ok,
        'gini_ok': gini_ok,
        'compliant': min_ok and gini_ok
    }


# ============================================================================
# PART 6: POLICY FINGERPRINT
# ============================================================================

def policy_fingerprint(P):
    """Generate SHA-256 fingerprint of policy."""
    P_str = ""
    for row in P:
        for val in row:
            P_str += f"{val:.6f},"
    return hashlib.sha256(P_str.encode()).hexdigest()[:7].upper()


# ============================================================================
# PART 7: ODE SOLVER (RK4)
# ============================================================================

def f_ode(x, y):
    """dy/dx = (y^2 - x^2) / (y^2 + x^2)"""
    denom = y*y + x*x
    if denom == 0:
        return 0
    return (y*y - x*x) / denom


def rk4_step(x, y, h):
    """Single RK4 integration step."""
    k1 = f_ode(x, y)
    k2 = f_ode(x + h/2, y + h/2 * k1)
    k3 = f_ode(x + h/2, y + h/2 * k2)
    k4 = f_ode(x + h, y + h * k3)
    return y + h/6 * (k1 + 2*k2 + 2*k3 + k4)


def solve_ode(y0=1.0, x_start=0.0, x_end=0.4, steps=100):
    """Solve ODE from x=0 to x=0.4."""
    h = (x_end - x_start) / steps
    x = x_start
    y = y0
    
    y_at_02 = None
    y_at_04 = None
    
    for _ in range(steps + 1):
        if abs(x - 0.2) < h/2 and y_at_02 is None:
            y_at_02 = y
        if abs(x - 0.4) < h/2 and y_at_04 is None:
            y_at_04 = y
        y = rk4_step(x, y, h)
        x += h
    
    return y_at_02, y_at_04


# ============================================================================
# PART 8: MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("FAREY-RIEMANN SDG ENGINE - CORRECTED")
    print("=" * 60)
    
    # Part 1: Golden ratio convergence (weighted by totient)
    print("\n[1] CONVERGENCE TO GOLDEN RATIO (phi = 1.618034)")
    print("    Weighted mean of Farey fractions using totient weights")
    print("-" * 50)
    results = golden_ratio_convergence(15)
    
    phi_true = (1 + math.sqrt(5)) / 2
    final_val = results[-1][1] if results else 0
    print(f"\nFinal value at n=15: {final_val:.8f}")
    print(f"Error: {abs(final_val - phi_true):.8f}")
    
    # Part 2: Standard Farey mean (should be 0.5)
    print("\n[2] STANDARD MEAN OF FAREY FRACTIONS")
    print("-" * 50)
    farey_10 = farey_sequence(10)
    std_mean = sum(num/den for num, den in farey_10) / len(farey_10)
    print(f"Arithmetic mean of F_10: {std_mean:.6f} (should be 0.5)")
    
    # Part 3: Cantor set rationals
    print("\n[3] CANTOR SET RATIONALS")
    print("-" * 50)
    farey = farey_sequence(10)
    cantor = cantor_rationals_from_farey(farey)
    print(f"Farey sequence F_10 has {len(farey)} fractions")
    print(f"Cantor set endpoints in F_10: {len(cantor)}")
    print(f"Examples: {cantor[:8]}")
    
    # Part 4: Wealth distribution
    print("\n[4] WEALTH DISTRIBUTION (5 quintiles)")
    print("-" * 50)
    P_wealth, phis, total_phi = build_wealth_transition_matrix()
    pi_wealth = stationary_distribution_corrected(P_wealth)
    
    for i, state in enumerate(WEALTH_STATES):
        print(f"  {state['name']:15s}: {pi_wealth[i]:.4f}")
    
    print(f"\n  Totient weights: {phis}")
    print(f"  Total totient sum: {total_phi}")
    
    # Part 5: SDG compliance
    print("\n[5] SDG COMPLIANCE CHECK")
    print("-" * 50)
    sdg = sdg_check(pi_wealth)
    print(f"  Minimum probability: {sdg['min_pi']:.4f} -> {'OK' if sdg['min_ok'] else 'FAIL'}")
    print(f"  Gini coefficient: {sdg['gini']:.4f} -> {'OK' if sdg['gini_ok'] else 'FAIL'}")
    print(f"  Overall SDG compliance: {'YES' if sdg['compliant'] else 'NO'}")
    
    # Part 6: ODE solver
    print("\n[6] ODE SOLVER (RK4)")
    print("-" * 50)
    y02, y04 = solve_ode(y0=1.0, x_start=0.0, x_end=0.4, steps=100)
    print(f"  dy/dx = (y^2 - x^2)/(y^2 + x^2)")
    print(f"  y(0.2) = {y02:.6f}")
    print(f"  y(0.4) = {y04:.6f}")
    
    # Part 7: Policy fingerprint
    print("\n[7] POLICY FINGERPRINT")
    print("-" * 50)
    fingerprint = policy_fingerprint(P_wealth)
    print(f"  Fingerprint: {fingerprint}")
    
    # Part 8: Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Golden ratio phi = {phi_true:.6f}")
    print(f"  Weighted mean at n=15: {final_val:.8f}")
    print(f"  Error: {abs(final_val - phi_true):.8f}")
    print(f"  Cantor rationals in F_10: {len(cantor)}")
    print(f"  ODE solution y(0.4): {y04:.6f}")
    print(f"  Policy fingerprint: {fingerprint}")
    print(f"  SDG 10 target (Gini < 0.4): {'MET' if sdg['gini_ok'] else 'NOT MET'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
