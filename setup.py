from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name="magma_kernel",
    version="0.1a1",
    author="Nils Bruin",
    author_email="nbruin@sfu.ca",
    description="A Jupyter kernel for the Magma computer algebra system",
    long_description=readme(),
    keywords="jupyter kernel magma",
    license="BSD",
    url="https://github.com/nbruin/magma_kernel",
    install_requires="wexpect>=4.0",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: IPython",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ]
)
