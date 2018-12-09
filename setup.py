from setuptools import setup, find_packages

setup(
    name='pure-protobuf',
    version='0.4.0',
    description=(
        'Python implementation of Protocol Buffer (protobuf) data types'
    ),
    author='eigenein',
    author_email='eigenein@gmail.com',
    url='https://github.com/eigenein/protobuf',
    packages=find_packages(exclude=['tests']),
    install_requires=['six>=1.11.0,<2.0.0'],
)
