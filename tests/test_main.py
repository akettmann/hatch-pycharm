import subprocess
import sys


def test_no_error(new_project):
    subprocess.run([sys.executable, "-m", "hatch", "run", "echo", "a"], check=True)
    print(list(new_project.iterdir()))
