import argparse
from datetime import datetime
import os
from subprocess import check_output


GIT_COMMAND = ["git", "log", "--pretty=format:{format}"]

FORMATS = {
    "committer": "%cn <%ce>",
    "timestamp": "%ct",
    "hash": "%h",
    "message": "%s"
}

CHANGE_ENTRY = """{project} ({version}) UNRELEASED; urgency=low

  * {subject}

 -- {author}  {date}
"""


def generate_git_version(commit):
    date = datetime.fromtimestamp(int(commit["timestamp"]))
    return date.strftime("%Y.%m%d.%H%M%S") + "-" + commit["hash"]


def generate_changelog_entry(
        project, commit, upload_target="UNRELEASED", urgency="low",
        version=generate_git_version):
    version_string = version(commit)
    date = datetime.fromtimestamp(int(commit["timestamp"]))
    commit_date = date.strftime("%a, %d %b %Y %H:%M:%S ") + "+0000"
    return CHANGE_ENTRY.format(
        project=project, version=version_string, subject=commit["message"],
        author=commit["committer"], date=commit_date, urgency=urgency,
        upload_target=upload_target)


def parse_commits(cwd=None, entries=100):
    commits = {}

    for attribute, format_string in FORMATS.items():
        command = [c.format(format=format_string) for c in GIT_COMMAND]
        if entries > 0:
            command += ["-n", str(entries)]
        commit_lines = [l.strip() for l in check_output(command).splitlines()]
        for i in range(len(commit_lines)):
            commits.setdefault(i, {})
            commits[i][attribute] = commit_lines[i]

    indexes = commits.keys()
    indexes.sort()

    return [commits[i] for i in indexes]


def get_current_version(cwd=None, version=generate_git_version):
    # project is unimportant for version string
    commit = parse_commits(cwd=cwd, entries=1)[0]
    return version(commit)


def main():
    default_project_name = os.path.basename(
        os.path.dirname(os.path.abspath(__file__))).lower()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--project", default=default_project_name, help="project name")
    parser.add_argument(
        "-n", "--entries", dest="entries", type=int,
        default=100, help="# of changelog entries")

    args = parser.parse_args()

    changelog = []

    for commit in parse_commits(entries=args.entries):
        changelog.append(generate_changelog_entry(args.project, commit))

    print "\n".join(changelog)


if __name__ == "__main__":
    main()
