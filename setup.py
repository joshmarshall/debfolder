import setuptools


setuptools.setup(
    name="debhelpers",
    version="0.1.0a",
    description="A few tools for building Debian packages.",
    author="Josh Marshall",
    author_email="catchjosh@gmail.com",
    url="https://github.com/joshmarshall/pydeb-helpers",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    packages=setuptools.find_packages(exclude=["tests", "dist"]))
