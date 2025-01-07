from setuptools import setup, find_packages

setup(
    name="mdconverter",
    version="0.1.0",
    description="Converter from Jupyter Notebook(.ipynb) to Markdown(.md)",
    author="sooyoung-wind, teddylee777",
    author_email="sooyoung.wind@gmail.com, teddylee777@gmail.com",
    packages=find_packages(),
    install_requires=[
        "nbconvert>=7.16.5",
    ],
    python_requires=">=3.11",
)
