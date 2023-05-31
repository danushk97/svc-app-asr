from appscommon.flaskutils.confighelper import inject_dependencies

from asr.application.service import SERVICES


_services = None


def bootstrap():
    global _services
    if _services:
        return _services
    
    _services = inject_dependencies(SERVICES, {})
