#!/usr/bin/env python3
"""Usage:
  xthemer [-m MODULE...] [-q | -v...] [-f] THEME
  xthemer [-m MODULE...] [-q | -v...] (-j | -y) [-]
  xthemer --help | --version

Arguments:
  THEME  theme directory

Options:
  -h --help           show this
  -m --module MODULE  theme module
  -f --file           indicates theme is a file, not directory
  -j --json           stdin is in json format
  -y --yaml           stdin is in yaml format
  -q --quiet          show less text
  -v --verbose        show more text
"""
import sys
import os
import json
import os.path as path
from docopt import docopt
from stevedore import NamedExtensionManager
from termcolor import colored
from functools import reduce
from xthemer import __version__
from yaml import YAMLError
from json import JSONDecodeError

options = {
    "verbose": 0,
    "quiet": False
}

modules = [
    "xresources",
    "bash",
    "vim",
    "wallpaper",
    "current"
]


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = docopt(__doc__, argv=argv, version=__version__)

    dir_check()

    if args["THEME"] and\
            (not path.isdir(args["THEME"]) or not path.isfile(args["THEME"])):
        print(f"ERROR: theme {args['THEME']} does not exist")
        return 66

    options["verbose"] = args["--verbose"]
    options["quiet"] = args["--quiet"]
    try:
        colors = read_colors(args)
    except YAMLError or JSONDecodeError:
        raise Exception("Error parsing colors")
        return -1

    config = load_config()

    modulelist = list(map(comma_to_array, args["--module"]))
    newmodules = reduce(lambda x, y: x + y, modulelist, [])
    if newmodules:
        config["modules"] = newmodules

    mgr = load_modules(config["modules"], colors, args["THEME"])

    def run_module(e):
        vprint(f"Running module {e.name}")
        e.obj.run()

    mgr.map(run_module)

    if not options["quiet"]:
        print(colored("Applied theme: " +
                      colored(f"{args['THEME']}", 'blue')
                      , 'green'))

    return 0


def comma_to_array(string):
    if "," in string:
        return list(map(lambda s: s.strip(),
                        string.split(",")))
    else:
        return [string]


def load_modules(names, colors, directory):
    return NamedExtensionManager(
        namespace="xthemer.effects",
        names=names,
        invoke_on_load=True,
        invoke_args=(colors, directory),
        on_missing_entrypoints_callback=
        lambda p: print(colored(f"ERROR: module {p} not found", "red")),
        on_load_failure_callback=
        lambda m, e, ex: print(colored(f"ERROR: module {e.name} failed to load"
                               , "red"))
    )


def dir_check():
    local_config_path = path.join(os.getenv("HOME"), ".config", "xthemer")
    global_config_path = "/etc/xthemer/templates"
    if not path.isdir(local_config_path) and not path.isdir(global_config_path):
        os.makedirs(path.join(local_config_path, "templates"))
        print("ERROR: no templates found")
        print(
            f"Put the contents of ./templates in {local_config_path}/templates")
        sys.exit(66)


def vprint(string, level=1):
    if level == 1:
        string = colored(string, 'green')
    if level <= options["verbose"]:
        print(string)


def read_colors(args):
    if args["--json"]:
        return read_json(sys.stdin, True)
    if args["--yaml"]:
        return read_yaml(sys.stdin, True)
    if args["--file"]:
        fn, ext = path.splitext(args["THEME"])
        if ext == ".json":
            return read_json(fn + ext)
        else:
            return read_yaml(fn + ext)
    else:
        if path.isfile(path.join(args["THEME"], "colors.json")):
            return read_json(path.join(args["THEME"], "colors.json"))

        if path.isfile(path.join(args["THEME"], "colors.yaml")):
            return read_yaml(path.join(args["THEME"], "colors.yaml"))

    sys.exit(66)


def read_json(file, stdin=False):
    if not stdin:
        with open(file) as f:
            out = json.load(f)
    else:
        out = json.load(file)

    if isinstance(out, list):
        return merge_dict(convert_color_format(out))
    else:
        return merge_dict(out)


def read_yaml(file, stdin=False):
    import yaml
    if not stdin:
        with open(file) as f:
            return merge_dict(yaml.load(f))
    else:
        return merge_dict(yaml.load(file))


def convert_color_format(colors):
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


def generate_colors(colors):
    out = {}
    for key, val in colors.items():
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


def merge_dict(colors):
    return {**{"scheme-name": "base16-custom", "scheme-author": ""},
            **generate_colors(colors),
            **{"scheme-slug": "custom"}}


def get_config_home():
    if os.getenv("XDG_CONFIG_HOME"):
        return os.getenv("XDG_CONFIG_HOME")
    else:
        return path.join(os.getenv("HOME"), ".config")


def get_template(name):
    vprint(f"\tgetting template {name}", 2)
    gpath = "/etc/xthemer/templates"
    lpath = path.join(os.getenv("HOME"), ".config", "xthemer", "templates")

    if path.isfile(path.join(lpath, f"{name}.mustache")):
        vprint(f"\tfound template {name} in {lpath}", 2)

        with open(path.join(lpath, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    elif path.isfile(path.join(gpath, f"{name}.mustache")):
        vprint(f"\tfound template {name} in {gpath}", 2)

        with open(path.join(gpath, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    else:
        vprint(f"\tGot error getting template {name}", 2)
        vprint(f"\t{name} does not exist", 2)
        raise Exception(f"Template {name} does not exist")


def render_template(name, colors):
    import pystache
    data = pystache.render(get_template(name), colors)
    vprint(f"\trendered template {name}", 3)
    vprint(f"\toutput:\n{data}", 3)
    return data


def load_config():
    import yaml
    gpath = "/etc/xthemer/config.yaml"
    lpath = path.join(get_config_home(), "xthemer", "config.yaml")
    hpath = path.join(os.getenv("HOME"), ".xthemer")
    if path.exists(lpath):
        with open(lpath) as f:
            return yaml.load(f)
    elif path.exists(hpath):
        with open(hpath) as f:
            return yaml.load(f)
    elif path.exists(gpath):
        with open(gpath) as f:
            return yaml.load(f)
    else:
        return {"modules": modules}


if __name__ == "__main__":
    sys.exit(main())
