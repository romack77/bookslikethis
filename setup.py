from setuptools import find_packages
from setuptools import setup

setup(
    name='bookslikethis',
    version='1.0.0',
    description='Book recommendations based on tropes.',
    license='MIT',
    keywords='recommendations literature books fiction tropes',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django :: 2.1',
    ],
    install_requires=[],
    dependency_links=[],
    packages=find_packages(exclude=['notebooks']),
    test_suite='bookslikethis',
)
