import os, sys, time
# Allow running example without installing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from geliver import GeliverClient, ClientOptions

def main():
    token = os.getenv("GELIVER_TOKEN", "YOUR_TOKEN")
    client = GeliverClient(ClientOptions(token=token))

    sender = client.create_sender_address({
        "name": "ACME Inc.", "email": "ops@acme.test", "phone": "+905051234567",
        "address1": "Street 1", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34",
        "districtName": "Esenyurt", "districtID": 107605, "zip": "34020", "isRecipientAddress": False,
    })

    # Alıcı adresini sunucuda kaydetmeden inline gönderin
    shipment = client.create_shipment_test({
        "sourceCode": "API", "senderAddressID": sender["id"],
        "recipientAddress": {
            "name": "John Doe", "email": "john@example.com", "phone": "+905051234568",
            "address1": "Dest St 2", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34",
            "districtName": "Esenyurt", "districtID": 107605, "zip": "34020",
        },
        "length": 10, "width": 10, "height": 10, "distanceUnit": "cm", "weight": 1, "massUnit": "kg",
    })
    # Etiketler bazı akışlarda create sonrasında hazır olabilir; varsa hemen indirin
    try:
        if getattr(shipment, 'labelURL', None):
            with open('label_pre.pdf', 'wb') as f:
                f.write(client.download_label_for_shipment(shipment.id))
        if getattr(shipment, 'responsiveLabelURL', None) or getattr(shipment, 'responsiveLabelUrl', None):
            with open('label_pre.html', 'w', encoding='utf-8') as f:
                f.write(client.download_responsive_label_for_shipment(shipment.id))
    except Exception:
        pass

    # Teklifler create yanıtında hazır olabilir; önce onu kontrol edin
    offers = getattr(shipment, 'offers', None)
    start = time.time()
    if not (offers and (float(offers.get('percentageCompleted', 0)) >= 99 or offers.get('cheapest'))):
        # Hazır değilse, >= %99 olana kadar 1 sn aralıkla sorgulayın (backend 99'da kalabilir)
        while True:
            s = client.get_shipment(shipment.id)
            offers = getattr(s, 'offers', None)
            if offers and (float(offers.get('percentageCompleted', 0)) >= 99 or offers.get('cheapest')):
                break
            if time.time() - start > 60:
                raise TimeoutError('Timed out waiting for offers')
            time.sleep(1)

    tx = client.accept_offer(offers["cheapest"]["id"]) 
    print("Transaction:", tx.id, tx.isPayed)
    print("Barcode:", getattr(tx.shipment, 'barcode', None))
    print("Tracking number:", getattr(tx.shipment, 'trackingNumber', None))
    print("Label URL:", getattr(tx.shipment, 'labelURL', None))
    print("Tracking URL:", getattr(tx.shipment, 'trackingUrl', None))

    # Test gönderilerinde her GET /shipments çağrısı kargo durumunu bir adım ilerletir; prod'da webhook/manuel kontrol önerilir.
    for _ in range(5):
        time.sleep(1)
        client.get_shipment(shipment.id)
    latest = client.get_shipment(shipment.id)
    print("Tracking number (refresh):", getattr(latest, 'trackingNumber', None))
    ts = getattr(latest, 'trackingStatus', None)
    if ts:
        print('Status:', ts.get('trackingStatusCode'), ts.get('trackingSubStatusCode'))

    # Download labels
    with open('label.pdf', 'wb') as f:
        f.write(client.download_label_for_shipment(shipment.id))
    with open('label.html', 'w', encoding='utf-8') as f:
        f.write(client.download_responsive_label_for_shipment(shipment.id))

if __name__ == "__main__":
    main()
