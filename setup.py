from setuptools import setup, find_packages
from webng.core.version import get_version

VERSION = get_version()

f = open("README.md", "r")
LONG_DESCRIPTION = f.read()
f.close()

INSTALL_REQUIRES = [
    "numpy",
    "cement",
    "pyyaml",
    "colorlog",
    "seaborn",
    "h5py",
    "pygpcca",
    "bionetgen>=0.7.5",
    "libroadrunner",
    "networkx",
    "westpa==2.0dev1"
]

EXTRAS_REQUIRE = {
    "dev" : ['pytest', 'twine>=1.11.0', 'wheel>=0.31.0']
}

setup(
    name="webng",
    version=VERSION,
    description="A weighted ensemble simulation setup tool starting from a BNGL model",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Ali Sinan Saglam",
    author_email="asinansaglam@gmail.com",
    url="https://github.com/ASinanSaglam/BNG_WESTPA_pipeline",
    license="unlicensed",
    packages=find_packages(exclude=["ez_setup", "tests*"]),
    package_data={"webng": ["templates/*"]},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points="""
        [console_scripts]
        webng = webng.main:main
    """,
)
