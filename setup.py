""" freshwater.content Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

NAME = 'freshwater.content'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(
    name=NAME,
    version=VERSION,
    description="An add-on for Plone",
    long_description_content_type="text/x-rst",
    long_description=(
        open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.txt")).read()
    ),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='EEA Add-ons Plone Zope',
    author='Laszlo Cseh',
    author_email='laszlo.cseh@eaudeweb.ro',
    url='https://github.com/eea/freshwater.content',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['freshwater'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'eea.restapi',
        'collective.bookmarks'
    ],
    # -*- Extra requirements: -*-
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
