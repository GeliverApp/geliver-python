import os, sys, time
# Allow running example without installing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from geliver import GeliverClient, ClientOptions

def main():
    token = os.getenv("GELIVER_TOKEN", "YOUR_TOKEN")
    client = GeliverClient(ClientOptions(token=token))

    sender = client.create_sender_address({
        "name": "ACME Inc.", "email": "ops@acme.test", "phone": "+905051234567",
        "address1": "Hasan Mahallesi", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34",
        "districtName": "Esenyurt", "zip": "34020", "isRecipientAddress": False,
    })

    # Alıcı adresini sunucuda kaydetmeden inline gönderin
    shipment = client.create_shipment_test({
        "senderAddressID": sender["id"],
        "recipientAddress": {
            "name": "John Doe", "email": "john@example.com", "phone": "+905051234568",
            "address1": "Atatürk Mahallesi", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34",
            "districtName": "Esenyurt", "zip": "34020",
        },
        "order": {"orderNumber": "ABC12333322", "sourceIdentifier": "https://magazaadresiniz.com", "totalAmount": "150", "totalAmountCurrency": "TL"},
    # Request dimensions/weight must be strings
    "length": "10.0", "width": "10.0", "height": "10.0", "distanceUnit": "cm", "weight": "1.0", "massUnit": "kg",
    })
    # Etiket indirme: Teklif kabulünden sonra (Transaction) gelen URL'leri kullanabilirsiniz de; URL'lere her shipment nesnesinin içinden ulaşılır.

    # Teklifler create yanıtındaki offers alanında gelir
    offers = getattr(shipment, 'offers', None)
    if not offers or not offers.get("cheapest"):
        print("Error: No cheapest offer available (henüz hazır değil)")
        sys.exit(1)

    try:
        tx = client.accept_offer(offers["cheapest"]["id"])
    except Exception as e:
        print(f"Accept offer error: {e}")
        # If it's an API error with response details, try to print them
        if hasattr(e, 'response') and hasattr(e.response, 'json'):
            try:
                error_data = e.response.json()
                print(f"API Error: {e.response.status_code} - {error_data}")
            except:
                pass
        sys.exit(1)
    print("Transaction:", tx.id, tx.isPayed)
    print("Barcode:", getattr(tx.shipment, 'barcode', None))
    print("Tracking number:", getattr(tx.shipment, 'trackingNumber', None))
    print("Label URL:", getattr(tx.shipment, 'labelURL', None))
    print("Tracking URL:", getattr(tx.shipment, 'trackingUrl', None))

    # Test gönderilerinde her GET /shipments çağrısı kargo durumunu bir adım ilerletir; prod'da webhook/manuel kontrol önerilir.
    #for _ in range(5):
    #    time.sleep(1)
    #    client.get_shipment(shipment.id)
    #latest = client.get_shipment(shipment.id)
    #print("Tracking number (refresh):", getattr(latest, 'trackingNumber', None))
    #ts = getattr(latest, 'trackingStatus', None)
    #if ts:
    #    print('Status:', ts.get('trackingStatusCode'), ts.get('trackingSubStatusCode'))

    # Etiket indirme: LabelFileType kontrolü
    # Eğer LabelFileType "PROVIDER_PDF" ise, LabelURL'den indirilen PDF etiket kullanılmalıdır.
    # Eğer LabelFileType "PDF" ise, responsiveLabelURL (HTML) dosyası kullanılabilir.
    if getattr(tx, 'shipment', None):
        label_file_type = getattr(tx.shipment, 'labelFileType', None)
        if label_file_type == 'PROVIDER_PDF':
            # PROVIDER_PDF: Sadece PDF etiket kullanılmalı
            if getattr(tx.shipment, 'labelURL', None):
                with open('label.pdf', 'wb') as f:
                    f.write(client.download_label_by_url(getattr(tx.shipment, 'labelURL')))
                print("PDF etiket indirildi (PROVIDER_PDF)")
        elif label_file_type == 'PDF':
            # PDF: ResponsiveLabel (HTML) kullanılabilir
            rl2 = getattr(tx.shipment, 'responsiveLabelURL', None)
            if rl2:
                with open('label.html', 'w', encoding='utf-8') as f:
                    f.write(client.download_responsive_label_by_url(rl2))
                print("HTML etiket indirildi (PDF)")
            # İsteğe bağlı olarak PDF de indirilebilir
            if getattr(tx.shipment, 'labelURL', None):
                with open('label.pdf', 'wb') as f:
                    f.write(client.download_label_by_url(getattr(tx.shipment, 'labelURL')))

if __name__ == "__main__":
    main()
