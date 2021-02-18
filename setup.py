from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

import sys
if sys.version_info[:2] >= (3,7):
    numpy_version = "numpy"
else:
    numpy_version = 'numpy==1.19.5'


setup(
    name='SLTev',
    version='1.1.3',
    author="Mohammad Mahmoudi",
    author_email="zaribar2928@gmail.com",
    description="a tool for evaluation",
    long_description=long_description,
    packages=['SLTev',],
    data_files = [ ('SLTev', ['SLTev/mwerSegmenter']) ],
    include_package_data=True,
    install_requires=[numpy_version, 'gitpython', 'sacremoses', 'sacrebleu', 'gitdir', 'jiwer', 'filelock'],
    url="https://github.com/ELITR/SLTev.git",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX :: Linux',
    ],
    entry_points={
        'console_scripts': [
            'SLTev = SLTev.SLTev:main',
        ],
    },
    python_requires='>=3.6',

)
