# Geliver Python SDK

[![PyPI](https://img.shields.io/pypi/v/geliver.svg)](https://pypi.org/project/geliver/) [![Python Versions](https://img.shields.io/pypi/pyversions/geliver.svg)](https://pypi.org/project/geliver/)

Geliver Python SDK — official Python client for Geliver Kargo Pazaryeri (Shipping Marketplace) API.
Türkiye’nin e‑ticaret gönderim altyapısı için kolay kargo entegrasyonu sağlar.

• Dokümantasyon (TR/EN): https://docs.geliver.io

---

## İçindekiler

- Kurulum
- Hızlı Başlangıç
- Adım Adım
- Webhooklar
- Testler
- Modeller
- Enum Kullanımı
- Notlar ve İpuçları

---

## Kurulum

- `pip install geliver`

---

## Akış (TR)

1. Geliver Kargo API tokenı alın (https://app.geliver.io/apitokens adresinden)
2. Gönderici adresi oluşturun (create_sender_address)
3. Gönderiyi alıcıyı ya ID ile ya da adres nesnesiyle vererek oluşturun
4. Teklifler tamamlanana kadar bekleyip en uygun teklifi kabul edin (accept_offer)
5. Barkod, takip numarası, etiket URL’leri Transaction içindeki Shipment’ten okunur
6. Test gönderilerinde her GET /shipments isteğinde kargo durumu bir adım ilerler; prod'da webhookları kullanın
7. Etiketleri indirin (PDF ve HTML dinamik etiket)
8. İade gönderisi gerekiyorsa create_return_shipment fonksiyonunu kullanın

---

## Hızlı Başlangıç

```python
from geliver import GeliverClient, ClientOptions

client = GeliverClient(ClientOptions(token="YOUR_TOKEN"))

sender = client.create_sender_address({
    "name": "ACME Inc.", "email": "ops@acme.test", "phone": "+905051234567",
    "address1": "Hasan Mahallesi", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34",
    "districtName": "Esenyurt", "zip": "34020",
})

shipment = client.create_shipment_test({
    "senderAddressID": sender["id"],
    "recipientAddress": {"name": "John Doe", "email": "john@example.com", "phone": "+905051234568", "address1": "Atatürk Mahallesi", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34", "districtName": "Kadıköy", "zip": "34000"},
    # Request dimensions/weight must be strings
    "length": "10.0", "width": "10.0", "height": "10.0", "distanceUnit": "cm", "weight": "1.0", "massUnit": "kg",
    "order": {
        "orderNumber": "WEB-12345",
        # sourceIdentifier alanına mağazanızın tam adresini yazın (ör. https://magazam.com).
        "sourceIdentifier": "https://magazam.com",
        "totalAmount": "150",
        "totalAmountCurrency": "TRY",
    },
})
```

Canlı ortamda `client.create_shipment_test(...)` yerine `client.create_shipment(...)` kullanın.

---

## Türkçe Akış (TR)

1. Gönderici adresi oluşturma

Her gönderici adresi için tek seferlik yapılır. Oluşan gönderici adres ID'sini saklayıp tekrar kullanılır.

```python
from geliver import GeliverClient, ClientOptions

client = GeliverClient(ClientOptions(token="YOUR_TOKEN"))

sender = client.create_sender_address({
    "name": "ACME Inc.",
    "email": "ops@acme.test",
    "phone": "+905051234567",
    "address1": "Hasan Mahallesi",
    "countryCode": "TR",
    "cityName": "Istanbul",
    "cityCode": "34",
    "districtName": "Esenyurt",

    "zip": "34020",
})
```

2. Gönderi oluşturma ve teklif kabulü (alıcıyı inline vererek)

```python
shipment = client.create_shipment({
    "senderAddressID": sender["id"],
    "recipientAddress": {
        "name": "John Doe", "email": "john@example.com", "phone": "+905051234568",
        "address1": "Atatürk Mahallesi", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34",
        "districtName": "Esenyurt", "zip": "34020",
    },
    "length": "10.0", "width": "10.0", "height": "10.0", "distanceUnit": "cm",
    "weight": "1.0", "massUnit": "kg",
    "order": {
        "orderNumber": "WEB-12345",
        # sourceIdentifier alanına mağazanızın tam adresini yazın (ör. https://magazam.com).
        "sourceIdentifier": "https://magazam.com",
        "totalAmount": "150",
        "totalAmountCurrency": "TRY",
    },
})

# Etiketler bazı akışlarda create sonrasında hazır olabilir; varsa hemen indirin
pre_label = getattr(shipment, 'labelURL', None)
if pre_label:
    # Avoid extra GET by using direct URL
    with open('label_pre.pdf', 'wb') as f:
        f.write(client.download_label_by_url(shipment.labelURL))
pre_html_url = getattr(shipment, 'responsiveLabelURL', None) or getattr(shipment, 'responsiveLabelUrl', None)
if pre_html_url:
    with open('label_pre.html', 'w', encoding='utf-8') as f:
        f.write(client.download_responsive_label_by_url(shipment.responsiveLabelURL))

# Teklifler create yanıtındaki offers alanında gelir
offers = getattr(shipment, "offers", None)
if not offers or not offers.get("cheapest"):
    raise RuntimeError("Teklifler hazır değil; GET /shipments çağrısı ile tekrar kontrol edin.")

cheapest = offers["cheapest"]
tx = client.accept_offer(cheapest["id"])  # purchase label
print('Barcode:', getattr(tx.shipment, 'barcode', None))
print('Label URL:', getattr(tx.shipment, 'labelURL', None))
print('Tracking URL:', getattr(tx.shipment, 'trackingUrl', None)) # Bu alan bazı firmalarda gönderici şubesine teslimden veya kurye sizden teslim aldıktan sonra dolar. Bu sebeple webhook kullarak bu alanı alabilirsiniz.
```

## Alıcı ID'si ile oluşturma (recipientAddressID)

```python
from geliver import CreateShipmentWithRecipientID
created_direct = client.create_shipment(CreateShipmentWithRecipientID(
    senderAddressID=sender["id"],
    recipientAddressID=recipient["id"],
    providerServiceCode="MNG_STANDART",
    length="10.0", width="10.0", height="10.0", distanceUnit="cm",
    weight="1.0", massUnit="kg",
))
```

3. Alıcı adresi oluşturma

```python
recipient = client.create_recipient_address({
    "name": "John Doe", "email": "john@example.com",
    "address1": "Atatürk Mahallesi", "countryCode": "TR", "cityName": "Istanbul", "cityCode": "34",
    "districtName": "Kadıköy", "zip": "34000",
})
```

3. Test gönderilerinde durum ilerletme (prod'da webhook önerilir)

```python
"""Test gönderilerinde her GET /shipments çağrısı kargo durumunu bir adım ilerletir."""
for _ in range(5):
    import time; time.sleep(1)
    client.get_shipment(shipment.id)
final = client.get_shipment(shipment.id)
ts = getattr(final, 'trackingStatus', None)
print('Final status:', ts.get('trackingStatusCode') if ts else None, ts.get('trackingSubStatusCode') if ts else None)
```

---

## İade Gönderisi Oluşturun

```python
returned = client.create_return_shipment(shipment.id, {
    'willAccept': True,
    'providerServiceCode': 'SURAT_STANDART',
    'count': 1,
})
```

Not:

- `providerServiceCode` alanı opsiyoneldir. Varsayılan olarak orijinal gönderinin sağlayıcısı kullanılır; gerekirse bu alanı vererek değiştirebilirsiniz.
- `senderAddress` alanı opsiyoneldir. Varsayılan olarak orijinal gönderinin alıcı adresi kullanılır; gerekirse bu alanı vererek değiştirebilirsiniz.

## Webhooklar

```python
from fastapi import FastAPI, Request
from geliver import verify_webhook, WebhookUpdateTrackingRequest

app = FastAPI()

@app.post("/webhooks/geliver")
async def webhook(req: Request):
    body = await req.body()
    ok = verify_webhook(body, req.headers, enable_verification=False)
    if not ok:
        return {"status": "invalid"}
    evt = WebhookUpdateTrackingRequest.model_validate_json(body.decode("utf-8"))
    if evt.event == "TRACK_UPDATED":
        shipment = evt.data
        print("Tracking update:", shipment.trackingUrl, shipment.trackingNumber)
    return {"status": "ok"}
```

### Webhookları Yönetme

```python
client.create_webhook(url="https://yourapp.test/webhooks/geliver")
webhooks = client.list_webhooks()
```

---

## Testler

- Birim testleri için `httpx.MockTransport` kullanabilirsiniz; `tests` klasörüne bakın.
- Üretilmiş modeller `geliver.models` altında yer alır (OpenAPI'den otomatik üretilir).

### Manuel takip kontrolü (isteğe bağlı)

```python
s = client.get_shipment(shipment.id)
ts = getattr(s, 'trackingStatus', None)
print('Status:', ts.get('trackingStatusCode') if ts else None, ts.get('trackingSubStatusCode') if ts else None)
```

### Gönderi Listeleme, Getir, Güncelle, İptal, Klonla

- Listeleme (docs): https://docs.geliver.io/docs/shipments_and_transaction/list_shipments
- Gönderi getir (docs): https://docs.geliver.io/docs/shipments_and_transaction/list_shipments
- Paket güncelle (docs): https://docs.geliver.io/docs/shipments_and_transaction/update_package_shipment
- Gönderi iptal (docs): https://docs.geliver.io/docs/shipments_and_transaction/cancel_shipment
- Gönderi klonla (docs): https://docs.geliver.io/docs/shipments_and_transaction/clone_shipment

```python
# Listeleme (sayfalandırma)
resp = client.list_shipments({"page": 1, "limit": 20})
for shipment in resp.data or []:
    print(shipment.id, getattr(shipment, "statusCode", None))

# Getir
fetched = client.get_shipment("SHIPMENT_ID")
ts = getattr(fetched, "trackingStatus", {}) or {}
print("Tracking:", ts.get("trackingStatusCode"), ts.get("trackingSubStatusCode"))

# Paket güncelle (eni, boyu, yüksekliği ve ağırlığı string gönderin)
client.update_package(fetched.id, {
    "length": "12.0",
    "width": "12.0",
    "height": "10.0",
    "distanceUnit": "cm",
    "weight": "1.2",
    "massUnit": "kg",
})

# İptal
client.cancel_shipment(fetched.id)

# Klonla
cloned = client.clone_shipment(fetched.id)
print("Cloned shipment:", getattr(cloned, "id", None))
```

---

## Modeller

- Shipment, Transaction, TrackingStatus, Address, ParcelTemplate, ProviderAccount, Webhook, Offer, PriceQuote ve daha fazlası.
- Tam liste için: `geliver.models` (otomatik oluşturulan modeller).

## Enum Kullanımı (TR)

```python
from geliver.models import ShipmentDistanceUnit, ShipmentMassUnit, ShipmentLabelFileType

shipment = client.create_shipment({
    "senderAddressID": sender["id"],
    "recipientAddressID": recipient["id"],
    "distanceUnit": ShipmentDistanceUnit.cm.value,
    "massUnit": ShipmentMassUnit.kg.value,
})
# Yanıtta label dosya türünü enum ile güvenli kontrol edebilirsiniz
if getattr(shipment, 'labelFileType', None) == ShipmentLabelFileType.PDF.value:
    print("PDF etiket hazır")
```

## Notlar ve İpuçları (TR)

- Ondalıklı alanlar (ör. length/weight) Decimal olarak işlenir; string kaynaklar hassasiyet kaybı olmadan Decimal'e dönüştürülür.
- Teklif üretimi zaman alabilir; 1 sn aralıklarla bekleme yeterlidir.
- Test gönderisi için `client.create_shipment_test(...)` veya `test=True` alanını kullanın; canlı ortamda `client.create_shipment(...)` çağırın.
- Takip numarası ile takip URL'si bazı kargo firmalarında teklif kabulünün hemen ardından oluşmayabilir. Paketi kargo şubesine teslim ettiğinizde veya kargo sizden teslim aldığında bu alanlar tamamlanır. Webhooklar ile değerleri otomatik çekebilir ya da teslimden sonra `shipment` GET isteği yaparak güncel bilgileri alabilirsiniz.
- Adres kuralları: phone alanı hem gönderici hem alıcı adresleri için zorunludur. Zip alanı gönderici adresi için zorunludur; alıcı adresi için opsiyoneldir. `create_sender_address` phone/zip eksikse, `create_recipient_address` phone eksikse hata verir.

## Örnekler

- Tam akış: `examples/full_flow.py`
- Tek aşamada gönderi (Create Transaction): `examples/onestep.py`
- Kapıda ödeme: `examples/pod.py`
- Kendi anlaşmanızla etiket satın alma: `examples/ownagreement.py`

---

## Hatalar ve İstisnalar

- İstemci şu durumlarda `GeliverError` fırlatır: (1) HTTP 4xx/5xx; (2) JSON envelope `result is False`.
- Hata alanları: `code: str|None`, `additional_message: str|None`, `status: int|None`, `response_body: Any`, `message`.

```python
from geliver.client import GeliverError

try:
    client.create_shipment({...})
except GeliverError as e:
    print('code:', e.code)
    print('message:', str(e))
    print('additional:', e.additional_message)
    print('status:', e.status)
```

- Şehir/İlçe seçimi: cityCode ve cityName beraber veya ayrı gönderilebilir; eşleşme açısından cityCode daha güvenilirdir. Şehir/ilçe verilerini API'den alabilirsiniz:

```python
cities = client.list_cities('TR')
districts = client.list_districts('TR', '34')
```

---

## Diğer Örnekler (Python)

- Sağlayıcı Hesapları (Provider Accounts)

```python
# Create provider account
acc = client.create_provider_account({
    'username': 'user', 'password': 'pass', 'name': 'My Account', 'providerCode': 'SURAT',
    'version': 1, 'isActive': True, 'isPublic': False, 'sharable': False, 'isDynamicPrice': False,
})
# List accounts
accounts = client.list_provider_accounts()
# Delete account
client.delete_provider_account(acc['id'], is_delete_account_connection=True)
```

- Kargo Şablonları (Parcel Templates)

```python
tpl = client.create_parcel_template({'name':'Small Box','distanceUnit':'cm','massUnit':'kg','height':'4','length':'4','weight':'1','width':'4'})
tpls = client.list_parcel_templates()
client.delete_parcel_template(tpl['id'])
```

[![Geliver Kargo Pazaryeri](https://geliver.io/geliverlogo.png)](https://geliver.io/)
Geliver Kargo Pazaryeri: https://geliver.io/

Etiketler (Tags): python, sdk, api-client, geliver, kargo, kargo-pazaryeri, shipping, e-commerce, turkey
