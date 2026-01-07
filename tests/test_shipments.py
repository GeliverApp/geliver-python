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


def test_create_transaction_wraps_shipment():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path.endswith("/transactions"):
            body = json.loads(request.content.decode())
            assert body.get("test") is None  # must be under shipment
            assert body.get("providerServiceCode") == "SURAT_STANDART"
            assert body.get("providerAccountID") == "acc-1"
            assert isinstance(body.get("shipment"), dict)
            shipment = body["shipment"]
            assert shipment.get("test") is True
            assert shipment.get("providerServiceCode") is None
            assert shipment.get("providerAccountID") is None
            assert shipment.get("length") == "10.5"
            assert shipment.get("weight") == "1.25"
            assert shipment.get("order", {}).get("sourceCode") == "API"
            payload = {"result": True, "data": {"id": "tx1", "offerID": "offer-123", "isPayed": True}}
            return httpx.Response(200, json=payload)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = GeliverClient(ClientOptions(token="test"))
    client._client._transport = transport  # type: ignore

    tx = client.create_transaction({
        "senderAddressID": "sender-1",
        "recipientAddress": {"name": "R", "phone": "+905000000000", "address1": "A", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34", "districtName": "Esenyurt"},
        "length": 10.5,
        "weight": 1.25,
        "distanceUnit": "cm",
        "massUnit": "kg",
        "test": True,
        "providerServiceCode": "SURAT_STANDART",
        "providerAccountID": "acc-1",
        "order": {"orderNumber": "ORDER-1"},
    })
    assert tx.id == "tx1"
