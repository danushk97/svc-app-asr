from io import BytesIO

from appscommon.flaskutils.http.utils import send_success_response
from appscommon.flaskutils.http.middleware import error_filter
from flask import Blueprint, request

from asr.bootstrap import bootstrap
from asr import constants


asr_feed_app = Blueprint('asr_feed', __name__, url_prefix='/asr/feed')
_services = bootstrap()


@asr_feed_app.post('')
@error_filter
def input_feed():
    audio = request.files['audio']
    audio_bytes = BytesIO(audio.read())
    _services[constants.ASR_FEED_SERVICE]().feed(audio_bytes, audio.filename)
    return send_success_response('Input feed was successful.')


@asr_feed_app.post('/from-link')
@error_filter
def input_feed_from_link():
    audio = request.json or {}
    file_link = audio.get('file_link')
    if not file_link:
        return {
            "message": "Please provide file_link"
        }, 400
    _services[constants.ASR_FEED_SERVICE]().feed_from_link(file_link)
    return send_success_response('Input feed was successful.')


@asr_feed_app.get('/status')
@error_filter
def input_feed_status():
    feed_status = _services[constants.ASR_FEED_SERVICE]().feed_status()
    return send_success_response(feed_status)


@asr_feed_app.get('/result/<file_name>')
@error_filter
def input_feed_result(file_name):
    feed_result = _services[constants.ASR_FEED_SERVICE]().feed_result(file_name)
    return send_success_response(feed_result)
