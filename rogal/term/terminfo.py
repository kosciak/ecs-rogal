import curses

from .capabilities import FLAG_CAPABILITIES, NUM_CAPABILITIES, STR_CAPABILITIES


"""Wrapper for basic terminfo database access.

For non Linux support consider: https://github.com/Rockhopper-Technologies/jinxed

"""


class Terminfo:

    def __init__(self, term=None, fd=-1):
        curses.setupterm(term, fd)

    def get_flag(self, cap_name):
        return curses.tigetflag(cap_name)

    def get_num(self, cap_name):
        return curses.tigetnum(cap_name)

    def get_str(self, cap_name):
        return curses.tigetstr(cap_name)

    tigetflag = get_flag
    tigetnum = get_num
    tigetstr = get_str

    def get(self, cap_name):
        if cap_name in FLAG_CAPABILITIES:
            return self.get_flag(cap_name)
        if cap_name in NUM_CAPABILITIES:
            return self.get_num(cap_name)
        return self.get_str(cap_name)

    def tparm(self, cap_name, *parameters):
        """Return parametrized sequence for given capability."""
        return curses.tparm(cap_name, *parameters)

    def list_all(self):
        """Return all supported capabilities as {cap_name: sequence, } dict."""
        capabilities = {}
        for cap_name in sorted(FLAG_CAPABILITIES):
            value = self.get_flag(cap_name)
            if value >= 0:
                capabilities[cap_name] = value
        for cap_name in sorted(NUM_CAPABILITIES):
            value = self.get_num(cap_name)
            if value >= 0:
                capabilities[cap_name] = value
        for cap_name in sorted(STR_CAPABILITIES):
            value = self.get_str(cap_name)
            if value:
                capabilities[cap_name] = value
        return capabilities


def setupterm():
    global _TERMINFO
    _TERMINFO = Terminfo()


def tigetflag(cap_name):
    return _TERMINFO.get_flag(cap_name)

def tigetnum(cap_name):
    return _TERMINFO.get_num(cap_name)

def tigetstr(cap_name):
    return _TERMINFO.get_str(cap_name)

def tparm(cap_name, *parameters):
    return _TERMINFO.tparm(cap_name, *parameters)

