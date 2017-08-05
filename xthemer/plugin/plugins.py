from xthemer.plugin import XThemerPlugin
from xthemer import vprint, get_data_home, render_template
import os
import xdg
import subprocess
import json
from os import path


class Xresources(XThemerPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'path' in kwargs['plugin']:
            self.path = kwargs['plugin']['path']
        else:
            self.path = path.join(os.getenv("HOME"), ".Xresources.d", "colors")

    def run(self):
        with open(self.path, "w") as f:
            f.write(render_template("xresources", self.colors))
        vprint("\treloading Xresources", 2)
        vprint("\t> xrdb ~/.Xresources", 2)
        subprocess.run(["xrdb", path.join(os.getenv("HOME"), ".Xresources")])


class Bash(XThemerPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'path' in kwargs['plugin']:
            self.path = kwargs['plugin']['path']
        else:
            self.path = path.join(os.getenv("HOME"), ".bash_colors")

    def run(self):
        with open(self.path, "w") as f:
            f.write('export COLORS_foreground="#{}"\n'.
                    format(self.colors["base05-hex"]))
            f.write('export COLORS_background="#{}"\n'.
                    format(self.colors["base00-hex"]))
            f.write('export COLORS_cursorColor="#{}"\n'.
                    format(self.colors["base06-hex"]))

            for idx in range(0, 15):
                num = "0%d" % idx
                if idx > 9:
                    num = "%0.2X" % idx
                f.write('export COLORS_color{}="#{}"\n'.
                        format(idx, self.colors[f"base{num}-hex"]))


class Termite(XThemerPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'part_path' in kwargs['plugin']:
            self.part_path = kwargs['plugin']['part_path']
        else:
            self.part_path = path.join(xdg.XDG_CONFIG_HOME, "termite", "config.part")

    def run(self):
        with open(path.join(xdg.XDG_CONFIG_HOME, "termite", "config"), 'w') as f:
            color_part = render_template('termite', self.colors)
            config_part = ""
            if path.exists(self.part_path):
                with open(self.part_path, "r") as p:
                    config_part = "".join(p.readlines())

            f.write("\n".join([config_part, color_part]))

        vprint("\treloading termite", 2)
        vprint("\t> killall -USR1 termite", 2)
        subprocess.run(["killall", "-USR1", "termite"])


class Dunst(XThemerPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'part_path' in kwargs['plugin']:
            self.part_path = kwargs['plugin']['part_path']
        else:
            self.part_path = path.join(xdg.XDG_CONFIG_HOME, "dunst", "dunstrc.part")

    def run(self):
        with open(path.join(xdg.XDG_CONFIG_HOME, "dunst", "dunstrc"), 'w') as f:
            color_part = render_template('dunst', self.colors)
            config_part = ""
            if path.exists(self.part_path):
                with open(self.part_path, 'r') as p:
                    config_part = "".join(p.readlines())

            f.write("\n".join([config_part, color_part]))


class Vim(XThemerPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'path' in kwargs['plugin']:
            self.path = kwargs['plugin']['path']
        else:
            self.path = path.join(os.getenv("HOME"), ".vim_colors")
        if 'neovim' in kwargs['plugin']:
            self.neovim = kwargs['plugin']['neovim']
        else:
            self.neovim = False

    def run(self):
        with open(self.path, 'w') as f:
            f.write(render_template('vim', self.colors))

        if self.neovim:
            try:
                from neovim import attach
                from glob import glob
                neovimInstances = glob('/tmp/nvim*/0')
                vprint("\tfound neovim instances", 2)
                vprint(f"\tInstances: {neovimInstances}", 2)
                for p in neovimInstances:
                    nvim = attach('socket', path=p)
                    nvim.command('colorscheme base16-custom', async=True)
                    nvim.command('echo "reloaded theme"', async=True)
                    nvim.command('AirlineRefresh', async=True)
            except ImportError:
                vprint("\tno neovim library. continuing", 2)


class Emacs(XThemerPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'path' in kwargs['plugin']:
            self.path = kwargs['plugin']['path']
        else:
            self.path = path.join(os.getenv("HOME"), ".emacs.d", "private", "themes")

    def run(self):
        if not path.isdir(self.path):
            os.makedirs(self.path)
        with open(path.join(self.path, "base16-custom-theme.el"), "w") as f:
            f.write(render_template('emacs', self.colors))


class Wallpaper(XThemerPlugin):
    def run(self):
        wallpaper = path.join(self.dir, "wallpaper")
        if path.isfile(wallpaper):
            subprocess.run(["feh", "--bg-fill", wallpaper])


class Rofi(XThemerPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'path' in kwargs['plugin']:
            self.path = kwargs['plugin']['path']
        else:
            self.path = path.join(os.getenv("HOME"), ".Xresources.d", "rofi_colors")

    def run(self):
        with open(self.path, "w") as f:
            f.write(render_template("rofi", self.colors))

        vprint("\treloading rofi Xresources", 2)
        vprint("\t> xrdb ~/.Xresources", 2)
        subprocess.run(["xrdb", path.join(os.getenv("HOME"), ".Xresources")])


class RxBar(XThemerPlugin):
    def run(self):
        import json
        dirp = path.join(xdg.XDG_CONFIG_HOME, "rxbarrc")
        if not os.path.isfile(dirp):
            f = open(dirp, "w")
        else:
            f = open(dirp, "r+")

        config = {}
        try:
            config = json.load(f)
        except:
            pass
        config["fg"] = ["#" + self.colors["base05-hex"].upper()]
        config["bg"] = ["#" + self.colors["base00-hex"].upper()]
        f.seek(0)
        json.dump(config, f)
        f.truncate()
        f.close()


class CurrentTheme(XThemerPlugin):
    def run(self):
        share_path = get_data_home()
        if not path.isdir(share_path):
            os.makedirs(share_path)
        vprint("\tWriting current theme to " +
               path.join(share_path, "current_theme"), 2)
        with open(path.join(share_path, "current_theme"), "w") as f:
            f.write(self.dir)
        with open(path.join(share_path, "colors.json"), "w") as f:
            json.dump(self.colors, f)
