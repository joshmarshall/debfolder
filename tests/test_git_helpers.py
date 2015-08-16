from StringIO import StringIO
import unittest

import mock

from debfolder import git_helpers

from tests.output import create_git_log_output


TEST_TIMESTAMP = 1439654861.243068
TEST_COMMIT = {
    "timestamp": TEST_TIMESTAMP,
    "hash": "hash",
    "message": "Commit message.",
    "committer": "Joe <joe@email.com>"
}

EXPECTED_ENTRIES = ["""project (2015.0815.160741-hash) UNRELEASED; urgency=low

  * Commit message.

 -- Joe <joe@email.com>  Sat, 15 Aug 2015 16:07:41 +0000
""", """project (2015.0815.050840-hash2) UNRELEASED; urgency=low

  * Other commit message.

 -- Jane <jane@email.com>  Sat, 15 Aug 2015 05:08:40 +0000
"""]


class TestGitHelpers(unittest.TestCase):

    def setUp(self):
        super(TestGitHelpers, self).setUp()
        self.check_output_calls = []
        self.check_output_results = {}
        self.patch_check_output = None

    def mock_check_output(self, command, cwd):
        command = tuple(command)
        if command not in self.check_output_results:
            self.fail("Unexpected command: {0}".format(command))
        output = self.check_output_results.pop(command)
        self.check_output_calls.append((command, cwd))
        return output

    def add_check_output_result(self, command, output):
        self.check_output_results[tuple(command)] = output
        if not self.patch_check_output:
            self.patch_check_output = mock.patch("subprocess.check_output")
            mock_check_output = self.patch_check_output.start()
            mock_check_output.side_effect = self.mock_check_output
            self.addCleanup(self.patch_check_output.stop)

    def add_git_log_format_result(self, format_str, entries=100):
        output = create_git_log_output(format_str, entries)
        self.add_check_output_result([
            "git", "log", "--pretty=format:{0}".format(format_str),
            "-n", str(entries)
        ], output)

    def assert_all_calls_made(self):
        self.assertEqual(
            0, len(self.check_output_results),
            "Not all expected `subprocess.check_output` calls were made.")

    def assert_cwd_equals(self, expected_cwd):
        for command, cwd in self.check_output_calls:
            self.assertEqual(cwd, expected_cwd)

    def test_generate_git_version_generates_timestamp_hash_version(self):
        version = git_helpers.generate_git_version(TEST_COMMIT)
        self.assertEqual("2015.0815.160741-hash", version)

    def test_generate_changelog_entry_formats_to_debian_specification(self):
        entry = git_helpers.generate_changelog_entry("project", TEST_COMMIT)
        self.assertEqual(EXPECTED_ENTRIES[0], entry)

    def test_generate_changelog_allows_overriding(self):
        entry = git_helpers.generate_changelog_entry(
            "project", TEST_COMMIT, upload_target="UPLOAD", urgency="high",
            version=lambda x: "1.0.1-1")

        expected = EXPECTED_ENTRIES[0].replace("UNRELEASED", "UPLOAD")
        expected = expected.replace("urgency=low", "urgency=high")
        expected = expected.replace("2015.0815.160741-hash", "1.0.1-1")

        self.assertEqual(expected, entry)

    def test_parse_commits_extracts_commits_from_git_repository(self):
        self.add_git_log_format_result("%cn <%ce>")
        self.add_git_log_format_result("%ct")
        self.add_git_log_format_result("%h")
        self.add_git_log_format_result("%s")

        commits = git_helpers.parse_commits()
        self.assertEqual([{
            "committer": "Joe <joe@email.com>",
            "hash": "hash",
            "timestamp": "1439654861",
            "message": "Commit message."
        }, {
            "committer": "Jane <jane@email.com>",
            "hash": "hash2",
            "timestamp": "1439615320",
            "message": "Other commit message."
        }], commits)

        self.assert_all_calls_made()

    def test_parse_commits_allows_custom_cwd_and_entries(self):
        self.add_git_log_format_result("%cn <%ce>", entries=1)
        self.add_git_log_format_result("%ct", entries=1)
        self.add_git_log_format_result("%h", entries=1)
        self.add_git_log_format_result("%s", entries=1)

        commits = git_helpers.parse_commits(cwd="/path", entries=1)

        self.assertEqual([{
            "committer": "Joe <joe@email.com>",
            "hash": "hash",
            "timestamp": "1439654861",
            "message": "Commit message."
        }], commits)

        self.assert_all_calls_made()
        self.assert_cwd_equals("/path")

    def test_get_current_version_grabs_most_recent_commit(self):
        self.add_git_log_format_result("%cn <%ce>", entries=1)
        self.add_git_log_format_result("%ct", entries=1)
        self.add_git_log_format_result("%h", entries=1)
        self.add_git_log_format_result("%s", entries=1)

        version = git_helpers.get_current_version()
        self.assertEqual("2015.0815.160741-hash", version)

    def test_get_current_version_allows_custom_cwd_and_version(self):
        self.add_git_log_format_result("%cn <%ce>", entries=1)
        self.add_git_log_format_result("%ct", entries=1)
        self.add_git_log_format_result("%h", entries=1)
        self.add_git_log_format_result("%s", entries=1)

        version_gen = lambda x: x["hash"]

        version = git_helpers.get_current_version(
            cwd="/path", version=version_gen)
        self.assertEqual("hash", version)
        self.assert_cwd_equals("/path")

    def test_main_execution(self):
        self.add_git_log_format_result("%cn <%ce>")
        self.add_git_log_format_result("%ct")
        self.add_git_log_format_result("%h")
        self.add_git_log_format_result("%s")

        output = StringIO()
        git_helpers.main(["--project", "project"], output)

        output.seek(0)
        self.assertEqual(output.read(), "\n".join(EXPECTED_ENTRIES) + "\n")
