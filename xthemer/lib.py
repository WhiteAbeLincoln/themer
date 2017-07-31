#!/usr/bin/env python3
"""Usage:
  xthemer [-m MODULE...] [--quiet | --verbose] THEME
  xthemer -h | --help | --version

Arguments:
  THEME  theme directory

Options:
  -h --help           show this
  -m --module MODULE  theme module
  --quiet             show less text
  --verbose           show more text
"""
import sys
import os
import json
import os.path as path
from docopt import docopt
from stevedore import NamedExtensionManager
from xthemer import __version__

options = {
    "verbose": False,
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

    if not path.isdir(args["THEME"]):
        print(f"ERROR: theme dir {args['THEME']} does not exist")
        return 66

    options["verbose"] = args["--verbose"]
    options["quiet"] = args["--quiet"]
    colors = read_colors(args["THEME"])
    config = load_config()

    if len(args["--module"]) == 1 and "," in args["--module"]:
        config["modules"] = map(lambda s: s.strip(),
                                args["--module"][0].split(","))
    elif len(args["--module"]) > 1:
        config["modules"] = args["--module"]

    mgr = load_modules(config["modules"], colors, args["THEME"])

    def run(e):
        vprint(f"Running module {e.name}")
        e.obj.run()

    mgr.map(run)

    if not options["quiet"]:
        print(f"Applied theme: {args['THEME']}")

    return 0


def load_modules(names, colors, directory):
    return NamedExtensionManager(
        namespace="xthemer.effects",
        names=names,
        invoke_on_load=True,
        invoke_args=(colors, directory),
        on_missing_entrypoints_callback=
        lambda p: print(f"ERROR: module {p} not found"),
        on_load_failure_callback=
        lambda m, e, ex: print(f"ERROR: module {e.name} failed to load")
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


def vprint(args):
    if options["verbose"]:
        print(args)


def read_colors(theme_dir):
    # can read one of colors.json, or colors.yaml
    if path.isfile(path.join(theme_dir, "colors.json")):
        with open(path.join(theme_dir, "colors.json")) as f:
            out = json.load(f)
            if isinstance(out, list):
                return merge_dict(convert_color_format(out))
            else:
                return merge_dict(out)

    if path.isfile(path.join(theme_dir, "colors.yaml")):
        import yaml
        with open(path.join(theme_dir, "colors.yaml")) as f:
            return merge_dict(yaml.load(f))

    sys.exit(66)


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
    vprint(f"\tgetting template {name}")
    gpath = "/etc/xthemer/templates"
    lpath = path.join(os.getenv("HOME"), ".config", "themer", "templates")

    if path.isfile(path.join(lpath, f"{name}.mustache")):
        vprint(f"\tfound template {name} in {lpath}")

        with open(path.join(lpath, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    elif path.isfile(path.join(gpath, f"{name}.mustache")):
        vprint(f"\tfound template {name} in {gpath}")

        with open(path.join(gpath, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    else:
        raise Exception(f"Template {name} does not exist")


def render_template(name, colors):
    import pystache
    return pystache.render(get_template(name), colors)


def load_config():
    import yaml
    if path.isdir(get_config_home()):
        try:
            with open(path.join(get_config_home(), "xthemer", "config")) as f:
                return yaml.load(f)
        except FileNotFoundError:
            return {"modules": modules}
    else:
        try:
            with open(path.join(os.getenv("HOME"), ".xthemer")) as f:
                return yaml.load(f)
        except FileNotFoundError:
            return {"modules": modules}


if __name__ == "__main__":
    sys.exit(main())
