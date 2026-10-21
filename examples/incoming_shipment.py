import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from geliver import GeliverClient, ClientOptions, CreateShipmentWithRecipientID, Address


def main():
    token = os.getenv('GELIVER_TOKEN')
    recipient_address_id = os.getenv('GELIVER_MERCHANT_ADDRESS_ID')
    if not token or not recipient_address_id:
        raise SystemExit('Set GELIVER_TOKEN and GELIVER_MERCHANT_ADDRESS_ID.')

    client = GeliverClient(ClientOptions(token=token))
    shipment = client.create_shipment(CreateShipmentWithRecipientID(
        sourceCode='SDK', isReturn=True, test=True,
        senderAddress=Address(
            name='Müşteri Adı', email='customer@example.com', phone='+905051234567',
            address1='Örnek Mahallesi 1', countryCode='TR', cityCode='34', districtName='Kadıköy', zip='34000',
        ),
        recipientAddressID=recipient_address_id,
        length='10', width='10', height='10', distanceUnit='cm', weight='1', massUnit='kg',
    ))
    print('Gelecek gönderi:', shipment.id)


if __name__ == '__main__':
    main()
