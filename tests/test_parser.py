from io import StringIO

import pytest

from unison_gitignore.parser import GitIgnoreToUnisonIgnore, LazyCompiledGitWildMatch


@pytest.fixture
def mock_path():
    return "/home/john_doe"


def test_root_path_removes_slash():
    parsed = GitIgnoreToUnisonIgnore("/").parse_gitignore(StringIO("test.py"))
    assert len(parsed) == 1
    assert parsed[0].anchor_path == ""


def test_keeps_trailing_slash_but_removes_leading_slash():
    parsed = GitIgnoreToUnisonIgnore("/a/b/c/").parse_gitignore(StringIO("test.py"))
    assert len(parsed) == 1
    assert parsed[0].anchor_path == "a/b/c/"


def test_empty_gitignore(mock_path):
    parsed = GitIgnoreToUnisonIgnore(mock_path).parse_gitignore(StringIO())
    assert parsed == []


def test_blank_lines_and_comments(mock_path):
    contents = """
    # test.py # commented out

    """
    parsed = GitIgnoreToUnisonIgnore(mock_path).parse_gitignore(StringIO(contents))
    assert parsed == []


def test_wildcard_and_negation_regex(mock_path):
    contents = """
    *.py[co]
    !test.pyc
    """
    parsed = GitIgnoreToUnisonIgnore(mock_path).parse_gitignore(StringIO(contents))
    assert len(parsed) == 2
    assert str(parsed[0]) == r"-ignore=Regex ^home/john_doe/(.+/)?[^/]*\.py[co](/.*)?$"
    assert str(parsed[1]) == r"-ignorenot=Regex ^home/john_doe/(.+/)?test\.pyc$"


def test_directories_regex(mock_path):
    contents = """
    abc/
    **/x/y
    b/**/c/d
    """
    parsed = GitIgnoreToUnisonIgnore(mock_path).parse_gitignore(StringIO(contents))
    assert len(parsed) == 3
    assert str(parsed[0]) == r"-ignore=Regex ^home/john_doe/(.+/)?abc$"
    assert str(parsed[1]) == r"-ignore=Regex ^home/john_doe/(.+/)?x/y(/.*)?$"
    assert str(parsed[2]) == r"-ignore=Regex ^home/john_doe/b(/.+)?/c/d(/.*)?$"


def test_lazy_match_does_lazy_compilation():
    match = LazyCompiledGitWildMatch(r"test\.py")
    assert not match.is_compiled
    match.regex
    assert match.is_compiled
