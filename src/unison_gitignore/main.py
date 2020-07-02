import os
import sys

from .parser import GitIgnoreToUnisonIgnore
from .util import (
    build_cmd,
    collect_paths_from_cmd,
    collect_gitignores_from_path,
    get_local_root_from_cmd,
    logger,
    run_cmd,
    should_parse_cmd,
)


def main(cmd=None):
    if cmd is None:
        cmd = sys.argv

    cmd_args = cmd[1:]

    if not should_parse_cmd(cmd_args):
        run_cmd(build_cmd(cmd_args, []))
    else:
        local_root = get_local_root_from_cmd(cmd_args)
        unison_ignores = []

        for abs_path, path in collect_paths_from_cmd(cmd_args):
            for gitignore_dir, gitignore_path in collect_gitignores_from_path(abs_path):
                gitignore_anchor = os.path.relpath(gitignore_dir, local_root)
                if gitignore_anchor == ".":
                    gitignore_anchor = ""

                parser = GitIgnoreToUnisonIgnore(gitignore_anchor)
                with open(gitignore_path, "r") as fh:
                    unison_ignores.extend(parser.parse_gitignore(fh))

        logger.info(
            f"Adding {len(unison_ignores)} ignore patterns based on .gitignore contents"
        )
        cmd_new = build_cmd(cmd_args, unison_ignores)
        run_cmd(cmd_new)
