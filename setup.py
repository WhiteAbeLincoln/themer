from setuptools import setup, find_packages
from os import path
from glob import glob

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
    install_requires=['pyyaml', 'pystache', 'docopt', 'stevedore', 'termcolor'],
    python_requires='~=3.6',
    data_files=[('/etc/xthemer/templates',
                 glob(path.join(here, 'data', 'templates', '*')))
                , ('/etc/xthemer', [path.join(here, 'data', 'config.yaml')])
                ],
    entry_points={
        'console_scripts': [
            'xthemer=xthemer:main'
        ],
        'xthemer.effects': [
            'xresources = xthemer.plugin:Xresources',
            'bash = xthemer.plugin:Bash',
            'termite = xthemer.plugin:Termite',
            'dunst = xthemer.plugin:Dunst',
            'vim = xthemer.plugin:Vim',
            'emacs = xthemer.plugin:Emacs',
            'wallpaper = xthemer.plugin:Wallpaper',
            'rofi = xthemer.plugin:Rofi',
            'rxbar = xthemer.plugin:RxBar',
            'current = xthemer.plugin:CurrentTheme',
        ]
    }
)
