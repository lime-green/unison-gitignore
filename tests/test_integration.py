import subprocess


def test_basic_command_completes_successully():
    # Since unison won't exist on CI
    subprocess.run(["alias", "unison=echo"])
    p = subprocess.run(
        ["unison_gitignore", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert p.stdout
    assert p.returncode == 0, p.stderr
