import requests
import base64
import json


class Judge0:
    # languages
    LANG_GO113 = 60
    LANG_NODE12 = 63
    LANG_PYTHON3 = 71
    LANG_RUBY2 = 72

    # statuses
    STATUS_ACCEPTED = 3
    STATUS_WRONG_ANSWER = 4

    def __init__(self,
                 api_protocol: str = 'https',
                 api_host: str = 'judge0-ce.p.rapidapi.com',
                 api_querystring: dict = {
                     'base64_encoded': 'true',
                     'wait': 'true',
                     'fields': '*'
                 },
                 api_key: str = None):
        self.api_protocol = api_protocol
        self.api_host = api_host
        self.api_querystring = api_querystring
        self.api_headers = {
            'content-type': 'application/json',
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': api_host
        }

    def _b64(self, input: str):
        input_bytes = input.encode('ascii')
        base64_bytes = base64.b64encode(input_bytes)
        return base64_bytes.decode('ascii')

    def submit(self, language_id: int, source_code: str, stdin: str = None, expected_output: str = None):
        """
        Return a tuple of JSON response and Exception object.
        """
        url = f'{self.api_protocol}://{self.api_host}/submissions'
        data = {
            'language_id': language_id,
            'source_code': self._b64(source_code),
        }
        if stdin:
            data['stdin'] = self._b64(stdin)
        if expected_output:
            data['expected_output'] = self._b64(expected_output)
        try:
            resp = requests.post(
                url,
                data=json.dumps(data),
                headers=self.api_headers,
                params=self.api_querystring
            )
            return resp.json(), None
        except Exception as e:
            return None, e
