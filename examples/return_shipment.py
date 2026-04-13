import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from geliver import GeliverClient, ClientOptions


def main():
    token = os.getenv("GELIVER_TOKEN")
    shipment_id = os.getenv("GELIVER_RETURN_SHIPMENT_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not token or not shipment_id:
        print("Set GELIVER_TOKEN and GELIVER_RETURN_SHIPMENT_ID, or pass the shipment ID as the first argument.")
        raise SystemExit(1)

    client = GeliverClient(ClientOptions(token=token))
    returned = client.create_return_shipment(shipment_id, {})
    print("Return shipment:", returned.id)
    print("Label is not purchased yet. This example waits for offers and buys it with accept_offer().")

    current = returned
    offers = getattr(current, "offers", None)
    deadline = time.time() + 60
    while not offers or not offers.get("cheapest"):
        if time.time() >= deadline:
            print("Timed out waiting for return offers.")
            raise SystemExit(1)
        print("Waiting offers...", (offers or {}).get("percentageCompleted", 0), "%")
        time.sleep(1)
        current = client.get_shipment(returned.id)
        offers = getattr(current, "offers", None)

    tx = client.accept_offer(offers["cheapest"]["id"])
    print("Transaction:", tx.id)
    print("Purchased return shipment:", getattr(tx.shipment, "id", None))


if __name__ == "__main__":
    main()
