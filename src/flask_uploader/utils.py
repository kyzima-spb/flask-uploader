from __future__ import annotations
import hashlib
import os
import typing as t


__all__ = (
    'get_extension',
    'increment_path',
    'md5file',
    'md5stream',
    'split_pairs',
)


def get_extension(filename: str) -> str:
    """
    Returns the file extension.

    '天安门.jpg'
    """
    _, ext = os.path.splitext(filename)
    return ext


def increment_path(path_pattern: str) -> str:
    """
    Finds the next free path in an sequentially named list of files.
    Author of this solution `James`_.

    Runs in log(n) time where n is the number of existing files in sequence.

    Arguments:
        path_pattern (str):
            e.g. 'file-%s.txt'

    .. _`James`: https://stackoverflow.com/a/47087513/10509709
    """
    i = 1

    # First do an exponential search
    while os.path.exists(path_pattern % i):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)

    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b


def md5file(filename: str) -> str:
    """Returns the hash sum of the contents of the given file."""
    with open(filename, 'rb') as f:
        return md5stream(f)


def md5stream(stream: t.BinaryIO, buffer_size: int = 16384) -> str:
    """
    Returns the hash sum of a binary data stream.

    Arguments:
        stream (bytes):
            Binary data stream.
        buffer_size (int):
            The buffer size is the number of bytes held in memory during the hash process.
            Default to 16Kb.
    """
    hash_md5 = hashlib.md5()

    for chunk in iter(lambda: stream.read(buffer_size), b''):
        hash_md5.update(chunk)

    stream.seek(0)

    return hash_md5.hexdigest()


def split_pairs(
    hash_sum: str,
    step: int = 2,
    max_split: int = 3,
) -> list[str]:
    """
    Splits the hash sum string into parts of the specified length.

    Arguments:
        step (int): cutting step. Default to ``2``.
        max_split (int): Maximum number of splits to do. Default to ``3``.
    """
    end = step * (max_split - 1) if max_split else len(hash_sum)
    pairs = []

    for start in range(0, end, step):
        pairs.append(hash_sum[start:start + step])

    pairs.append(hash_sum[end:])

    return pairs
