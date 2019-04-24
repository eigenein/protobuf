from setuptools import find_packages, setup

setup(
    name='pure-protobuf',
    version='1.1.0',
    description='Python implementation of Protocol Buffers data types with dataclasses support',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Pavel Perestoronin',
    author_email='eigenein@gmail.com',
    url='https://github.com/eigenein/protobuf',
    packages=find_packages(exclude=['tests']),
    zip_safe=True,
    install_requires=[
        'dataclasses>=0.6,<1.0; python_version >= "3.6" and python_version < "3.7"',
    ],
    extras_require={
        'dev': ['flake8', 'isort', 'pytest', 'pytest-cov', 'coveralls'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
)
