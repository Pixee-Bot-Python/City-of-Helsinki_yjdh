import os

from setuptools import find_packages, setup

from shared import __version__

#
# with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
#     README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="yjdh_backend_shared",
    version=__version__,
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    license="MIT License",
    description="YJDH backend shared component",
    url="https://github.com/City-of-Helsinki/yjdh",
    author="City of Helsinki",
    author_email="dev@hel.fi",
    install_requires=[
        "Django",
        "mozilla_django_oidc",
        "django_auth_adfs",
        "django-extensions",
        "djangosaml2",
        "security==1.3.1",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-django"],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
