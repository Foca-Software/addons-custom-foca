from datetime import datetime
import json
import logging
import requests

_logger = logging.getLogger(__name__)


class DataSender:

    def _debo_date_format(self):
        return "%d/%m/%Y"

    def _get_authorization_header(self):
        return {
            "Authorization": "none",
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

    def send_debo_fields(
        self,
        data: dict = False,
        endpoint: str = "",
        allow_import: bool = False,
        context: dict = {},
    ):
        if not allow_import and context.get("import_file", False):
            return False
        try:
            headers = self._get_authorization_header()
            data = data or {}
            url = endpoint
            _logger.info("Sending data to: %s", url)
            _logger.info("data:")
            _logger.info(data)
            r = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(data),
            )
        except Exception as e:
            _logger.error(e)
            raise Warning(e)
        try:
            response = r.text
            _logger.info("Response:")
            if r.status_code == 200:
                _logger.info(response)
            else:
                _logger.error(response)
                return False
                # raise Warning(response)
        except Exception as e:
            _logger.error(e)
            raise Warning(e.args)

        return True
