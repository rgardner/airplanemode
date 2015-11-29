#!/usr/bin/env python3
"""Toggle network connectivity and Internet-only daemons."""

import configparser
import os
import subprocess
from subprocess import DEVNULL

# The programs to terminate
RELEVANT_APPS = ['Caffeine', 'Dropbox', 'Google Drive']
AIRPLANE_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.airplanemode.ini')

__version__ = '0.2.1'


class State(object):
    def __repr__(self):
        return 'bluetooth: {}, wifi: {}, apps: {}'.format(self.bluetooth,
                                                          self.wifi,
                                                          self.apps)

    @property
    def bluetooth(self):
        """Is bluetooth on? Lazy instantiates to the current status."""
        if not hasattr(self, '_bluetooth'):
            output = subprocess.check_output(['blueutil', 'status'])
            self._bluetooth = 'on' in str(output)
        return self._bluetooth

    @bluetooth.setter
    def bluetooth(self, status):
        self._bluetooth = status

    @property
    def wifi(self):
        """Is wifi on? Lazy instantiates to the current status."""
        if not hasattr(self, '_wifi'):
            cmd = ['networksetup', '-getairportpower', 'en0']
            output = subprocess.check_output(cmd)
            self._wifi = 'On' in str(output)
        return self._wifi

    @wifi.setter
    def wifi(self, status):
        self._wifi = status

    @property
    def apps(self):
        """Which of the relevant apps are active? Lazy instantiate."""
        if not hasattr(self, '_apps'):
            self._apps = [app for app in RELEVANT_APPS if is_running(app)]
        return self._apps

    @apps.setter
    def apps(self, active_apps):
        self._apps = active_apps

    def write(self):
        config = configparser.ConfigParser()
        config['PREVSTATE'] = {
            'bluetooth': str(self.bluetooth),
            'wifi': str(self.wifi),
            'apps': ','.join(self.apps)
        }
        with open(AIRPLANE_CONFIG_PATH, 'w+') as configfile:
            config.write(configfile)

    @staticmethod
    def from_save():
        config = init_config_parser()
        state = State()
        state.bluetooth = config.getboolean('PREVSTATE', 'bluetooth')
        state.wifi = config.getboolean('PREVSTATE', 'wifi')
        state.apps = config.getlist('PREVSTATE', 'apps')
        return state


def init_config_parser() -> configparser.ConfigParser:
    conv = {}
    conv['list'] = lambda v: [e.strip() for e in v.split(',') if e.strip()]
    config = configparser.ConfigParser(converters=conv)
    config.read(AIRPLANE_CONFIG_PATH)
    return config


def airplane_mode_enabled() -> bool:
    return os.path.exists(AIRPLANE_CONFIG_PATH)


def is_running(program) -> bool:
    return run_quiet(['pgrep', program]).returncode == 0


def run_quiet(argv):
    """Ignore output of program."""
    return subprocess.run(argv, stdout=DEVNULL, stderr=DEVNULL)


def toggle():
    if airplane_mode_enabled():
        # re-enable previously disabled state
        prev_state = State.from_save()
        if prev_state.bluetooth:
            subprocess.call(['blueutil', 'on'])
        if prev_state.wifi:
            subprocess.call(['networksetup', '-setairportpower', 'en0', 'on'])
        for app in prev_state.apps:
            subprocess.call(['open', '-a', app])
        os.remove(AIRPLANE_CONFIG_PATH)

    else:
        # disable default apps
        curr_state = State()
        curr_state.write()
        if curr_state.bluetooth:
            subprocess.call(['blueutil', 'off'])
        if curr_state.wifi:
            subprocess.call(['networksetup', '-setairportpower', 'en0', 'off'])
        for app in curr_state.apps:
            run_quiet(['pkill', app])


def main():
    import sys

    if len(sys.argv) == 1:
        toggle()
        sys.exit(0)

    if sys.argv[1] == 'status':
        enabled = 'Enabled' if airplane_mode_enabled() else 'Disabled'
        print("Airplane Mode: {}".format(enabled))

    elif sys.argv[1] == '-v' or sys.argv[1] == '--version':
        print('airplanemode version {}'.format(__version__))

    else:
        print('usage: airplane <status>')
        sys.exit(1)
