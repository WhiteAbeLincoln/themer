from setuptools import setup, find_packages
from os import path
from glob import glob

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='xthemer',
    version='0.1.1',
    description='xorg theming system, centered on base16',
    url='https://github.com/whiteabelincoln/themer',
    author='Abraham White',
    author_email='abelincoln.white@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='wm colorscheme base16 color theme wallpaper',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pyyaml', 'pystache', 'docopt'],
    python_requires='~=3.6',
    data_files=[('/etc/xthemer/templates', glob(path.join(here, 'templates')+'/*'))],
    entry_points={
        'console_scripts': [
            'xthemer=xthemer:main'
        ]
    }
)
