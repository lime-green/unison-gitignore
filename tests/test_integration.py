import subprocess


def test_basic_command_completes_successully():
    p = subprocess.run(
        ["unison_gitignore", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert p.stdout
    assert p.returncode == 0, p.stderr
