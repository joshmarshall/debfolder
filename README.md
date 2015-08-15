# DebFolder

This project contains a few helpers for building /debian folders, primarily
for Python projects (although it can be extended for others), and primarily
for `dh_virtualenv` based projects.

## Instructions

Install the package, either through `pip install debfolder` or manually
by pulling it down and running `python setup.py install`.

Create a `deb.json` file that contains at minimum the following values:

```json
{
    "project": "projectname",
    "description": "This is an awesome project",
    "maintainer": "Joe Brigs <joe.brigs@email.com>"
}
```

This file should ideally live inside the project folder, in the same
directory as the `setup.py` or `Makefile` for the project you wish to build.

Run the `debfolder` command inside the project directory. Optionally, you
can run `debfolder --changelog` to generate a Debian compatible changelog
from a Git repository.

Run `parse_git_log` inside a Git repository folder to print out a
Debian-compatible changelog without creating a Debian folder or writing
any files.

## Customizing

There are a lot of customizable options in the deb.json file or by using the
direct functions inside `debfolder.git_helpers.py` or
`debfolder.setup_helpers.py`. Specifically, `debfolder.setup_helpers.py`
contains a `find_data_files("/PATH")` function which can be used in setup.py
files to automatically discover static assets, templates, etc. for projects.

Use `debfolder.git_helpers.py:get_current_version()` inside a setup.py file
if you would like to use the Git-generated version. These look like:

```
YYYY.MMDD.HHMMSS-HASH or
2015.0814.125234-871d956
```

...and are designed to be used so that you don't have to keep versions
up-to-date manually. This is especially useful in continuous integration /
continuous deployment environments.

*Feedback invited! Tests are missing!*
