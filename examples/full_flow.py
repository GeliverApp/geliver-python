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
    # Request dimensions/weight must be strings
    "length": "10.0", "width": "10.0", "height": "10.0", "distanceUnit": "cm", "weight": "1.0", "massUnit": "kg",
    })
    # Etiket indirme: Teklif kabulünden sonra (Transaction) gelen URL'leri kullanabilirsiniz de; URL'lere her shipment nesnesinin içinden ulaşılır.

    # Teklifler create yanıtında hazır olabilir; önce onu kontrol edin
    offers = getattr(shipment, 'offers', None)
    start = time.time()
    if not (offers and (float(offers.get('percentageCompleted', 0)) == 100 or offers.get('cheapest'))):
        # Hazır değilse, %100 olana kadar 1 sn aralıkla sorgulayın
        while True:
            s = client.get_shipment(shipment.id)
            offers = getattr(s, 'offers', None)
            if offers and (float(offers.get('percentageCompleted', 0)) == 100 or offers.get('cheapest')):
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

    # Download labels using URLs from transaction.shipment (no extra GET)
    if getattr(tx, 'shipment', None) and getattr(tx.shipment, 'labelURL', None):
        with open('label.pdf', 'wb') as f:
            f.write(client.download_label_by_url(getattr(tx.shipment, 'labelURL')))
    rl2 = getattr(tx.shipment, 'responsiveLabelURL', None) if getattr(tx, 'shipment', None) else None
    if rl2:
        with open('label.html', 'w', encoding='utf-8') as f:
            f.write(client.download_responsive_label_by_url(rl2))

if __name__ == "__main__":
    main()
