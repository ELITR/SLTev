import subprocess
import difflib
from expected_outputs import asr_result
import os
from pathlib import Path

# checking ASReval (asr file)
def test_asr_output():
    cmd = (
        "ASReval -i "
        + "{} ".format(
            os.path.join(Path.cwd().parent, "sample-data", "sample.en.en.asr")
        )
        + "{} ".format(os.path.join(Path.cwd().parent, "sample-data", "sample.en.OSt"))
        + "-f asr ost "
        + "2> /dev/null"
    )

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    out_result = proc.communicate()[0].decode("utf-8")
    output_list = [
        li
        for li in difflib.ndiff(
            " ".join(asr_result.split("\n")[1:]), " ".join(out_result.split("\n")[1:])
        )
        if li[0] != " "
    ]
    assert output_list == []

