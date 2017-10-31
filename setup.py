from setuptools import setup, find_packages
from codecs import open
from os import path


# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
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
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    package_data={
        'data': ['config.dat',
                'island2.dat',
                'islands.dat'],
    },
    install_requires=[
        'numpy>=1.9.2',
        'simplejson>=3.8.1',
        'scipy>=0.15.1',
        'tqdm>=4.19.4',
        'jsonschema>=2.6.0'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        'console_scripts': ['pumha=pumha.run_sim:main']
    }
)
