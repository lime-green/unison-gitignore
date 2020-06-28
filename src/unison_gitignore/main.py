import os
import sys

from .parser import GitIgnoreToUnisonIgnore
from .util import (
    build_cmd,
    collect_paths_from_cmd,
    collect_gitignores_from_path,
    logger,
    run_cmd,
)


def main(cmd=None, cwd=None):
    if cmd is None:
        cmd = sys.argv
    if cwd is None:
        cwd = os.getcwd()

    unison_ignores = []
    cmd_args = cmd[1:]

    for abs_path, path in collect_paths_from_cmd(cmd_args, cwd):
        for gitignore_root, gitignore in collect_gitignores_from_path(abs_path):
            gitignore_anchor = os.path.relpath(gitignore_root, abs_path)
            if gitignore_anchor == ".":
                gitignore_anchor = ""

            parser = GitIgnoreToUnisonIgnore(gitignore_anchor)
            with open(gitignore, "r") as fh:
                unison_ignores.extend(parser.parse_gitignore(fh))

    logger.info(
        f"Adding {len(unison_ignores)} ignore patterns based on .gitignore contents"
    )
    cmd_new = build_cmd(cmd_args, unison_ignores)
    run_cmd(cmd_new)
