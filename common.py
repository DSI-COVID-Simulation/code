"""
common.py
some epidemiological assumptions
"""

import numpy as np
import math
from scipy import stats
from scipy.stats import gamma

IFR = 0.01
"""
IFR: Infection fatality ratio is assumed to be 1% regardless of age
"""

SAR = 0.35
"""
SAR: Maximum Secondary Attack Rate is assumed to be 0.35 for close contacts
"""
    
def incubation(n):
    """
    Infected agent's incubation time indicates
    time between infection and symptom onset
    randomly drawn from a lognormal distribution
   (n is a dummy variable)
   """
    return np.random.lognormal(mean=1.63, sigma=0.5)


def infectiousness(t):
    """
    infectiousness function at t-th day of symptom onset (t = time_since_infection - incubation)
    agent's infectiousness from Dr. Ashcroft's work doi:10.4414/smw.2020.20336 
    or a box function?: max(np.sign((t+4)*(-t+8)), 0)
    """
    return gamma.pdf(t, 97.18750, -25.625, 1/3.71875)/0.1511372
    """
    infectiousness function is not a p.d.f.
    It is scaled to be one at its maximum, meaning
    when the agent is most infectious, every contact of the agent is infected at the rate of SAR (0.35).
    """

def detectability(t):
    """
    detectability function at t-th day of symptom onset (t = time_since_infection - incubation).
    detectability is defined as the probability of a positive test result given the agent is infected with SARS-CoV-2 (sensitivity).
    detectability is assumed to have the same shape as the infectiousness function.
    """
    return gamma.pdf(t, 97.18750, -25.625, 1/3.71875)/0.1511372

    """
    Detectability function is not a p.d.f.
    It is scaled to be one at its maximum:
    when the detectability is 1, the sensitivity of the PCR test is 100%.
    """

