import subprocess
import re
import os.path
from collections import namedtuple

SCORE_REGEXP = re.compile(
    r'^Your\ code\ has\ been\ rated\ at\ (\-?[0-9\.]+)/10')

TOOLS_ROOT = os.path.dirname(os.path.dirname(__file__))


def parse_output(pylint_output):
    """Parse the score out of pylint's output as a float If the score is not
    found, return 0.0.
    """
    score = 0.0
    errors = 0
    warnings = 0
    for line in pylint_output.splitlines():
        match = re.match(SCORE_REGEXP, line)
        if match:
            score = float(match.group(1))
        if line.lower().startswith('e:'):
            errors = errors + 1
        if line.lower().startswith('w:'):
            warnings = warnings + 1

    return score, errors, warnings


def execute_pylint(filename):
    """Execute a pylint process and collect it's output
    """
    process = subprocess.Popen(
        ["pylint", filename, "-r", "y"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stout, sterr = process.communicate()
    status = process.poll()
    return status, stout, sterr


module_info = namedtuple('mark', ['File', 'score', 'warnings'])
modules = [module_info('pyocd/target/target_CY8C6xx7.py', 8.76, 8), module_info('pyocd/target/target_CY8C6xxA.py', 8.76, 7)]


def main():
    status = 0
    for module in modules:
        _, stdout, stderr = execute_pylint(os.path.join(TOOLS_ROOT, module.File))
        print stdout
        score, errors, warnings = parse_output(stdout)
        if errors > 0:
            print 'Detected errors: ', errors
        if warnings > module.warnings:
            print 'Detected warnings: ', module.warnings

        # pyocd 0.16.1 taken as a baseline
        if score < module.score or errors > 0 or warnings > module.warnings:
            status = 1

    exit(status)


if __name__ == "__main__":
    main()
