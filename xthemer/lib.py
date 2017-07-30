#!/usr/bin/env python3
"""Usage:
  themer.py [-m MODULE...] [--quiet | --verbose] THEME
  themer.py -h | --help | --version

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
import subprocess
import os.path as path
import glob
from docopt import docopt
import pystache


def main(argv=None):
    templates = {
        "xresources": write_xresources,
        "shell": write_bash,
        "termite": write_termite,
        "dunst": write_dunst,
        "vim": write_vim,
        "rofi": write_rofi,
        "emacs": write_emacs,
        "bar": write_bar
    }

    if argv is None:
        argv = sys.argv[1:]
    args = docopt(__doc__, argv=argv, version="0.1.0")

    share_path = path.join(os.getenv("HOME"), ".local/share/themer")
    local_config_path = path.join(os.getenv("HOME"), ".config/themer")
    global_config_path = "/etc/xthemer/templates"
    if not path.isdir(share_path):
        os.makedirs(share_path)
    if not path.isdir(local_config_path) and not path.isdir(global_config_path):
        os.makedirs(local_config_path + "/templates")
        print(f"Put the contents of ./templates in {local_config_path}/templates")
        return 66

    if not path.isdir(args["THEME"]):
        return 66

    colors = read_colors(args["THEME"])
    formats = templates.keys()

    if args["--output"]:
        if len(args["--output"]) == 1 and "," in args["--output"]:
            args["--output"] = map(lambda s: s.strip(), args["--output"][0].split(","))
        formats = args["--output"]

    for f in formats:
        if f in templates:
            templates[f](colors)

    write_wallpaper(args["THEME"])

    with open(path.join(os.getenv("HOME"), ".local/share/themer/current_theme"), "w") as f:
        f.write(args["THEME"])

    return 0


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
        if not "base0" in key:
            continue
        r = val[:2]
        g = val[2:4]
        b = val[4:]
        out[f"{key}-hex"] = val
        out[f"{key}-hex-r"] = r
        out[f"{key}-hex-g"] = g
        out[f"{key}-hex-b"] = b
        out[f"{key}-rgb-r"] = int("0x"+r, 16)
        out[f"{key}-rgb-g"] = int("0x"+g, 16)
        out[f"{key}-rgb-b"] = int("0x"+b, 16)
        out[f"{key}-dec-r"] = int("0x"+r, 16) / 255
        out[f"{key}-dec-g"] = int("0x"+g, 16) / 255
        out[f"{key}-dec-b"] = int("0x"+b, 16) / 255
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
    gpath = "/etc/xthemer/templates"
    lpath = path.join(os.getenv("HOME"), ".config/themer/templates")
    if path.isfile(path.join(lpath, f"{name}.mustache")):
        with open(path.join(lpath, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    elif path.isfile(path.join(gpath, f"{name}.mustache")):
        with open(path.join(gpath, f"{name}.mustache"), "r") as t:
            return "".join(t.readlines())
    else:
        raise Exception(f"Template {name} does not exist")


def write_xresources(colors):
    with open(path.join(os.getenv("HOME"), ".Xresources.d/colors"), "w") as f:
        f.write(pystache.render(get_template('xresources'), colors))
    subprocess.run(["xrdb", os.getenv("HOME") + "/.Xresources"])


def write_bash(colors):
    with open(os.getenv("HOME") + "/.bash_colors", "w") as f:
        f.write('export COLORS_foreground="#{}"\n'.format(colors["base05-hex"]))
        f.write('export COLORS_background="#{}"\n'.format(colors["base00-hex"]))
        f.write('export COLORS_cursorColor="#{}"\n'.format(colors["base06-hex"]))

        for idx in range(0,15):
            num = "0%d" % idx
            if idx > 9:
                num = "%0.2X" % idx
            f.write('export COLORS_color{}="#{}"\n'.format(idx, colors[f"base{num}-hex"]))


def write_termite(colors):
    config_home = get_config_home()

    with open(path.join(config_home, "termite/config"), 'w') as f:
        color_part = pystache.render(get_template('termite'), colors)
        config_part = ""
        with open(path.join(config_home, "termite/config.part"), 'r') as p:
            config_part = "".join(p.readlines())

        f.write("\n".join([config_part, color_part]))

    subprocess.run(["killall", "-USR1", "termite"])


def write_dunst(colors):
    config_home = get_config_home()

    with open(path.join(config_home, "dunst/dunstrc"), 'w') as f:
        color_part = pystache.render(get_template('dunst'), colors)
        config_part = ""
        with open(path.join(config_home, "dunst/dunstrc.part"), 'r') as p:
            config_part = "".join(p.readlines())

        f.write("\n".join([config_part, color_part]))


def write_vim(colors):
    with open(path.join(os.getenv("HOME"), ".vim_colors"), 'w') as f:
        f.write(pystache.render(get_template('vim'), colors))

    neovimInstances = glob.glob('/tmp/nvim*/0')
    for p in neovimInstances:
        try:
            from neovim import attach
            nvim = attach('socket', path=p)
            nvim.command('colorscheme base16-custom', async=True)
            nvim.command('echo "reloaded theme"', async=True)
            nvim.command('AirlineRefresh', async=True)
        except:
            pass


def write_emacs(colors):
    with open(path.join(os.getenv("HOME"), ".emacs.d/private/themes/base16-custom-theme.el"), "w") as f:
        f.write(pystache.render(get_template('emacs'), colors))


def write_wallpaper(directory):
    wallpaper = path.join(directory, "wallpaper")
    if path.isfile(wallpaper):
        subprocess.run(["feh", "--bg-fill", wallpaper])


def write_rofi(colors):
    with open(path.join(os.getenv("HOME"), ".Xresources.d/rofi_colors"), "w") as f:
        f.write(pystache.render(get_template('rofi'), colors))

    subprocess.run(["xrdb", os.getenv("HOME") + "/.Xresources"])


def write_bar(colors):
    dir = path.join(os.getenv("HOME"), ".config/rxbarrc")
    f = None
    if not os.path.isfile(dir):
        f = open(dir, "w")
    else:
        f = open(dir, "r+")

    config = {}
    try:
        config = json.load(f)
    except:
        pass
    config["fg"] = ["#"+colors["base05-hex"].upper()]
    config["bg"] = ["#"+colors["base00-hex"].upper()]
    f.seek(0)
    json.dump(config, f)
    f.truncate()
    f.close()

if __name__ == "__main__":
    sys.exit(main())
