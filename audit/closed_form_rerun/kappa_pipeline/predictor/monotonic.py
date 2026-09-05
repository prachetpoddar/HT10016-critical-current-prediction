"""A stub for the monotonic baseline.

The real module is not in this repository. It is used only by the
monotonic_K3 block of run_closed_form_fits.py, which is wrapped in its own
try/except, runs after every Form fit has completed, and draws no random
numbers. Raising here therefore leaves the Form 3 column identical and records
the baseline as unavailable rather than silently producing one.
"""


class Anchor:
    def __init__(self, temperature_K, field_T, log_Jc):
        self.temperature_K = temperature_K
        self.field_T = field_T
        self.log_Jc = log_Jc


def predict(*a, **k):
    raise RuntimeError("monotonic baseline not available in this repository")
