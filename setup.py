import setuptools


setuptools.setup(
    name="debfolder",
    version="0.3.1",
    description="A few tools for building Debian packages for Python.",
    author="Josh Marshall",
    author_email="catchjosh@gmail.com",
    url="https://github.com/joshmarshall/debfolder",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    install_requires=["pytz"],
    entry_points={
        "console_scripts": [
            "parse_git_log = debfolder.git_helpers:main",
            "debfolder = debfolder.setup_helpers:main"
        ],
    },
    packages=setuptools.find_packages(exclude=["tests", "dist"]))
