# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Installation file for the ansys-api-speos package"""

import os
from datetime import datetime

import setuptools

from ansys.tools.protoc_helper import CMDCLASS_OVERRIDE

# Get the long description from the README file
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

product = "speos"
library = ""
package_info = ["ansys", "api", product, library, ""]
with open(os.path.join(HERE, "src", "ansys", "api", product, library, "_version.py"), encoding="utf-8") as f:
    # Parse the version from the _version.py file
    version_file_vars = {}
    exec(f.read(), version_file_vars)
    version = version_file_vars["__version__"]

package_name = "ansys-api-speos"
dot_package_name = '.'.join(filter(None, package_info))

description = f"Autogenerated python gRPC interface package for {package_name}, built on {datetime.now().strftime('%H:%M:%S on %d %B %Y')}"

if __name__ == "__main__":
    setuptools.setup(
        name=package_name,
        version=version,
        author="ANSYS, Inc.",
        author_email="pyansys.core@ansys.com",
        description=description,
        long_description=long_description,
        long_description_content_type='text/markdown',
        url=f"https://github.com/ansys/{package_name}",
        license="MIT",
        python_requires=">=3.10",
        install_requires=["grpcio~=1.48", "protobuf>=3.20,<6"],
        package_dir = {"": "src"},
        packages=setuptools.find_namespace_packages("src", include=("ansys.*",)),
        package_data={
            "": ["*.proto", "*.pyi", "py.typed", "_version.py"],
        },
        entry_points={
            "ansys.tools.protoc_helper.proto_provider": [
                f"{dot_package_name}={dot_package_name}"
            ],
        },
        cmdclass=CMDCLASS_OVERRIDE,
        project_urls={
            "Documentation": "https://github.com/ansys/ansys-api-speos/#readme",
            "Source": "https://github.com/ansys/ansys-api-speos/",
            "Tracker": "https://github.com/ansys/ansys-api-speos/issues/",
        },
    )
