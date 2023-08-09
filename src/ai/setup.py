#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

VERSION = "0.1.0"

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
]

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.md', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

DEPENDENCIES = [
    "openai",
    "colorama"
]

setup(
    name='ai',
    version=VERSION,
    description='Interact with LLM to generate and executable Azure CLIs.',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    author='Microsoft Corporation',
    author_email='sulixu@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/ai',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_ai': ['azext_metadata.json']}
)
