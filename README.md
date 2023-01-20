### ansys-api-speos gRPC Interface Package

This Python package contains the auto-generated gRPC Python interface files for
Speos.


#### Installation

Provided that these wheels have been published to public PyPI, they can be
installed with:

```
pip install ansys-api-speos
```

#### Build

To build the gRPC packages, run:

```
pip install build
python -m build
```

This will create both the source distribution containing just the protofiles
along with the wheel containing the protofiles and build Python interface
files.


#### Manual Deployment

After building the packages, manually deploy them with:

```
pip install twine
twine upload dist/*
```

Note that this is automatically done through CI/CD.

#### Automatic Deployment

This repository contains GitHub CI/CD that enables the automatic building of
source and wheel packages for these gRPC Python interface files. By default,
these are built on PRs, the main branch, and on tags when pushing. Artifacts
are uploaded for each PR.

To publicly release wheels to PyPI, ensure your branch is up-to-date and then
push tags. For example, for the version ``v0.5.0``.

```bash
git tag v0.5.0
git push --tags
```
