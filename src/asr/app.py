import os

import connexion
from appscommon.logconfig import init_logging

from asr.bootstrap import bootstrap, CustomJSONEncoder
from asr.config import Config


def main():
    init_logging()
    Config.init_config()
    bootstrap()
    basedir = os.path.abspath(os.path.dirname(__file__))

    connex_app = connexion.App(__name__, specification_dir=basedir)
    connex_app.add_api(
        "swagger.yml",
        strict_validation=True
    )
    connex_app.app.json_encoder = CustomJSONEncoder

    return connex_app.app


if __name__ == '__main__':
    main()
