"""Toggle network connectivity and Internet-only daemons."""

import argparse
import configparser
import pathlib
import subprocess

import platformdirs

from .version import __version__

# The programs to terminate
RELEVANT_APPS = ["Creative Cloud", "Dropbox", "Google Drive", "OneDrive"]
AIRPLANE_CONFIG_PATH = pathlib.Path.home() / ".airplanemode.ini"
APP_NAME = "airplanemode"
APP_AUTHOR = "Starflower"
APP_DATA_FILENAME = "state.ini"


class State:
    """Tracks state of devices and apps controlled by airplane mode."""

    def __repr__(self):
        """Returns representation of current state."""
        return f"bluetooth: {self.bluetooth}, wifi: {self.wifi}, apps: {self.apps}"

    @property
    def bluetooth(self):
        """Is bluetooth on? Lazy instantiates to the current status."""
        if not hasattr(self, "_bluetooth"):
            output = subprocess.check_output(["blueutil", "--power"])
            self._bluetooth = "on" in str(output)
        return self._bluetooth

    @bluetooth.setter
    def bluetooth(self, status):
        """Sets bluetooth state."""
        self._bluetooth = status

    @property
    def wifi(self):
        """Is wifi on? Lazy instantiates to the current status."""
        if not hasattr(self, "_wifi"):
            cmd = ["networksetup", "-getairportpower", "en0"]
            output = subprocess.check_output(cmd)
            self._wifi = "On" in str(output)
        return self._wifi

    @wifi.setter
    def wifi(self, status):
        """Sets Wi-Fi state."""
        self._wifi = status

    @property
    def apps(self):
        """Which of the relevant apps are active? Lazy instantiate."""
        if not hasattr(self, "_apps"):
            self._apps = [app for app in RELEVANT_APPS if is_running(app)]
        return self._apps

    @apps.setter
    def apps(self, active_apps):
        """Sets apps state."""
        self._apps = active_apps

    def write(self):
        """Writes state to disk."""
        config = configparser.ConfigParser()
        config["PREVSTATE"] = {
            "bluetooth": str(self.bluetooth),
            "wifi": str(self.wifi),
            "apps": ",".join(self.apps),
        }
        data_file = app_data_file_path()
        data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(data_file, "w+", encoding="utf-8") as configfile:
            config.write(configfile)

    @staticmethod
    def from_save():
        """Reads state from disk."""
        config = init_config_parser()
        state = State()
        state.bluetooth = config.getboolean("PREVSTATE", "bluetooth")
        state.wifi = config.getboolean("PREVSTATE", "wifi")
        # getlist extension added by init_config_parser
        state.apps = config.getlist("PREVSTATE", "apps")  # pylint: disable=no-member
        return state


def init_config_parser() -> configparser.ConfigParser:
    """Creates config parser for airplane mode state file."""
    conv = {}
    conv["list"] = lambda v: [e.strip() for e in v.split(",") if e.strip()]
    config = configparser.ConfigParser(converters=conv)
    config.read(app_data_file_path())
    return config


def airplane_mode_enabled() -> bool:
    """Returns True if the airplane mode config file exists, False otherwise."""
    return app_data_file_path().exists()


def app_data_file_path() -> pathlib.Path:
    """Returns path to the app data file (app state)."""
    data_dir = platformdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    return pathlib.Path(data_dir, APP_DATA_FILENAME)


def is_running(program: str) -> bool:
    """Returns True if the program is running, False otherwise."""
    try:
        run_quiet(["pgrep", program])
        return True
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 1:
            return False
        raise


def run_quiet(argv):
    """Ignore output of program."""
    subprocess.run(
        argv, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def toggle():
    """Toggles airplane mode."""
    if airplane_mode_enabled():
        # re-enable previously disabled state
        prev_state = State.from_save()
        if prev_state.bluetooth:
            subprocess.call(["blueutil", "on"])
        if prev_state.wifi:
            subprocess.call(["networksetup", "-setairportpower", "en0", "on"])
        for app in prev_state.apps:
            subprocess.call(["open", "-a", app])
        app_data_file_path().unlink()

    else:
        # disable default apps
        curr_state = State()
        curr_state.write()
        if curr_state.bluetooth:
            subprocess.call(["blueutil", "off"])
        if curr_state.wifi:
            subprocess.call(["networksetup", "-setairportpower", "en0", "off"])
        for app in curr_state.apps:
            run_quiet(["pkill", app])


def run_status_command() -> None:
    """Runs status CLI command, showing current airplane mode status."""
    enabled = "Enabled" if airplane_mode_enabled() else "Disabled"
    print(f"Airplane Mode: {enabled}")


def run_toggle_command() -> None:
    """Runs toggle CLI command, toggling airplane mode."""
    toggle()


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(prog="airplanemode")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.set_defaults(func=run_toggle_command)
    subparsers = parser.add_subparsers()
    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=run_status_command)
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    args.func()
