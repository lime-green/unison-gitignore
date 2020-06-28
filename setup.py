import os
from os.path import join, exists
from setuptools import find_packages, setup

base_dir = os.path.dirname(__file__)
readme_path = join(base_dir, "README.md")
if exists(readme_path):
    with open(readme_path) as stream:
        long_description = stream.read()
else:
    long_description = ""

setup(
    name="unison-gitignore",
    install_requires=["pathspec"],
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="A unison wrapper to integrate with .gitignore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Josh DM",
    url="https://github.com/lime-green/unison-gitignore",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "unison-gitignore = unison_gitignore.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license="MIT",
    keywords=["unison", "gitignore"],
)
