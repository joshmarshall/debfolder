DEBIAN_FILES = {
    "compat": """{version}
""",
    "control": """Source: {project}
Section: {section}
Priority: {priority}
Maintainer: {maintainer}
Build-Depends: {build_depends}
Standards-Version: {standards_version}

Package: {project}
Pre-Depends: {pre_depends}
Depends: {depends}
Architecture: {architecture}
Description: {description}
""",
    "rules": """#!/usr/bin/make -f

%:
\t{build_command}

{extra_build_options}
"""
}

DEFAULT_OPTIONS = {
    "compat": {
        "version": "9"
    },
    "control": {
        "section": "python",
        "priority": "extra",
        "build_depends": [
            "debhelper (>= 9)", "python", "dh-virtualenv (>= 0.6)",
            "python-dev", "git-core"
        ],
        "standards_version": "3.9.5",
        "pre_depends": ["dpkg", "python", "${misc:Pre-Depends}"],
        "depends": ["${python:Depends}", "${misc:Depends}"],
        "architecture": "any"
    },
    "rules": {
        "build_command": "dh $@ --with python-virtualenv",
        "extra_build_options": """overide_dh_virtualenv:
\tdh_virtualenv --python /usr/bin/python2.7 --setuptools
    """
    }
}

REQUIRED_SETTINGS = {
    "project": "control",
    "description": "control",
    "maintainer": "control"
}

OPTIONAL_SETTINGS = {
    "depends": "control",
    "build_depends": "control",
    "architecture": "control"
}

MERGE_COMMANDS = {
    "depends": lambda x, y: x + y,
    "build_depends": lambda x, y: x + y,
}

DEFAULT_MERGE = lambda x, y: y

COERCE_COMMANDS = {
    "control": {
        "build_depends": lambda x: ", ".join(x),
        "pre_depends": lambda x: ", ".join(x),
        "depends": lambda x: ", ".join(x),
    }
}
