from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="econfin_functions",
    version="0.2.0",
    author="Samuel Bakst",
    author_email="107sbakst@gmail.com",
    description="A Python package for economic and financial data functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/107SBakst/econfin_functions",
    project_urls={
        "Bug Tracker": "https://github.com/107SBakst/econfin_functions/issues",
        "Documentation": "https://github.com/107SBakst/econfin_functions#readme",
        "Source Code": "https://github.com/107SBakst/econfin_functions",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="economics finance data api israel cbs statistics",
    include_package_data=True,
    zip_safe=False,
)