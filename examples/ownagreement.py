import os
from geliver.client import GeliverClient, ClientOptions

token = os.getenv('GELIVER_TOKEN')
if not token:
    print('GELIVER_TOKEN required')
    raise SystemExit(1)

client = GeliverClient(ClientOptions(token=token))

sender = client.create_sender_address({
    'name': 'OwnAg Sender', 'email': 'sender@example.com',
    'address1': 'Hasan Mahallesi', 'countryCode': 'TR', 'cityName': 'Istanbul', 'cityCode': '34', 'districtName': 'Esenyurt', 'zip': '34020',
})

tx = client.create_transaction({
    'senderAddressID': sender.get('id'),
    'recipientAddress': {
        'name': 'OwnAg Recipient', 'phone': '+905000000002', 'address1': 'Dest 2', 'countryCode': 'TR', 'cityName': 'Istanbul', 'cityCode': '34', 'districtName': 'Esenyurt',
    },
    'length': '10.0', 'width': '10.0', 'height': '10.0', 'distanceUnit': 'cm', 'weight': '1.0', 'massUnit': 'kg',
    'providerServiceCode': 'SURAT_STANDART',
    'providerAccountID': 'c0dfdb42-012d-438c-9d49-98d13b4d4a2b',
})
print('transaction id:', tx.id)
