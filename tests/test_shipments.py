from __future__ import annotations
import json
import unittest
import httpx
from geliver import GeliverClient, ClientOptions


class ShipmentsTests(unittest.TestCase):
    def test_list_shipments_uses_envelope_and_pagination(self) -> None:
        # Mock transport returning one page with two items
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertTrue(request.headers["Authorization"].startswith("Bearer "))
            self.assertTrue((request.headers.get("User-Agent") or "").startswith("geliver-python/"))
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
        self.assertEqual([s.id for s in items], ["s1", "s2"])

    def test_accept_offer(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "POST" and request.url.path.endswith("/transactions"):
                body = json.loads(request.content.decode())
                self.assertEqual(body.get("offerID"), "offer-123")
                payload = {"result": True, "data": {"id": "tx1", "offerID": "offer-123", "isPayed": True}}
                return httpx.Response(200, json=payload)
            return httpx.Response(404)

        transport = httpx.MockTransport(handler)
        client = GeliverClient(ClientOptions(token="test"))
        client._client._transport = transport  # type: ignore

        tx = client.accept_offer("offer-123")
        self.assertEqual(tx.id, "tx1")
        self.assertIs(tx.isPayed, True)

    def test_create_transaction_wraps_shipment(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "POST" and request.url.path.endswith("/transactions"):
                body = json.loads(request.content.decode())
                self.assertIsNone(body.get("test"))  # must be under shipment
                self.assertEqual(body.get("providerServiceCode"), "SURAT_STANDART")
                self.assertEqual(body.get("providerAccountID"), "acc-1")
                self.assertIsInstance(body.get("shipment"), dict)
                shipment = body["shipment"]
                self.assertIs(shipment.get("test"), True)
                self.assertIsNone(shipment.get("providerServiceCode"))
                self.assertIsNone(shipment.get("providerAccountID"))
                self.assertEqual(shipment.get("length"), "10.5")
                self.assertEqual(shipment.get("weight"), "1.25")
                self.assertEqual(shipment.get("order", {}).get("sourceCode"), "SDK")
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
        self.assertEqual(tx.id, "tx1")

    def test_create_return_shipment_uses_post_and_defaults(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "POST" and request.url.path.endswith("/shipments/shp-1"):
                body = json.loads(request.content.decode())
                self.assertIs(body.get("isReturn"), True)
                self.assertEqual(body.get("count"), 1)
                self.assertEqual(body.get("providerServiceCode"), "SURAT_STANDART")
                self.assertNotIn("willAccept", body)
                payload = {"result": True, "data": {"id": "ret-1"}}
                return httpx.Response(200, json=payload)
            return httpx.Response(404)

        transport = httpx.MockTransport(handler)
        client = GeliverClient(ClientOptions(token="test"))
        client._client._transport = transport  # type: ignore

        returned = client.create_return_shipment("shp-1", {"providerServiceCode": "SURAT_STANDART"})
        self.assertEqual(returned.id, "ret-1")


if __name__ == "__main__":
    unittest.main()
