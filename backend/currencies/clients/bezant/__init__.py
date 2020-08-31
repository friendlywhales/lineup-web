
import requests


class Client:
    http = None
    apikey = None
    endpoint = None
    _endpoints = {
        'testnet': 'https://testnet-apis.bezant.io',
    }

    class InvalidArgumentError(ValueError):
        pass

    def __init__(self, endpoint: str, apikey: str):
        try:
            self.endpoint = self._endpoints[endpoint]
        except KeyError:
            raise self.InvalidArgumentError(f'invalid endpoint: {endpoint}')
        self.apikey = apikey
        self.http = requests.Session()
        self.http.headers['apikey'] = self.apikey

    def create_wallet(self, password: str) -> dict:
        url = f'{self.endpoint}/blockchain/v1/wallet'
        res = self.http.post(
            url=url,
            json={
                'skey': password,
            }
        )
        res.raise_for_status()
        return res.json()

