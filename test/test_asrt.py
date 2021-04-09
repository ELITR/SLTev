import subprocess
import difflib
from expected_outputs import asrt_result
import os
from pathlib import Path

# checking ASReval (asrt file)
def test_asrt_output():
    cmd = (
        "ASReval -i "
        + "{} ".format(
            os.path.join(Path.cwd().parent, "sample-data", "sample.en.en.asrt")
        )
        + "{} ".format(os.path.join(Path.cwd().parent, "sample-data", "sample.en.OSt"))
        + "{} ".format(os.path.join(Path.cwd().parent, "sample-data", "sample.en.OStt"))
        + "-f asrt ost ostt "
        + "2> /dev/null"
    )
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    out_result = proc.communicate()[0].decode("utf-8")
    output_list = [
        li
        for li in difflib.ndiff(
            " ".join(asrt_result.split("\n")[1:]), " ".join(out_result.split("\n")[1:])
        )
        if li[0] != " "
    ]
    assert output_list == []

