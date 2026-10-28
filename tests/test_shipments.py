from __future__ import annotations
import json
import unittest
import httpx
from geliver import GeliverClient, ClientOptions, CreateShipmentWithRecipientID, CreateShipmentWithRecipientAddress, Address


class ShipmentsTests(unittest.TestCase):
    def test_new_shipment_flows_allow_default_sender_and_require_recipient(self) -> None:
        client = GeliverClient(ClientOptions(token="test"))
        base = {"sourceCode": "SDK", "senderAddressID": "merchant-1", "recipientAddressID": "customer-1"}
        invalid = [
            {**base, "senderAddress": {"address1": "A"}},
            {**base, "recipientAddressID": None},
            {**base, "recipientAddress": {"address1": "B", "phone": "+905051234568"}},
        ]

        for body in invalid:
            with self.assertRaisesRegex(ValueError, "exactly one"):
                client.create_shipment(body)
            with self.assertRaisesRegex(ValueError, "exactly one"):
                client.create_shipment_test(body)
            with self.assertRaisesRegex(ValueError, "exactly one"):
                client.create_transaction({"shipment": body})

        client._client._transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"result": True, "data": {"id": "s1", "offerID": "offer-1"}}))  # type: ignore
        client.create_shipment({"recipientAddressID": "customer-1"})
        client.create_shipment_test({"recipientAddressID": "customer-1"})
        client.create_transaction({"shipment": {"recipientAddressID": "customer-1"}})

    def test_create_incoming_shipment_address_combinations(self) -> None:
        sent = []

        def handler(request: httpx.Request) -> httpx.Response:
            sent.append(json.loads(request.content.decode()))
            return httpx.Response(200, json={"result": True, "data": {"id": "incoming-1"}})

        client = GeliverClient(ClientOptions(token="test"))
        client._client._transport = httpx.MockTransport(handler)  # type: ignore
        merchant = Address(name="Merchant", phone="+905051234567", address1="A")
        customer = Address(name="Customer", phone="+905051234568", address1="B")
        cases = [
            (CreateShipmentWithRecipientID(sourceCode="SDK", isReturn=True, recipientAddressID="customer-1"), None, "recipientAddressID"),
            (CreateShipmentWithRecipientID(sourceCode="SDK", isReturn=True, senderAddressID="merchant-1", recipientAddressID="customer-1"), "senderAddressID", "recipientAddressID"),
            (CreateShipmentWithRecipientAddress(sourceCode="SDK", isReturn=True, senderAddressID="merchant-1", recipientAddress=customer), "senderAddressID", "recipientAddress"),
            (CreateShipmentWithRecipientID(sourceCode="SDK", isReturn=True, senderAddress=merchant, recipientAddressID="customer-1"), "senderAddress", "recipientAddressID"),
            (CreateShipmentWithRecipientAddress(sourceCode="SDK", isReturn=True, senderAddress=merchant, recipientAddress=customer), "senderAddress", "recipientAddress"),
        ]

        for request, sender_key, recipient_key in cases:
            client.create_shipment(request)
            body = sent[-1]
            self.assertIs(body["isReturn"], True)
            for key in ("senderAddressID", "senderAddress", "recipientAddressID", "recipientAddress"):
                self.assertEqual(key in body, key == sender_key or key == recipient_key)

    def test_create_incoming_shipment_keeps_address_direction(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertTrue(request.url.path.endswith("/shipments"))
            body = json.loads(request.content.decode())
            self.assertIs(body["isReturn"], True)
            self.assertEqual(body["recipientAddress"]["name"], "Customer")
            self.assertNotIn("senderAddress", body)
            self.assertNotIn("senderAddressID", body)
            return httpx.Response(200, json={"result": True, "data": {"id": "incoming-1"}})

        client = GeliverClient(ClientOptions(token="test"))
        client._client._transport = httpx.MockTransport(handler)  # type: ignore
        shipment = client.create_shipment(CreateShipmentWithRecipientAddress(
            sourceCode="SDK", isReturn=True,
            recipientAddress=Address(name="Customer", phone="+905051234567", address1="A"),
        ))
        self.assertEqual(shipment.id, "incoming-1")

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

    def test_return_flows_forward_customer_sender_address_without_swapping(self) -> None:
        customer = {"name": "Customer", "phone": "+905051234567", "address1": "Pickup address"}
        calls = []

        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertTrue(request.url.path.endswith("/shipments/original-1"))
            body = json.loads(request.content)
            calls.append(body)
            self.assertEqual(body["senderAddress"], customer)
            self.assertNotIn("recipientAddress", body)
            self.assertNotIn("recipientAddressID", body)
            self.assertIs(body["isReturn"], True)
            return httpx.Response(200, json={"result": True, "data": {"id": "return-1", "offerID": "offer-1"}})

        client = GeliverClient(ClientOptions(token="test"))
        client._client._transport = httpx.MockTransport(handler)
        client.create_return_shipment("original-1", {"senderAddress": customer})
        client.create_return_transaction("original-1", {"senderAddress": customer})
        self.assertEqual(len(calls), 2)
        self.assertNotIn("willAccept", calls[0])
        self.assertIs(calls[1]["willAccept"], True)

    def test_create_return_shipment_with_will_accept_raises(self) -> None:
        client = GeliverClient(ClientOptions(token="test"))
        with self.assertRaises(ValueError):
            client.create_return_shipment("shp-1", {"willAccept": True})

    def test_create_return_transaction_forces_will_accept(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "POST" and request.url.path.endswith("/shipments/shp-1"):
                body = json.loads(request.content.decode())
                self.assertIs(body.get("isReturn"), True)
                self.assertIs(body.get("willAccept"), True)
                self.assertEqual(body.get("count"), 1)
                payload = {"result": True, "data": {"id": "tx-1", "offerID": "offer-1", "transactionType": "CREATE_SHIPMENT"}}
                return httpx.Response(200, json=payload)
            return httpx.Response(404)

        transport = httpx.MockTransport(handler)
        client = GeliverClient(ClientOptions(token="test"))
        client._client._transport = transport  # type: ignore

        returned = client.create_return_transaction("shp-1", {"providerServiceCode": "SURAT_STANDART"})
        self.assertEqual(returned.id, "tx-1")
        self.assertEqual(returned.offerID, "offer-1")


if __name__ == "__main__":
    unittest.main()
