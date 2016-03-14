COMMIT_LOG = [{
    "%cn": "Joe",
    "%ce": "joe@email.com",
    "%ct": "1439654861",
    "%h": "hash",
    "%s": "Commit message."
}, {
    "%cn": "Jane",
    "%ce": "jane@email.com",
    "%ct": "1439615320",
    "%h": "hash2",
    "%s": "Other commit message."
}]


def create_git_log_output(format_str, entries):
    output_lines = []
    for entry in COMMIT_LOG[:entries]:
        output = format_str
        for key, value in entry.items():
            output = output.replace(key, value)
        output_lines.append(output)
    return "\n".join(output_lines).encode("utf8")
