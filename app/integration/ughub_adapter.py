import httpx
from typing import Any


class UGHubClient:
    def __init__(self, base_url: str = "https://ughub.nita.go.ug/api"):
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={"User-Agent": "UGSP-Backend/1.0"},
            )
        return self._client

    async def verify_nin(self, nin: str) -> dict[str, Any]:
        client = await self._get_client()
        resp = await client.post(
            "/identity/verify",
            json={"nin": nin},
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "valid": data.get("valid", False),
            "name": data.get("name", ""),
            "dob": data.get("dateOfBirth", ""),
        }

    async def submit_application(self, service_id: int, nin: str, metadata: dict) -> str:
        client = await self._get_client()
        resp = await client.post(
            "/applications/submit",
            json={"serviceId": service_id, "nin": nin, "metadata": metadata},
        )
        resp.raise_for_status()
        return resp.json().get("applicationId", "")

    async def check_payment(self, prn: str) -> dict[str, Any]:
        client = await self._get_client()
        resp = await client.get(f"/payments/{prn}")
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "UGHubClient":
        await self._get_client()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
