DEBIAN_FILES = {
    "compat": """{version}
""",
    "install": """{install}
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
            "debhelper (>= 9)", "dh-virtualenv (>= 0.6)", "git-core"
        ],
        "standards_version": "3.9.5",
        "pre_depends": [],
        "depends": [],
        "architecture": "any"
    },
    "rules": {
        "build_command": "dh $@ --with python-virtualenv",
        "extra_build_options": ""
    },
    "install": {
        "install": ""
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
    "architecture": "control",
    "install": "install"
}

MERGE_COMMANDS = {
    "depends": lambda x, y: x + y,
    "build_depends": lambda x, y: x + y,
    "install": lambda x, y: "\n".join([" ".join(i) for i in y.items()] + [x])
}


def DEFAULT_MERGE(x, y):
    return y


COERCE_COMMANDS = {
    "control": {
        "build_depends": lambda x: ", ".join(x),
        "pre_depends": lambda x: ", ".join(x),
        "depends": lambda x: ", ".join(x),
    }
}
