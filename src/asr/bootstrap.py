from flask.json import JSONEncoder

from appscommon.flaskutils.confighelper import inject_dependencies
from bson import ObjectId

from asr.application.services import SERVICES


_services = None


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def bootstrap():
    global _services
    if _services:
        return _services

    _services = inject_dependencies(SERVICES, {})
