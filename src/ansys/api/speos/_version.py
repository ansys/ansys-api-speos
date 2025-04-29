"""Version of ansys-speos-core module.

On the ``main`` branch, use 'dev0' to denote a development version.
For example:
version_info = 0, 1, 'dev0'
"""

# major, minor, patch
version_info = 0, 15, "1"

# Nice string for the version
__version__ = ".".join(map(str, version_info))

# Defining a version alias for compatibility with other modules
version = __version__