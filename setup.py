import os

from setuptools import setup

VERSION = "2024.10"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="crispy-bootstrap4",
    description="Bootstrap4 template pack for django-crispy-forms",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="David Smith",
    url="https://github.com/django-crispy-forms/crispy-bootstrap4",
    project_urls={
        "Issues": "https://github.com/django-crispy-forms/crispy-bootstrap4/issues",
        "CI": "https://github.com/django-crispy-forms/crispy-bootstrap4/actions",
        "Changelog": (
            "https://github.com/django-crispy-forms/crispy-bootstrap4/releases"
        ),
    },
    license="MIT",
    version=VERSION,
    packages=["crispy_bootstrap4"],
    install_requires=["django-crispy-forms>=2.3", "django>=4.2"],
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
