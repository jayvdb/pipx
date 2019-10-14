import os
import sys

import nox  # type: ignore
from pathlib import Path

# NOTE: these tests require nox to create virtual environments
# with venv. nox currently uses virtualenv. pipx
# uses a fork of nox at https://github.com/cs01/nox
# on the branch cs01/use-venv
# To invoke nox for pipx, use:
# pipx run --spec=git+https://github.com/cs01/nox.git@2ba8984a nox
# until this is fixed in nox. See
# https://github.com/theacodes/nox/issues/199


travis_python_version = os.environ.get("TRAVIS_PYTHON_VERSION")
if travis_python_version:
    python = [travis_python_version]
else:
    python = ["3.6", "3.7"]

nox.options.sessions = ["unittests", "lint"]
# docs fail on Windows, even if `chcp.com 65001` is used
if sys.platform != "win32":
    nox.options.sessions.append("docs")


doc_dependencies = [".", "jinja2", "mkdocs", "mkdocs-material"]
lint_dependencies = ["black", "flake8", "mypy", "check-manifest"]


@nox.session(python=python)
def unittests(session):
    session.install(".")
    session.run("python", "-m", "unittest", "discover")


@nox.session(python=python)
def lint(session):
    session.install(*lint_dependencies)
    files = ["pipx", "tests"] + [str(p) for p in Path(".").glob("*.py")]
    session.run("black", "--check", *files)
    session.run("flake8", *files)
    session.run("mypy", *files)
    session.run("check-manifest")
    session.run("python", "setup.py", "check", "--metadata", "--strict")


@nox.session(python=python)
def docs(session):
    session.install(*doc_dependencies)
    session.run("python", "generate_docs.py")
    session.run("mkdocs", "build")


@nox.session(python=python)
def develop(session):
    session.install(*doc_dependencies, *lint_dependencies)
    session.install("-e", ".")


@nox.session(python=["3.7"])
def build(session):
    session.install("setuptools")
    session.install("wheel")
    session.install("twine")
    session.run("rm", "-rf", "dist", external=True)
    session.run("python", "setup.py", "--quiet", "sdist", "bdist_wheel")


@nox.session(python=["3.7"])
def publish(session):
    build(session)
    print("REMINDER: Has the changelog been updated?")
    session.run("python", "-m", "twine", "upload", "dist/*")


@nox.session(python=["3.7"])
def watch_docs(session):
    session.install(*doc_dependencies)
    session.run("mkdocs", "serve")


@nox.session(python=["3.7"])
def publish_docs(session):
    session.install(*doc_dependencies)
    session.run("python", "generate_docs.py")
    session.run("mkdocs", "gh-deploy")
