from xthemer.plugin import PluginBase
from xthemer import vprint, get_config_home, render_template
import os
import subprocess
from os import path


class Xresources(PluginBase):
    def run(self):
        with open(path.join(os.getenv("HOME"), ".Xresources.d", "colors"), "w") as f:
            f.write(render_template("xresources", self.colors))
        vprint("\treloading Xresources", 2)
        vprint("\t> xrdb ~/.Xresources", 2)
        subprocess.run(["xrdb", path.join(os.getenv("HOME"), ".Xresources")])


class Bash(PluginBase):
    def run(self):
        with open(path.join(os.getenv("HOME"), ".bash_colors"), "w") as f:
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


class Termite(PluginBase):
    def run(self):
        config_home = get_config_home()
        part_path = path.join(config_home, "termite", "config.part")

        with open(path.join(config_home, "termite", "config"), 'w') as f:
            color_part = render_template('termite', self.colors)
            config_part = ""
            if path.exists(part_path):
                with open(part_path, "r") as p:
                    config_part = "".join(p.readlines())

            f.write("\n".join([config_part, color_part]))

        vprint("\treloading termite", 2)
        vprint("\t> killall -USR1 termite", 2)
        subprocess.run(["killall", "-USR1", "termite"])


class Dunst(PluginBase):
    def run(self):
        config_home = get_config_home()
        part_path = path.join(config_home, "dunst", "dunstrc.part")

        with open(path.join(config_home, "dunst", "dunstrc"), 'w') as f:
            color_part = render_template('dunst', self.colors)
            config_part = ""
            if path.exists(part_path):
                with open(part_path, 'r') as p:
                    config_part = "".join(p.readlines())

            f.write("\n".join([config_part, color_part]))


class Vim(PluginBase):
    def run(self):
        with open(path.join(os.getenv("HOME"), ".vim_colors"), 'w') as f:
            f.write(render_template('vim', self.colors))

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


class Emacs(PluginBase):
    def run(self):
        dirp = path.join(os.getenv("HOME"),
                         ".emacs.d", "private", "themes")
        if not path.isdir(dirp):
            os.makedirs(dirp)
        with open(path.join(dirp, "base16-custom-theme.el"), "w") as f:
            f.write(render_template('emacs', self.colors))


class Wallpaper(PluginBase):
    def run(self):
        wallpaper = path.join(self.dir, "wallpaper")
        if path.isfile(wallpaper):
            subprocess.run(["feh", "--bg-fill", wallpaper])


class Rofi(PluginBase):
    def run(self):
        with open(path.join(os.getenv("HOME"), ".Xresources.d", "rofi_colors"),
                  "w") as f:
            f.write(render_template("rofi", self.colors))

        vprint("\treloading rofi Xresources", 2)
        vprint("\t> xrdb ~/.Xresources", 2)
        subprocess.run(["xrdb", path.join(os.getenv("HOME"), ".Xresources")])


class RxBar(PluginBase):
    def run(self):
        import json
        dirp = path.join(get_config_home(), "rxbarrc")
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


class CurrentTheme(PluginBase):
    def run(self):
        share_path = path.join(os.getenv("HOME"), ".local", "share", "themer")
        if not path.isdir(share_path):
            os.makedirs(share_path)
        vprint("\tWriting current theme to " +
               path.join(share_path, "current_theme"), 2)
        with open(path.join(share_path, "current_theme"), "w") as f:
            f.write(self.dir)
