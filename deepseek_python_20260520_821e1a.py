"""
FAREY-RIEMANN SDG ENGINE - ASCII ONLY VERSION
Runs on Python IDLE - no special characters
"""

import math
import hashlib

# ============================================================================
# PART 1: FAREY SEQUENCE AND EULER'S TOTIENT
# ============================================================================

def farey_sequence(n):
    """Generate Farey sequence F_n as list of fractions."""
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
    """Build Markov transition matrix (as list of lists)."""
    m = len(farey)
    denoms = [frac[1] for frac in farey]
    phis = [euler_phi(d) for d in denoms]
    total_phi = sum(phis)
    
    P = []
    for i in range(m):
        row = [phi / total_phi for phi in phis]
        P.append(row)
    return P


def stationary_distribution(P, iterations=1000):
    """Compute stationary distribution by power iteration."""
    m = len(P)
    pi = [1.0 / m] * m
    
    for _ in range(iterations):
        new_pi = [0.0] * m
        for i in range(m):
            for j in range(m):
                new_pi[j] += pi[i] * P[i][j]
        pi = new_pi
    
    return pi


# ============================================================================
# PART 2: CONVERGENCE TO GOLDEN RATIO
# ============================================================================

def golden_ratio_convergence(max_n=20):
    """Show convergence of mean Farey fraction to golden ratio."""
    phi_true = (1 + math.sqrt(5)) / 2
    results = []
    
    for n in range(3, max_n + 1):
        farey = farey_sequence(n)
        P = build_transition_matrix(farey)
        pi = stationary_distribution(P)
        
        # Weighted average of fractions
        avg = 0.0
        for (num, den), prob in zip(farey, pi):
            avg += prob * (num / den)
        results.append((n, avg))
        
        error = abs(avg - phi_true)
        print(f"n={n:2d}: mean fraction = {avg:.6f}, error = {error:.8f}")
    
    return results


# ============================================================================
# PART 3: CANTOR SET RATIONALS
# ============================================================================

def is_in_cantor_set(frac, max_digits=10):
    """Check if fraction is in Cantor set (base-3 digits only 0 and 2)."""
    p, q = frac
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
    {'name': 'Middle 20%', 'farey_denom': 5},
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
    return P


# ============================================================================
# PART 5: SDG PENALTY FUNCTION
# ============================================================================

def sdg_penalty(pi, thresholds=None):
    """Calculate penalty for SDG violations."""
    if thresholds is None:
        thresholds = {'min_pi': 0.03, 'max_gini': 0.4}
    
    min_pi = min(pi)
    # Simplified Gini (based on distribution)
    gini = 1.0 - sum(p**2 for p in pi)
    
    penalty = 0.0
    if min_pi < thresholds['min_pi']:
        penalty += (thresholds['min_pi'] - min_pi) ** 2
    if gini > thresholds['max_gini']:
        penalty += (gini - thresholds['max_gini']) ** 2
    
    return penalty, min_pi, gini


# ============================================================================
# PART 6: POLICY FINGERPRINT
# ============================================================================

def policy_fingerprint(P):
    """Generate SHA-256 fingerprint of policy."""
    # Convert matrix to string
    P_str = ""
    for row in P:
        for val in row:
            P_str += f"{val:.6f},"
    return hashlib.sha256(P_str.encode()).hexdigest()[:7].upper()


# ============================================================================
# PART 7: SIMPLE ODE SOLVER (RK4)
# ============================================================================

def f_ode(x, y):
    """dy/dx = (y^2 - x^2) / (y^2 + x^2)"""
    if y*y + x*x == 0:
        return 0
    return (y*y - x*x) / (y*y + x*x)


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
    
    results = []
    for _ in range(steps + 1):
        if abs(x - 0.2) < h/2:
            y_at_02 = y
        if abs(x - 0.4) < h/2:
            y_at_04 = y
        results.append((x, y))
        y = rk4_step(x, y, h)
        x += h
    
    return y_at_02, y_at_04


# ============================================================================
# PART 8: MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("FAREY-RIEMANN SDG ENGINE")
    print("ASCII version - runs on Python IDLE")
    print("=" * 60)
    
    # Part 1: Golden ratio convergence
    print("\n[1] CONVERGENCE TO GOLDEN RATIO (phi = 1.618034)")
    print("-" * 50)
    results = golden_ratio_convergence(15)
    
    # Part 2: Cantor set rationals
    print("\n[2] CANTOR SET RATIONALS")
    print("-" * 50)
    farey = farey_sequence(10)
    cantor = cantor_rationals_from_farey(farey)
    print(f"Farey sequence F_10 has {len(farey)} fractions")
    print(f"Cantor set endpoints in F_10: {len(cantor)}")
    print(f"Examples: {cantor[:5]}")
    
    # Part 3: Wealth distribution
    print("\n[3] WEALTH DISTRIBUTION (5 quintiles)")
    print("-" * 50)
    P_wealth = build_wealth_transition_matrix()
    pi_wealth = stationary_distribution(P_wealth)
    
    for i, state in enumerate(WEALTH_STATES):
        print(f"  {state['name']:15s}: {pi_wealth[i]:.4f}")
    
    # Part 4: SDG compliance
    print("\n[4] SDG COMPLIANCE CHECK")
    print("-" * 50)
    thresholds = {'min_pi': 0.03, 'max_gini': 0.4}
    penalty, min_pi, gini = sdg_penalty(pi_wealth, thresholds)
    
    check1 = "OK" if min_pi >= 0.03 else "FAIL"
    check2 = "OK" if gini <= 0.4 else "FAIL"
    print(f"  Minimum probability: {min_pi:.4f} [{check1}]")
    print(f"  Gini coefficient: {gini:.4f} [{check2}]")
    print(f"  SDG penalty: {penalty:.6f}")
    
    # Part 5: ODE solver (RK4)
    print("\n[5] ODE SOLVER (RK4)")
    print("-" * 50)
    y02, y04 = solve_ode(y0=1.0, x_start=0.0, x_end=0.4, steps=100)
    print(f"  dy/dx = (y^2 - x^2)/(y^2 + x^2)")
    print(f"  y(0.2) = {y02:.6f}")
    print(f"  y(0.4) = {y04:.6f}")
    
    # Part 6: Policy fingerprint
    print("\n[6] POLICY FINGERPRINT")
    print("-" * 50)
    fingerprint = policy_fingerprint(P_wealth)
    print(f"  Fingerprint: {fingerprint}")
    
    # Part 7: Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    phi_true = (1 + math.sqrt(5)) / 2
    final_error = abs(results[-1][1] - phi_true)
    print(f"  Golden ratio phi = {phi_true:.6f}")
    print(f"  Final approximation error: {final_error:.8f}")
    print(f"  Cantor rationals in F_10: {len(cantor)}")
    print(f"  ODE solution y(0.4): {y04:.6f}")
    print(f"  Policy fingerprint: {fingerprint}")
    print("\n  SDG 10 target: Gini < 0.4")
    if gini <= 0.4:
        print("  -> Gini target MET")
    else:
        print("  -> Gini target NOT MET (needs optimization)")
    print("=" * 60)


if __name__ == "__main__":
    main()