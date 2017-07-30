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

options = {
    "verbose": False,
    "quiet": False
}


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
        print(
            f"Put the contents of ./templates in {local_config_path}/templates")
        return 66

    if not path.isdir(args["THEME"]):
        return 66

    colors = read_colors(args["THEME"])
    formats = templates.keys()

    options["verbose"] = args["--verbose"]
    options["quiet"] = args["--quiet"]

    if "--module" in args:
        if len(args["--module"]) == 1 and "," in args["--module"]:
            args["--module"] = map(lambda s: s.strip(),
                                   args["--module"][0].split(","))
        elif len(args["--module"]) > 1:
            formats = args["--module"]

    for f in formats:
        if f in templates:
            vprint(f"Running module {f}")
            templates[f](colors)

    vprint("Running module wallpaper")
    write_wallpaper(args["THEME"])

    vprint("Writing current theme to " + path.join(share_path, "current_theme"))
    with open(path.join(share_path, "current_theme"), "w") as f:
        f.write(args["THEME"])

    if not options["quiet"]:
        print(f"Applied theme: {args['THEME']}")

    return 0


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
    lpath = path.join(os.getenv("HOME"), ".config/themer/templates")
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


def write_xresources(colors):
    with open(path.join(os.getenv("HOME"), ".Xresources.d/colors"), "w") as f:
        f.write(pystache.render(get_template('xresources'), colors))
    vprint("\treloading Xresources")
    vprint("\t> xrdb ~/.Xresources")
    subprocess.run(["xrdb", os.getenv("HOME") + "/.Xresources"])


def write_bash(colors):
    with open(os.getenv("HOME") + "/.bash_colors", "w") as f:
        f.write('export COLORS_foreground="#{}"\n'.format(colors["base05-hex"]))
        f.write('export COLORS_background="#{}"\n'.format(colors["base00-hex"]))
        f.write(
            'export COLORS_cursorColor="#{}"\n'.format(colors["base06-hex"]))

        for idx in range(0, 15):
            num = "0%d" % idx
            if idx > 9:
                num = "%0.2X" % idx
            f.write('export COLORS_color{}="#{}"\n'.format(idx, colors[
                f"base{num}-hex"]))


def write_termite(colors):
    config_home = get_config_home()
    part_path = path.join(config_home, "termite/config.part")

    with open(path.join(config_home, "termite/config"), 'w') as f:
        color_part = pystache.render(get_template('termite'), colors)
        config_part = ""
        if path.exists(part_path):
            with open(part_path, "r") as p:
                config_part = "".join(p.readlines())

        f.write("\n".join([config_part, color_part]))

    vprint("\treloading termite")
    vprint("\t> killall -USR1 termite")
    subprocess.run(["killall", "-USR1", "termite"])


def write_dunst(colors):
    config_home = get_config_home()
    part_path = path.join(config_home, "dunst/dunstrc.part")

    with open(path.join(config_home, "dunst/dunstrc"), 'w') as f:
        color_part = pystache.render(get_template('dunst'), colors)
        config_part = ""
        if path.exists(part_path):
            with open(part_path, 'r') as p:
                config_part = "".join(p.readlines())

        f.write("\n".join([config_part, color_part]))


def write_vim(colors):
    with open(path.join(os.getenv("HOME"), ".vim_colors"), 'w') as f:
        f.write(pystache.render(get_template('vim'), colors))

    try:
        from neovim import attach
        neovimInstances = glob.glob('/tmp/nvim*/0')
        vprint("\tfound neovim instances")
        vprint(f"\tInstances: {neovimInstances}")
        for p in neovimInstances:
            nvim = attach('socket', path=p)
            nvim.command('colorscheme base16-custom', async=True)
            nvim.command('echo "reloaded theme"', async=True)
            nvim.command('AirlineRefresh', async=True)
    except:
        pass


def write_emacs(colors):
    dirp = path.join(os.getenv("HOME"),
                     ".emacs.d/private/themes")
    if not path.isdir(dirp):
        os.makedirs(dirp)
    with open(path.join(dirp, "base16-custom-theme.el"), "w") as f:
        f.write(pystache.render(get_template('emacs'), colors))


def write_wallpaper(directory):
    wallpaper = path.join(directory, "wallpaper")
    if path.isfile(wallpaper):
        subprocess.run(["feh", "--bg-fill", wallpaper])


def write_rofi(colors):
    with open(path.join(os.getenv("HOME"), ".Xresources.d/rofi_colors"),
              "w") as f:
        f.write(pystache.render(get_template('rofi'), colors))

    vprint("\treloading Xresources")
    vprint("\t> xrdb ~/.Xresources")
    subprocess.run(["xrdb", path.join(os.getenv("HOME"), ".Xresources")])


def write_bar(colors):
    dirp = path.join(os.getenv("HOME"), ".config/rxbarrc")
    if not os.path.isfile(dirp):
        f = open(dirp, "w")
    else:
        f = open(dirp, "r+")

    config = {}
    try:
        config = json.load(f)
    except:
        pass
    config["fg"] = ["#" + colors["base05-hex"].upper()]
    config["bg"] = ["#" + colors["base00-hex"].upper()]
    f.seek(0)
    json.dump(config, f)
    f.truncate()
    f.close()


if __name__ == "__main__":
    sys.exit(main())
