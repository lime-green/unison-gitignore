## Unison Gitignore
[![PyPI version](https://badge.fury.io/py/unison-gitignore.svg)](https://badge.fury.io/py/unison-gitignore)

A gitignore-aware wrapper around [Unison](https://github.com/bcpierce00/unison)

`unison-gitignore` will walk the local root and any supplied paths finding gitignore files and then call
`unison` with the appropriate unison ignore patterns

## Usage
First install it:
```bash
pip install unison-gitignore
```

Then use:
```bash
unison-gitignore /home/john_doe/local_root ssh://remote_root/ -path data
```
It accepts the exact same arguments as `unison`

## Caveats
- Will not add patterns when using two local roots:

    Unison does the match without the root attached, so a .gitignore file
    in either root would apply to both local roots
- Will not add patterns when profile usage method is used
- Does not handle `!pattern` in the same way as git does:

    ```
    b/
    !b/c/test.py
    ```
    `test.py` will not be ignored in git, but will be ignored by `unison`

    The [Unison reference](https://www.cis.upenn.edu/~bcpierce/unison/download/releases/stable/unison-manual.html#reference)
    says this:
    > Unison starts detecting updates from the root of the replicas—i.e., from the empty path. If the empty path matches an ignore pattern and does not match an ignorenot pattern, then the whole replica will be ignored. (For this reason, it is not a good idea to include Name * as an ignore pattern. If you want to ignore everything except a certain set of files, use Name ?*.)

    > If the root is a directory, Unison continues looking for updates in all the immediate children of the root. Again, if the name of some child matches an ignore pattern and does not match an ignorenot pattern, then this whole path including everything below it will be ignored.

    > If any of the non-ignored children are directories, then the process continues recursively.

    So any negated files or directories that are not direct children of an ignored directory will be ignored improperly.
