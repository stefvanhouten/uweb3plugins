import os
from setuptools import setup, find_packages

VERSION = "0.0.4"


def Description():
    """Returns the contents of the README.md file as description information."""
    with open(os.path.join(os.path.dirname(__file__), "README.md")) as r_file:
        return r_file.read()


setup(
    name="uwebthreeplugins",
    version=VERSION,
    description="uWeb3 python3.10 plugin package",
    long_description=Description(),
    long_description_content_type="text/markdown",
    license="ISC",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    author="Stef van Houten",
    author_email="stef@underdark.nl",
    url="https://github.com/stefvanhouten/uweb3plugins",
    keywords="uweb3 plugins",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
)
