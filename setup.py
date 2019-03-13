from setuptools import find_packages, setup

setup(
    name='pure-protobuf',
    version='0.5.0',
    description='Python implementation of Protocol Buffers data types',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Pavel Perestoronin',
    author_email='eigenein@gmail.com',
    url='https://github.com/eigenein/protobuf',
    packages=find_packages(exclude=['tests']),
    install_requires=[],
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
