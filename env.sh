# Project environment. Usage: source env.sh
# Only affects the current terminal; other projects are untouched.
module unload jupyter/14.6.5 python39 2>/dev/null
module load python/3.11
unset PYTHONPATH
source .venv/bin/activate
