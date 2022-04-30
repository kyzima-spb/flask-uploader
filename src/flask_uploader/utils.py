from __future__ import annotations
import hashlib
import typing as t


__all__ = ('md5file', 'md5stream', 'split_pairs')


def md5file(filename: str) -> str:
    """Returns the hash sum of the contents of the given file."""
    with open(filename, 'rb') as f:
        return md5stream(f)


def md5stream(stream: t.BinaryIO) -> str:
    """Returns the hash sum of a binary data stream."""
    hash_md5 = hashlib.md5()

    for chunk in iter(lambda: stream.read(4096), b''):
        hash_md5.update(chunk)

    stream.seek(0)

    return hash_md5.hexdigest()


def split_pairs(
    hash_sum: str,
    pair_length: int = 2,
    max_pairs: t.Optional[int] = None
) -> list[str]:
    """
    Splits the hash sum string into parts of the specified length.

    Used to generate file paths for distributed storage of files on disk.
    """
    end = pair_length * (max_pairs - 1) if max_pairs else len(hash_sum)
    pairs = []

    for start in range(0, end, pair_length):
        pairs.append(hash_sum[start:start + pair_length])

    pairs.append(hash_sum[end:])

    return pairs
