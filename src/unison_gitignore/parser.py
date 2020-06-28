#!/usr/bin/env python

import pathspec
import re


class GitIgnoreToUnisonIgnore:
    """
    Class for converting a .gitignore file to unison sync ignore patterns

    The anchor path is the gitignore directory path relative to either:
        - a path, supplied via the "-path" option
        - the local root, when no "-path" is supplied
    """

    def __init__(self, anchor_path):
        self.anchor_path = anchor_path
        if not self.anchor_path.endswith("/"):
            self.anchor_path += "/"
        if self.anchor_path.startswith("/"):
            self.anchor_path = self.anchor_path[1:]

    def parse_gitignore(self, gitignore):
        spec = pathspec.PathSpec.from_lines(
            LazyCompiledGitWildMatch, gitignore.readlines()
        )
        return [
            UnisonPathIgnore.from_pattern(self.anchor_path, pattern)
            for pattern in spec.patterns
            if not pattern.is_null
        ]


class LazyCompiledGitWildMatch(pathspec.patterns.GitWildMatchPattern):
    def __init__(self, pattern, include=None):
        self.regex_s = None

        if isinstance(pattern, str):
            assert (
                include is None
            ), "include:{!r} must be null when pattern:{!r} is a string.".format(
                include, pattern
            )
            regex_s, include = self.pattern_to_regex(pattern)
            self.regex_s = regex_s
        elif pattern is not None and hasattr(pattern, "match"):
            self._regex = pattern
            self.regex_s = pattern.pattern
        elif pattern is None:
            assert (
                include is None
            ), "include:{!r} must be null when pattern:{!r} is null.".format(
                include, pattern
            )
        else:
            raise TypeError(
                "pattern:{!r} is not a string, RegexObject, or None.".format(pattern)
            )

        self.include = include

    @property
    def is_null(self):
        return self.include is None and self.regex_s is None

    @property
    def regex(self):
        if not self.is_compiled:
            self._regex = None
            if self.regex_s:
                self._regex = re.compile(self.regex_s)
        return self._regex

    @property
    def is_compiled(self):
        return hasattr(self, "_regex")


class UnisonPathIgnore:
    NON_CAPTURE_GROUP_REMOVAL_REGEX = re.compile(r"\?:")

    def __init__(self, anchor_path, regex, include):
        self.anchor_path = anchor_path
        self.raw_regex = regex
        self.include = include

    @classmethod
    def from_pattern(cls, anchor_path, pattern):
        return cls(anchor_path, pattern.regex_s, pattern.include)

    @property
    def regex(self):
        regex = self.raw_regex
        if regex.startswith("^"):
            regex = regex[1:]
        regex = re.sub(self.NON_CAPTURE_GROUP_REMOVAL_REGEX, "", regex)
        # Remove the trailing slash wildcard, unison won't match the slash
        regex = regex.replace("/.*$", "$")
        return f"^{self.anchor_path}{regex}"

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f" anchor_path={self.anchor_path}"
            f" raw_regex={self.raw_regex}"
            f" include={self.include}>"
        )

    def __str__(self):
        s = "-ignore" if self.include else "-ignorenot"
        return f"{s}=Regex {self.regex}"
