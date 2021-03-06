from setuptools import setup, find_packages
import os
from os import path
from glob import glob


def get_config_home():
    return os.environ.get('XDG_CONFIG_HOME') \
           or path.expandvars("$HOME/.config")

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='xthemer',
    description='xorg theming system, using base16',
    long_description=long_description,
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
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'xdg',
        'pyyaml',
        'pystache',
        'stevedore',
        'termcolor',
        'confuse'
    ],
    python_requires='~=3.6',
    data_files=[
        (
            path.join(get_config_home(), 'xthemer', 'templates'),
            glob(path.join(here, 'data', 'templates', '*'))
        ),
        (
            path.join(get_config_home(), 'xthemer'),
            [path.join(here, 'xthemer', 'config_default.yaml')]
        )
    ],
    entry_points={
        'console_scripts': [
            'xthemer=xthemer:main'
        ],
        'xthemer.effects': [
            'xresources = xthemer.plugin:Xresources',
            'bash_colors = xthemer.plugin:BashColors',
            'shell = xthemer.plugin:Shell',
            'termite = xthemer.plugin:Termite',
            'dunst = xthemer.plugin:Dunst',
            'vim = xthemer.plugin:Vim',
            'emacs = xthemer.plugin:Emacs',
            'wallpaper = xthemer.plugin:Wallpaper',
            'rofi = xthemer.plugin:Rofi',
            'current = xthemer.plugin:CurrentTheme',
            'template = xthemer.plugin:Template'
        ]
    }
)
