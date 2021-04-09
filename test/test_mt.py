import subprocess
import difflib
from expected_outputs import mt_result
import os
from pathlib import Path

# checking MTeval
def test_mt_output():
    cmd = (
        "MTeval -i "
        + "{} ".format(
            os.path.join(Path.cwd().parent, "sample-data", "sample.en.cs.mt")
        )
        + "{} ".format(os.path.join(Path.cwd().parent, "sample-data", "sample.cs.OSt"))
        + "-f mt ref "
        + "2> /dev/null"
    )
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    out_result = proc.communicate()[0].decode("utf-8")
    output_list = [
        li
        for li in difflib.ndiff(
            " ".join(mt_result.split("\n")[1:]), " ".join(out_result.split("\n")[1:])
        )
        if li[0] != " "
    ]
    assert output_list == []


