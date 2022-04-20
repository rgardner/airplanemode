"""Airplane Mode tests."""

import airplanemode


def test_version():
    """Verifies __version__ constant exists and is nonempty."""
    assert bool(airplanemode.__version__)
