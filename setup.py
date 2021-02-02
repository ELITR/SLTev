#pip install -e .
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
"""
'SLTev/utilities.py','SLTev/ASRev.py', 'SLTev/evaluator.py', 'SLTev/delay_modules.py', 'SLTev/flicker_modules.py', 'SLTev/files_modules.py', 'SLTev/quality_modules.py' 
"""
    
import os
import sys
SLTev_path = os.path.dirname(os.path.abspath(__file__)) + "/SLTev"
sys.path.insert(1, SLTev_path)
setup(
    name='SLTev',
    version='1.0.0',
    author="Mohammad Mahmoudi",
    author_email="zaribar2928@gmail.com",
    description="a tool for evaluation",
    long_description=long_description,
    packages=['SLTev',],
    data_files = [ ('SLTev', ['SLTev/mwerSegmenter']) ],
    include_package_data=True,
    install_requires=['gitpython', 'requests', 'mosestokenizer', 'sacrebleu', 'gitdir', 'jiwer'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['SLTev/SLTev'],
    python_requires='>=3.6',

)



