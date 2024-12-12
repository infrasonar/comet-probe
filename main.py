from libprobe.probe import Probe
from lib.check.comet import check_comet
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'comet': check_comet
    }

    probe = Probe("comet", version, checks)

    probe.start()
