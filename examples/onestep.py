import os
from geliver.client import GeliverClient, ClientOptions

token = os.getenv('GELIVER_TOKEN')
if not token:
    print('GELIVER_TOKEN required')
    raise SystemExit(1)

client = GeliverClient(ClientOptions(token=token))

sender = client.create_sender_address({
    'name': 'OneStep Sender', 'email': 'sender@example.com',
    'address1': 'Hasan Mahallesi', 'countryCode': 'TR', 'cityName': 'Istanbul', 'cityCode': '34', 'districtName': 'Esenyurt', 'zip': '34020',
})

tx = client.create_transaction({
    'senderAddressID': sender.get('id'),
    'recipientAddress': {
        'name': 'OneStep Recipient', 'phone': '+905000000000', 'address1': 'Atatürk Mahallesi', 'countryCode': 'TR', 'cityName': 'Istanbul', 'cityCode': '34', 'districtName': 'Esenyurt',
    },
    'length': '10.0', 'width': '10.0', 'height': '10.0', 'distanceUnit': 'cm', 'weight': '1.0', 'massUnit': 'kg',
})
print('transaction id:', tx.id)
