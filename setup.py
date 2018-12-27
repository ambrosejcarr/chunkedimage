#!/usr/bin/env python

import os
import setuptools

install_requires = [
    line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "REQUIREMENTS.txt"))
]
print(install_requires)

setuptools.setup(
    name="chunkedimage",
    version="0.0.0",
    description="Library to access chunked imaging data",
    author="Ambrose J Carr",
    author_email="acarr@chanzuckerberg.com",
    license="MIT",
    packages=setuptools.find_packages(
        exclude=(
            "tests",
            "tests.*",
        )
    ),
    install_requires=install_requires,
)
