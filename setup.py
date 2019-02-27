import os

from setuptools import setup, find_packages

README=""
CHANGES=""

requires = []

setup(name="frameapp",
      version="1.0",
      description="Flask demostration frame app",
      long_description=README + "\n\n" + CHANGES,
      classifiers=[],
      author="Nathan Harrington",
      author_email="harrington.nathan@gmail.com",
      url="",
      keywords="",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite="app",
      install_requires=requires,
      )
