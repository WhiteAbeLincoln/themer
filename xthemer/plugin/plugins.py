from xthemer.plugin import XThemerPlugin
from xthemer import get_data_home, render_template
import os
import xdg
import subprocess
import json
from confuse import NotFoundError, ConfigTypeError


class Xresources(XThemerPlugin):
    def run(self):
        try:
            path = self.config['path'].as_filename()
        except NotFoundError:
            path = os.path.join(os.getenv("HOME"), ".Xresources.d", "colors")
        except ConfigTypeError:
            return

        with open(path, "w") as f:
            f.write(render_template("xresources", self.colors))
        self._log.info("reloading Xresources")
        self._log.debug("> xrdb ~/.Xresources")
        subprocess.run(["xrdb", os.path.join(os.getenv("HOME"), ".Xresources")])


class Shell(XThemerPlugin):
    def run(self):
        try:
            command = self.config['command'].get()
        except NotFoundError:
            command = None
        except ConfigTypeError:
            return

        if command is not None:
            self._log.info("> bash -c " + command)
            subprocess.run(["bash", "-c", command])


class BashColors(XThemerPlugin):
    def run(self):
        try:
            path = self.config['path'].as_filename()
        except NotFoundError:
            path = os.path.join(os.getenv("HOME"), ".bash_colors")
        except ConfigTypeError:
            return

        with open(path, "w") as f:
            f.write(render_template("bash", self.colors))


class Termite(XThemerPlugin):
    def run(self):
        try:
            part_path = self.config['partial'].as_filename()
        except NotFoundError:
            part_path = os.path.join(xdg.XDG_CONFIG_HOME,
                                     "termite", "config.part")
        except ConfigTypeError:
            return

        with open(os.path.join(xdg.XDG_CONFIG_HOME, "termite", "config"), 'w') as f:
            color_part = render_template('termite', self.colors)
            config_part = ""
            if os.path.exists(part_path):
                with open(part_path, "r") as p:
                    config_part = "".join(p.readlines())

            f.write("\n".join([config_part, color_part]))

        self._log.info("reloading termite")
        self._log.debug("> killall -USR1 termite")
        subprocess.run(["killall", "-USR1", "termite"])


class Dunst(XThemerPlugin):
    def run(self):
        try:
            part_path = self.config['partial'].as_filename()
        except NotFoundError:
            part_path = os.path.join(xdg.XDG_CONFIG_HOME, "dunst", "dunstrc.part")
        except ConfigTypeError:
            return

        with open(os.path.join(xdg.XDG_CONFIG_HOME, "dunst", "dunstrc"), 'w') as f:
            color_part = render_template('dunst', self.colors)
            config_part = ""
            if os.path.exists(part_path):
                with open(part_path, 'r') as p:
                    config_part = "".join(p.readlines())

            f.write("\n".join([config_part, color_part]))


class Vim(XThemerPlugin):
    def run(self):
        try:
            path = self.config['path'].as_filename()
        except NotFoundError:
            path = os.path.join(os.getenv("HOME"), ".vim_colors")
        except ConfigTypeError:
            return

        try:
            tryneovim = self.config['neovim'].get(bool)
        except NotFoundError:
            tryneovim = False
        except ConfigTypeError:
            return

        with open(path, 'w') as f:
            f.write(render_template('vim', self.colors))

        if tryneovim:
            try:
                from neovim import attach
                from glob import glob
                neovimInstances = glob('/tmp/nvim*/0')
                self._log.info("found neovim instances")
                self._log.debug("Instances: %s", neovimInstances)
                for p in neovimInstances:
                    nvim = attach('socket', path=p)
                    nvim.command('colorscheme base16-custom', async=True)
                    nvim.command('echo "reloaded theme"', async=True)
                    nvim.command('AirlineRefresh', async=True)
            except ImportError:
                self._log.warning("no neovim library found.")
            except ConnectionRefusedError:
                pass


class Template(XThemerPlugin):
    def run(self):
        try:
            templates = self.config.get()
        except NotFoundError:
            return
        except ConfigTypeError:
            return

        for name, val in templates.items():
            if "path" in val:
                color_part = render_template(name, self.colors)
                if color_part is None:
                    color_part = ""
                config_part = ""
                if "partial" in val:
                    try:
                        with open(os.path.expanduser(val["partial"])) as f:
                            config_part = "".join(f.readlines())
                    except FileNotFoundError:
                        self._log.warning("file %s not found when "
                                          "reading partial for template %s",
                                          val["partial"], name)
                try:
                    with open(os.path.expanduser(val["path"]), "w") as f:
                        self._log.info("writing template %s to %s",
                                       name, val["path"])
                        f.write("\n".join([config_part, color_part]))
                except FileNotFoundError:
                    self._log.warning("file %s not found when "
                                      "writing template %s",
                                      val["path"], name)
            if "command" in val:
                self._log.info("running command > %s", val["command"])
                subprocess.run(["bash", "-c", val["command"]])


class Emacs(XThemerPlugin):
    def run(self):
        try:
            path = self.config['path'].as_filename()
        except NotFoundError:
            path = os.path.join(os.getenv("HOME"), ".emacs.d")
        except ConfigTypeError:
            return

        if not os.path.isdir(path):
            os.makedirs(path)
        with open(os.path.join(path, "base16-custom-theme.el"), "w") as f:
            f.write(render_template('emacs', self.colors))


class Wallpaper(XThemerPlugin):
    def run(self):
        wallpaper = os.path.join(self.directory, "wallpaper")
        if os.path.isfile(wallpaper):
            subprocess.run(["feh", "--bg-fill", wallpaper])


class Rofi(XThemerPlugin):
    def run(self):
        try:
            path = self.config['path'].as_filename()
        except NotFoundError:
            path = os.path.join(os.getenv("HOME"), ".Xresources.d", "rofi_colors")
        except ConfigTypeError:
            return

        with open(path, "w") as f:
            f.write(render_template("rofi", self.colors))

        self._log.info("reloading rofi Xresources")
        self._log.debug("> xrdb ~/.Xresources")
        subprocess.run(["xrdb", os.path.join(os.getenv("HOME"), ".Xresources")])


class CurrentTheme(XThemerPlugin):
    def run(self):
        share_path = get_data_home()
        if not os.path.isdir(share_path):
            os.makedirs(share_path)
        self._log.info("Writing current theme to %s",
                        os.path.join(share_path, "current_theme"))
        with open(os.path.join(share_path, "current_theme"), "w") as f:
            f.write(self.directory)
        with open(os.path.join(share_path, "colors.json"), "w") as f:
            json.dump(self.colors, f)
