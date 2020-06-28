import pytest
from unittest import mock

from unison_gitignore.main import main


@pytest.fixture
def cmd():
    return [
        "unison_gitignore",
        "local_root",
        "ssh://remote_root",
        "-path",
        "path1",
        "-prefer",
        "root1",
    ]


@pytest.fixture
def cwd():
    return "/home/john_doe"


@pytest.fixture
def mock_collect_gitignores():
    def generator(abs_path):
        yield f"{abs_path}/stuff/data", f"{abs_path}/stuff/data/.gitignore"

    with mock.patch("unison_gitignore.main.collect_gitignores_from_path") as m:
        m.side_effect = generator
        yield m


@pytest.fixture
def mock_run_cmd():
    with mock.patch("unison_gitignore.main.run_cmd") as m:
        yield m


@pytest.fixture
def mock_files():
    with mock.patch(
        "builtins.open", mock.mock_open(read_data=mock_gitignore_contents)
    ) as mock_file:
        yield mock_file


mock_gitignore_as_array = [
    "*.py[co]",
]

mock_gitignore_contents = "\n".join(mock_gitignore_as_array)


@pytest.mark.usefixtures("mock_collect_gitignores", "mock_files")
def test_calls_run_cmd(cmd, cwd, mock_run_cmd):
    main(cmd, cwd)
    mock_run_cmd.assert_called_once()


def test_no_args_calls_run_cmd(cwd, mock_run_cmd):
    main(["unison_gitignore"], cwd)
    mock_run_cmd.assert_called_once()
    args = mock_run_cmd.call_args[0][0]
    assert args == ["unison"]


@pytest.mark.usefixtures("mock_collect_gitignores", "mock_files")
def test_calls_run_cmd_with_regex_patterns(cmd, cwd, mock_run_cmd):
    main(cmd, cwd)
    args = mock_run_cmd.call_args[0][0]
    assert args[0] == "unison"
    assert args[1:7] == cmd[1:7]
    assert len(args) == len(cmd) + len(mock_gitignore_as_array)

    for arg in args[7:]:
        assert arg.startswith("-ignore=")


@pytest.mark.usefixtures("mock_collect_gitignores", "mock_files")
@pytest.mark.parametrize(
    "cmd",
    [
        # Local ambiguity
        ["unison_gitignore", "local1", "local2", "-path", "path"],
        # Profile
        ["unison_gitignore", "my_profile", "-path", "path"],
    ],
)
def test_does_not_add_patterns_when_unable_to(cmd, cwd, mock_run_cmd):
    main(cmd, cwd)
    mock_run_cmd.assert_called_once()
    args = mock_run_cmd.call_args[0][0]
    assert args[0] == "unison"
    assert len(args) == len(cmd)
    assert args[1:] == cmd[1:]


@pytest.mark.usefixtures("mock_collect_gitignores", "mock_files")
def test_when_no_path_given_it_uses_local_root(cwd, mock_run_cmd):
    cmd = ["unison_gitignore", "/home/john_doe", "ssh://remote/john_doe_data"]
    main(cmd, cwd)
    mock_run_cmd.assert_called_once()
    args = mock_run_cmd.call_args[0][0]
    assert args[0] == "unison"
    assert args[1:3] == cmd[1:3]
    assert len(args) == 4
    assert args[3] == "-ignore=Regex ^stuff/data/(.+/)?[^/]*\\.py[co](/.*)?$"


@pytest.mark.usefixtures("mock_files")
def test_gitignore_in_root(cmd, cwd, mock_run_cmd):
    def generator(abs_path):
        yield f"{abs_path}", f"{abs_path}.gitignore"

    with mock.patch("unison_gitignore.main.collect_gitignores_from_path") as m:
        m.side_effect = generator
        main(cmd, cwd)
    mock_run_cmd.assert_called_once()
    args = mock_run_cmd.call_args[0][0]
    assert args[0] == "unison"
    assert args[1:7] == cmd[1:7]
    assert len(args) == 8
    assert args[7] == "-ignore=Regex ^(.+/)?[^/]*\\.py[co](/.*)?$"
