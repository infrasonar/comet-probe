from libprobe.probe import Probe
from lib.check.comet import CheckComet
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckComet,
    )

    probe = Probe("comet", version, checks)

    probe.start()
