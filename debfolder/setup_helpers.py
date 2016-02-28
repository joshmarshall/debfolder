import argparse
import json
import os
import sys

from debfolder import defaults


def find_data_files(folder, filter_file=lambda x: True):
    filtered_files = []
    for root, _, files in os.walk(folder):
        full_paths = [
            "%s/%s" % (root, filename)
            for filename in files
            if filter_file(filename)
        ]
        filtered_files.append((root, full_paths))
    return filtered_files


def update_settings_with_defaults(settings):
    file_values = settings.pop("defaults", {})

    for basename, file_settings in defaults.DEFAULT_OPTIONS.items():
        for key, value in file_settings.items():
            file_values.setdefault(basename, {})
            file_values[basename].setdefault(key, value)

    for required, basename in defaults.REQUIRED_SETTINGS.items():
        if required not in settings:
            raise Exception("Missing required option: {0}".format(required))
        file_values[basename].setdefault(required, settings.pop(required))

    for optional, basename in defaults.OPTIONAL_SETTINGS.items():
        if optional in settings:
            updated = settings.pop(optional)
            original = file_values[basename][optional]
            merge = defaults.MERGE_COMMANDS.get(optional) or \
                defaults.DEFAULT_MERGE
            file_values[basename][optional] = merge(original, updated)

    for basename, keys in defaults.COERCE_COMMANDS.items():
        for key, coercer in keys.items():
            file_values[basename][key] = coercer(file_values[basename][key])

    for key in settings:
        if key not in file_values:
            raise Exception("Unknown setting: {0}".format(key))
        file_values[key].update(settings[key])

    return file_values


def initialize_debian_folder(settings, directory):
    settings = settings.copy()
    file_values = update_settings_with_defaults(settings)

    directory_path = os.path.join(directory, "debian")

    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    for basename, template in defaults.DEBIAN_FILES.items():
        path = os.path.join(directory_path, basename)
        content = template.format(**file_values[basename])
        with open(path, "w") as debian_fp:
            debian_fp.write(content)


def main(sys_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--settings_path", dest="settings_path", default=None)
    parser.add_argument("-d", "--directory", dest="directory", default=None)
    parser.add_argument(
        "-c", "--changelog", help="also generate debian/changelog",
        dest="changelog", action="store_true",
        default=False)

    sys_args = sys_args if sys_args is not None else sys.argv[1:]
    args = parser.parse_args(sys_args)
    directory = args.directory or os.getcwd()

    settings_path = args.settings_path or os.path.join(directory, "deb.json")
    with open(settings_path, "rb") as settings_fp:
        settings = json.loads(settings_fp.read())

    initialize_debian_folder(settings, directory)

    if args.changelog:
        from debfolder import git_helpers
        project = settings["project"]
        changelog = []
        for commit in git_helpers.parse_commits(cwd=directory):
            log_line = git_helpers.generate_changelog_entry(project, commit)
            changelog.append(log_line)

        changelog_path = os.path.join(directory, "debian", "changelog")
        with open(changelog_path, "wb") as changelog_fp:
            changelog_fp.write("\n".join(changelog))


if __name__ == "__main__":
    main()
