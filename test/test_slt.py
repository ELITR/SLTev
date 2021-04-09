import subprocess
import difflib
from expected_outputs import slt_result
import os
from pathlib import Path

# checking SLTeval
def test_slt_output():
    cmd = (
        "SLTeval -i "
        + "{} ".format(
            os.path.join(Path.cwd().parent, "sample-data", "sample.en.cs.slt")
        )
        + "{} ".format(os.path.join(Path.cwd().parent, "sample-data", "sample.cs.OSt"))
        + "{} ".format(os.path.join(Path.cwd().parent, "sample-data", "sample.en.OStt"))
        + "-f slt ref ostt "
        + "2> /dev/null"
    )
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    out_result = proc.communicate()[0].decode("utf-8")
    output_list = [
        li
        for li in difflib.ndiff(
            " ".join(slt_result.split("\n")[1:]), " ".join(out_result.split("\n")[1:])
        )
        if li[0] != " "
    ]
    assert output_list == []


