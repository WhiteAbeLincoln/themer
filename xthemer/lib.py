#!/usr/bin/env python3
"""Usage:
  xthemer [-m MODULE...] [-q | -v...] [-j | -y] THEME
  xthemer [-m MODULE...] [-q | -v...] (-j | -y) [-]
  xthemer --help | --version

Arguments:
  THEME  theme file or directory

Options:
  -h --help           show this
  -p --plugin PLUGIN  theme plugin to run
  -j --json           file is in json format
  -y --yaml           file is in yaml format
  -q --quiet          show less text
  -v --verbose        show more text
"""
import sys
import os
import xdg
import os.path as path
import argparse
from stevedore import NamedExtensionManager
from termcolor import colored
from xthemer import __version__
from yaml import YAMLError
from json import JSONDecodeError
import confuse
import logging
from typing import List, Dict, Any, Optional, Union, TextIO

# set up a convenience aliases
Maybe = Optional
Colors = Dict[str, Union[str, float]]

GLOBAL_DIR = "/etc/xthemer"
GLOBAL_CONFIG_PATH = GLOBAL_DIR + "/config.yaml"
GLOBAL_TEMPLATE_DIR = GLOBAL_DIR + "/templates"

config = confuse.Configuration('xthemer', __name__)
logger = logging.getLogger('xthemer')


# main :: IO()
def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply base16 theme to X")
    parser.add_argument("--version", action="version", version="%(prog)s " +
                                                               __version__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true",
                       help="don't produce any output text")
    group.add_argument("-v", "--verbose", action="count", default=0,
                       help="increase output verbosity")
    parser.add_argument("-p", "--plugins", nargs="*",
                        help="theme plugins to run")
    parser.add_argument("theme", nargs="?", type=argparse.FileType(),
                        default=sys.stdin, help="theme file")

    args = parser.parse_args(argv)
    config.set_args(args)

    logger = config_logger(args)

    dir_check()

    colors = read_colors(args.theme)
    if colors is None:
        raise Exception("Colors couldn't be parsed")

    mgr = load_modules(config["plugins"].get())

    def run_module(e, colors, directory):
        logger.info("Running plugin %s", cg(e.name))
        plugin = e.plugin(e.name, colors, directory)
        plugin.run()

    mgr.map(run_module, colors, os.path.dirname(args.theme.name))

    if not args.quiet:
        print(colored("Applied theme: " +
                      colored(f"{args.theme.name}", "blue")
                      , "green"))

    return 0


def load_modules(names: str) -> NamedExtensionManager:
    return NamedExtensionManager(
        namespace="xthemer.effects",
        names=names,
        name_order=True,
        invoke_on_load=False,
        propagate_map_exceptions=True,
        on_missing_entrypoints_callback=
        lambda p: logger.warning("plugin %s not found", cg(p)),
        on_load_failure_callback=
        lambda m, e, ex: logger.warning("plugin %s failed to load", cg(e.name))
    )


def config_logger(args: Any) -> logging.Logger:
    if args.verbose > 1:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    log = logging.getLogger('xthemer')
    log.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    log.addHandler(ch)
    return log


def dir_check() -> None:
    local_config_path = path.join(get_config_home(), "templates")
    logger.debug("checking for templates in %s and %s",
                 cb(local_config_path), cb(GLOBAL_TEMPLATE_DIR))
    if not path.isdir(local_config_path) and not path.isdir(GLOBAL_TEMPLATE_DIR):
        os.makedirs(path.join(local_config_path, "templates"))
        logger.warning("no templates found")


def read_colors(file: TextIO) -> Maybe[Dict[str, Any]]:
    import yaml
    import json

    try:
        out = yaml.load(file)
    except YAMLError:
        logger.debug("Unable to decode file %s using yaml", cb(file.name))
        out = json.load(file)
    except JSONDecodeError:
        logger.debug("Unable to decode file %s using json", cb(file.name))
        logger.critical("Unable to parse color file")
        out = None

    if isinstance(out, list):
        return merge_dict(convert_color_format(out))
    elif out is not None:
        return merge_dict(out)
    else:
        return None


def convert_color_format(colors: List[str]) -> Dict[str, str]:
    return {
        "scheme-name": "",
        "scheme-author": "",
        "base00": colors[0],
        "base01": colors[1],
        "base02": colors[2],
        "base03": colors[3],
        "base04": colors[4],
        "base05": colors[5],
        "base06": colors[6],
        "base07": colors[7],
        "base08": colors[8],
        "base09": colors[9],
        "base0A": colors[10],
        "base0B": colors[11],
        "base0C": colors[12],
        "base0D": colors[13],
        "base0E": colors[14],
        "base0F": colors[15],
    }


def generate_colors(colors: Dict[str, str]) -> Colors:
    out = {}
    for key, val in colors.items():
        val = val.lower()
        if "base0" not in key:
            continue
        r = val[:2]
        g = val[2:4]
        b = val[4:]
        out[f"{key}-hex"] = val
        out[f"{key}-hex-r"] = r
        out[f"{key}-hex-g"] = g
        out[f"{key}-hex-b"] = b
        out[f"{key}-rgb-r"] = int("0x" + r, 16)
        out[f"{key}-rgb-g"] = int("0x" + g, 16)
        out[f"{key}-rgb-b"] = int("0x" + b, 16)
        out[f"{key}-dec-r"] = int("0x" + r, 16) / 255
        out[f"{key}-dec-g"] = int("0x" + g, 16) / 255
        out[f"{key}-dec-b"] = int("0x" + b, 16) / 255
    return out


def merge_dict(colors: Dict[str, str]) -> Colors:
    return {**{"scheme-name": "base16-custom", "scheme-author": ""},
            **generate_colors(colors),
            **{"scheme-slug": "custom"}}


def get_config_home() -> str:
    return config.config_dir()


def get_data_home() -> str:
    return path.join(xdg.XDG_DATA_HOME, "xthemer")


def cb(s):
    """
    Colors a string in blue
    :param s: string to color
    :return: colored string
    """
    return colored(s, "blue")


def cg(s):
    """
    Colors a string in green
    :param s: string to color
    :return: colored string
    """
    return colored(s, "green")


def get_template(name) -> Maybe[str]:
    logger.debug("getting template %s", cg(name))
    lpath = path.join(get_config_home(), "templates")

    if path.isfile(path.join(lpath, f"{name}.mustache")):
        logger.debug("found template %s in %s", cg(name), cb(lpath))

        with open(path.join(lpath, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    elif path.isfile(path.join(GLOBAL_TEMPLATE_DIR, f"{name}.mustache")):
        logger.debug("found template %s in %s", cg(name),
                     cb(GLOBAL_TEMPLATE_DIR))

        with open(path.join(GLOBAL_TEMPLATE_DIR, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    else:
        logger.error("Template %s not found", cg(name))
        return None


def render_template(name: str, colors: Colors) -> Maybe[str]:
    template = get_template(name)
    if template is not None:
        import pystache
        data = pystache.render(template, colors)
        logger.debug("rendered template %s", cg(name))
        logger.debug("template output:\n%s", data)
        return data
    return None


if __name__ == "__main__":
    sys.exit(main())
