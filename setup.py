from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='SLTev',
    version='1.0.8',
    author="Mohammad Mahmoudi",
    author_email="zaribar2928@gmail.com",
    description="a tool for evaluation",
    long_description=long_description,
    packages=['SLTev',],
    data_files = [ ('SLTev', ['SLTev/mwerSegmenter']) ],
    include_package_data=True,
    install_requires=['gitpython', 'requests', 'mosestokenizer', 'sacrebleu', 'gitdir', 'jiwer', 'filelock'],
    url="https://github.com/ELITR/SLTev.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'SLTev = SLTev.SLTev:main',
        ],
    },
    python_requires='>=3.7',

)

