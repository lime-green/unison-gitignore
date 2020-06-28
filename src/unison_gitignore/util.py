import logging
import os


log_level = os.environ.get("UNISON_GITIGNORE_LOG_LEVEL", "WARN")
logger = logging.getLogger("unison_gitignore")
logger.setLevel(getattr(logging, log_level))
logFormatter = logging.Formatter(fmt="%(name)s :: %(levelname)-8s :: %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(logFormatter)
logger.addHandler(handler)

GIT_IGNORE = ".gitignore"


def build_cmd(cmd, unison_ignores):
    new_cmd = ["unison"] + cmd
    for unison_ignore in unison_ignores:
        new_cmd.append(str(unison_ignore))
    return new_cmd


def _is_ssh_root(root):
    return root.startswith("ssh://")


def collect_paths_from_cmd(cmd, cwd):
    if len(cmd) < 2:
        return

    if cmd[1].startswith("-"):
        # In the case of running using a profile
        logger.warning(
            "No .gitignore patterns will be added since a unison profile was given"
        )
        return

    roots = cmd[0:2]
    if not _is_ssh_root(roots[0]) and not _is_ssh_root(roots[1]):
        # Since unison matches the patterns against the path
        # and not the root, we can't add ignore rules when two local
        # paths are being synced, since they would match against both roots
        logger.warning(
            "No .gitignore patterns will be added since no remote roots were given"
        )
        return

    if _is_ssh_root(roots[0]):
        _, local_root = roots
    else:
        local_root, _ = roots

    has_path = False
    for i, token in enumerate(cmd):
        if token == "-path" and i < len(cmd):
            has_path = True
            path = cmd[i + 1]
            abs_path = os.path.join(cwd, local_root, path)
            yield abs_path, path

    if not has_path:
        abs_path = os.path.join(cwd, local_root)
        yield abs_path, ""


def collect_gitignores_from_path(path):
    for root, _, files in os.walk(path):
        if GIT_IGNORE in files:
            yield root, os.path.join(root, GIT_IGNORE)


def run_cmd(cmd):
    logger.debug(f"Running: {cmd}")
    os.execvp(cmd[0], cmd)
