from __future__ import annotations
import json
import httpx
from geliver import GeliverClient, ClientOptions


def test_list_shipments_uses_envelope_and_pagination():
    # Mock transport returning one page with two items
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"].startswith("Bearer ")
        if request.url.path.endswith("/shipments"):
            payload = {
                "result": True,
                "limit": 2,
                "page": int(request.url.params.get("page", "1")),
                "totalRows": 2,
                "totalPages": 1,
                "data": [
                    {"id": "s1", "statusCode": "CREATED"},
                    {"id": "s2", "statusCode": "DELIVERED"},
                ],
            }
            return httpx.Response(200, json=payload)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = GeliverClient(ClientOptions(token="test", base_url="https://api.geliver.io/api/v1"))
    client._client._transport = transport  # type: ignore

    items = list(client.iter_shipments())
    assert [s.id for s in items] == ["s1", "s2"]


def test_accept_offer():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path.endswith("/transactions"):
            body = json.loads(request.content.decode())
            assert body.get("offerID") == "offer-123"
            payload = {"result": True, "data": {"id": "tx1", "offerID": "offer-123", "isPayed": True}}
            return httpx.Response(200, json=payload)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = GeliverClient(ClientOptions(token="test"))
    client._client._transport = transport  # type: ignore

    tx = client.accept_offer("offer-123")
    assert tx.id == "tx1"
    assert tx.isPayed is True

