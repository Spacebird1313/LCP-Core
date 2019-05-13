from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'waitress',
    'pysimplegui'
]

setup(
    name='LCP',
    version='0.1',
    author='iMagineLab',
    url='https://imaginelab.club',
    install_requires=requires
)
