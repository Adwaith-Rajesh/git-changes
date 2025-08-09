from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path


GIT_DIR = Path('.git')
GIT_COMMIT_MSG_FILE = GIT_DIR / 'current_message.txt'
GIT_COMMIT_MSG_FILE_BK = GIT_DIR / 'current_message.txt.bk'
GIT_POST_COMMIT_FILE = GIT_DIR / 'hooks/post-commit'

COMMIT_TYPES = [
    'feat',
    'fix',
    'docs',
    'style',
    'refactor',
    'perf',
    'test',
    'build',
    'ci',
    'chore',
    'revert',
]


def _write_post_commit_file() -> None:
    with open(GIT_POST_COMMIT_FILE, 'w') as f:
        f.write('#!/bin/env bash\ngitc --reset')

    os.chmod(GIT_POST_COMMIT_FILE, os.stat(GIT_POST_COMMIT_FILE).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _init() -> None:
    GIT_COMMIT_MSG_FILE.touch()
    _write_post_commit_file()


def _add_msg_to_file(message: str, type: str) -> str:
    msg = f'[{type}] {message}'
    with open(GIT_COMMIT_MSG_FILE, 'a') as f:
        f.write(f'{msg}\n')

    return msg


def _print_commit_msg() -> None:
    with open(GIT_COMMIT_MSG_FILE, 'r') as f:
        print(f.read().strip() or 'No commit messages yet!.. To add new message run\ngitc <message> [--type]')


def _reset_commit_msg_file() -> None:
    GIT_COMMIT_MSG_FILE.write_text('')


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument('message', help='message for the change', nargs='?')

    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('--type', choices=COMMIT_TYPES, default='feat', help='The type of the change')
    grp.add_argument('--init', action='store_true', help='Initialize everything')
    grp.add_argument('--show-msg', action='store_true', help='Show the current commit message')
    grp.add_argument('--reset', action='store_true', help='reset commit messages')

    args = parser.parse_args()

    if not GIT_DIR.exists() or not GIT_DIR.is_dir():
        print('error: not a git repository', file=sys.stderr)
        return 1

    if args.init:
        _init()
        os.execvp('git', ('git', 'config', '--local', 'commit.template', GIT_COMMIT_MSG_FILE))

    if args.show_msg:
        _print_commit_msg()
        return 0

    if args.reset:
        _reset_commit_msg_file()
        return 0

    _init()

    if args.message:
        print(_add_msg_to_file(args.message, args.type))

    return 0
