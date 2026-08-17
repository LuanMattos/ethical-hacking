# setup.py
from setuptools import setup, find_packages

setup(
    name="zeroday",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        # outras dependências
    ],
)