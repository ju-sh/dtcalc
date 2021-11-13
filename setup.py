import pathlib
import setuptools

long_description = pathlib.Path("README.md").read_text()

setuptools.setup(
    name="dtcalc",
    version="0.1-alpha0",
    author="Julin S",
    author_email="",
    description="Find difference between dates and times",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ju-sh/dtcalc",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    project_urls={
        'Changelog': 'https://github.com/ju-sh/dtcalc/blob/master/CHANGELOG.md',
        'Issue Tracker': 'https://github.com/ju-sh/dtcalc/issues',
    },
    install_requires=[],
    python_requires='>=3.7',
)
