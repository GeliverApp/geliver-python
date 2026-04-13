import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from geliver import GeliverClient, ClientOptions


def main():
    token = os.getenv("GELIVER_TOKEN")
    shipment_id = os.getenv("GELIVER_RETURN_SHIPMENT_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not token or not shipment_id:
        print("Set GELIVER_TOKEN and GELIVER_RETURN_SHIPMENT_ID, or pass the shipment ID as the first argument.")
        raise SystemExit(1)

    client = GeliverClient(ClientOptions(token=token))
    tx = client.create_return_transaction(shipment_id, {})
    print("Transaction:", tx.id)
    print("Purchased return shipment:", getattr(tx.shipment, "id", None))


if __name__ == "__main__":
    main()
