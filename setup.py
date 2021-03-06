# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from os import listdir

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

s111_scripts = ["scripts/" + item for item in listdir("scripts")]
        
setup(
    name='chs_s111',
    version='1.0.0.dev2', 
    description='CHS S-111 tools',   
    long_description=long_description,    
    url='https://github.com/caris/chs-s111',
    author='CARIS',
    author_email='github@caris.com',
    license='BSD 2-Clause',
    packages=find_packages(),
    scripts=s111_scripts,
    install_requires=['pytz', 'iso8601', 'numpy', 'h5py', 'netcdf4'],
    classifiers=[
                   "Development Status :: 3 - Alpha",
                   "Environment :: Console",        
                   "Intended Audience :: Science/Research",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "License :: OSI Approved :: BSD 2-Clause License",
                   "Programming Language :: Python :: 3"]
)