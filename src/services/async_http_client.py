from httpx import AsyncClient, HTTPError, RequestError, TimeoutException


class HTTPXClient:
    """
    A wrapper class for httpx AsyncClient to handle http requests.
    """

    async def __aenter__(self, **kwargs):
        self.client = AsyncClient(**kwargs)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def get(self, url):
        try:
            response = await self.client.get(url=url)
            response.raise_for_status()
            return response
        except (HTTPError, RequestError, TimeoutException) as e:
            raise ConnectionError(e) from e
