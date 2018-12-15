from setuptools import setup, find_packages

setup(
    name='pure-protobuf',
    version='0.4.0',
    description=(
        'Python implementation of Protocol Buffer (protobuf) data types'
    ),
    long_description=open('README.markdown').read(),
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
    ],
)
