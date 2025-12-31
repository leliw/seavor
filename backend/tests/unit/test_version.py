import re
import subprocess


def test_version():
    # When: Run a version script
    result = subprocess.run(["python", "app/version.py"], capture_output=True, text=True)
    ret = result.stdout.strip()
    # Then: The version number is returned
    assert ret
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, ret)
