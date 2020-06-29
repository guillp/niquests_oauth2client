from setuptools import setup

__title__ = "requests_oauth2client"
__description__ = "OAuth20 Client for Humans, with Requests Authentication Handlers."
__url__ = "https://github.com/guillp/requests_oauth2client"
__version__ = "0.1.0"
__author__ = "Guillaume Pujol"
__author_email__ = "guill.p.linux@gmail.com"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2020 Guillaume Pujol"

with open("README.rst", "rt") as finput:
    readme = finput.read()

with open("requirements.txt", "rt") as finput:
    requires = [line.strip() for line in finput.readlines()]

with open("requirements-dev.txt", "rt") as finput:
    tests_require = [line.strip() for line in finput.readlines()]

setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=readme,
    long_description_content_type="text/x-rst",
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    packages=["requests_oauth2client"],
    package_data={"": ["LICENSE"]},
    package_dir={"requests": "requests"},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=requires,
    license=__license__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    tests_require=tests_require,
    project_urls={"Source": "https://github.com/guillp/requests_oauth2client", },
)
