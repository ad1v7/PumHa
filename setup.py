from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='PumHa',
    version='0.5.1',
    description='Modelling pumas and hares in a landscape',
    long_description=long_description,
    url='https://github.com/ad1v7/PumHa',
    author=['Chloe Sumner', 'Elen Kalda', 'Marcin Kirsz'],
    license='MIT',
    packages=find_packages(),
    package_data={
        'data': ['config.dat',
                'island2.dat',
                'islands.dat'],
    },
    install_requires=[
        'numpy',
        'simplejson',
        'scipy',
        'tqdm'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
