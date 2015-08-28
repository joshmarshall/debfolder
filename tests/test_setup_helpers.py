import json
import os
import shutil
import tempfile
import unittest

import mock

from debfolder import setup_helpers


EXAMPLE_WALK_OUTPUT = [
    ("/path", ["static", "templates"], []),
    ("/path/static", ["images"], []),
    ("/path/static/images", [], ["image.png", "logo.jpg"]),
    ("/path/templates", [], ["view.html"])
]

EXPECTED_FILES_OUTPUT = [
    ("/path", []),
    ("/path/static", []),
    ("/path/static/images",
        ["/path/static/images/image.png", "/path/static/images/logo.jpg"]),
    ("/path/templates", ["/path/templates/view.html"])
]

EXPECTED_FILTERED_FILES_OUTPUT = [
    ("/path", []),
    ("/path/static", []),
    ("/path/static/images", []),
    ("/path/templates", ["/path/templates/view.html"])
]

BASIC_SETTINGS = {
    "project": "project",
    "maintainer": "Joe <joe@email.com>",
    "description": "Description"
}

INSTALL_SETTINGS = {
    "project": "project",
    "maintainer": "Joe <joe@email.com>",
    "description": "Description",
    "install": {
        "foo/bar/*": "/dest/dir/bar/",
        "foo/*": "/dest/dir/"
    }
}


class TestSetupHelpers(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.tempdir))

    def test_find_data_files_generates_proper_structure(self):
        with mock.patch("os.walk") as mock_walk:
            mock_walk.return_value = EXAMPLE_WALK_OUTPUT
            data_files = setup_helpers.find_data_files("/path")
            mock_walk.assert_called_with("/path")
        self.assertEqual(data_files, EXPECTED_FILES_OUTPUT)

    def test_find_data_files_accepts_filter(self):
        with mock.patch("os.walk") as mock_walk:
            mock_walk.return_value = EXAMPLE_WALK_OUTPUT
            data_files = setup_helpers.find_data_files(
                "/path", lambda x: x.endswith(".html"))
        self.assertEqual(data_files, EXPECTED_FILTERED_FILES_OUTPUT)

    def test_initialize_debian_folder(self):
        setup_helpers.initialize_debian_folder(BASIC_SETTINGS, self.tempdir)
        for filename in ["control", "compat", "rules"]:
            full_path = os.path.join(self.tempdir, "debian", filename)
            self.assertTrue(os.path.exists(full_path))
            # TODO: check content against templates

    # TODO: check optional and required attributes
    # TODO: check merge and coerce behavior

    def test_initialize_debian_folder_with_install(self):
        setup_helpers.initialize_debian_folder(INSTALL_SETTINGS, self.tempdir)
        full_path = os.path.join(self.tempdir, "debian", "install")
        self.assertTrue(os.path.exists(full_path))
        with open(full_path) as install_fp:
            contents = dict([
                a.strip().split(" ") for a in install_fp.readlines()
                if a.strip()
            ])

        self.assertEqual(contents, INSTALL_SETTINGS["install"])

    @mock.patch("debfolder.git_helpers.generate_changelog_entry")
    @mock.patch("debfolder.git_helpers.parse_commits")
    def test_setup_debian_folder_command(self, mock_commits, mock_changelog):
        mock_commits.return_value = [{"a": 1}, {"b": 2}]
        mock_changelog.side_effect = ["MOCK", "CHANGELOG"]

        settings_file = os.path.join(self.tempdir, "deb.json")
        with open(settings_file, "wb") as settings_fp:
            settings_fp.write(json.dumps(BASIC_SETTINGS))
            settings_fp.flush()

        parameters = ["-s", settings_file, "-d", self.tempdir, "-c"]
        setup_helpers.main(parameters)

        for filename in ["control", "compat", "rules"]:
            full_file = os.path.join(self.tempdir, "debian", filename)
            self.assertTrue(os.path.exists(full_file))

        changelog_file = os.path.join(self.tempdir, "debian/changelog")
        self.assertTrue(os.path.exists(changelog_file))

        with open(changelog_file, "rb") as changelog_fp:
            self.assertEqual("MOCK\nCHANGELOG", changelog_fp.read())

        mock_commits.assert_called_with(cwd=self.tempdir)
        mock_changelog.assert_any_call("project", {"a": 1})
        mock_changelog.assert_any_call("project", {"b": 2})
