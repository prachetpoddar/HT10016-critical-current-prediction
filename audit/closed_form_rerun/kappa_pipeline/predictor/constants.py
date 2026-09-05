"""The two constants run_closed_form_fits.py imports.

GLOBAL_ALPHA is stated in that file's own comment as 0.047. LOG_H_EPS is not
stated anywhere available, and the package both came from is not in this
repository. The value here is a guess.

Neither can be validated against the deposit. The only deposited output of that
fitter is form3_per_compound_fits.csv, which carries Form 3 columns alone, and
neither constant enters the Form 3 predictor. Saying that Form 3 reproduces is
therefore no evidence at all about these two values, and an earlier version of
this docstring offered exactly that as the check.

What can be established, and is, by reading run_closed_form_fits.py rather than
by running it: neither constant can move a Form 3 result. Both appear only in
form1_predict. run_per_compound creates one default_rng(42) per compound and
consumes it with rng.shuffle inside the form loop, after a skip test that reads
only the size and temperature count of the filtered frame, and filter_per_form
uses neither constant. A Form 1 fit that raises is caught after its shuffle has
already happened. So the random stream, the Form 3 filter and the Form 3 fit
are all independent of these values.

The consequence for anything this repository writes: every form1_* column
produced with these constants is unusable, and the rerun script drops those
columns rather than depositing them beside the Form 3 columns that reproduce.
"""
GLOBAL_ALPHA = 0.047
LOG_H_EPS = 1e-3
