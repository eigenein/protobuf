from setuptools import find_packages, setup

setup(
    name='pure-protobuf',
    version='2.1.1',
    description="Implementation of Protocol Buffers with dataclass-based schemaʼs",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Pavel Perestoronin',
    author_email='eigenein@gmail.com',
    url='https://github.com/eigenein/protobuf',
    packages=find_packages(exclude=['tests*']),
    zip_safe=True,
    extras_require={
        'dev': [
            'flake8',
            'isort',
            'mypy',
            'pytest',
            'coveralls',
            'build',
            'twine',
            'pytest-benchmark',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        'Changelog': 'https://github.com/eigenein/protobuf/blob/master/CHANGELOG.md',
    },
)
