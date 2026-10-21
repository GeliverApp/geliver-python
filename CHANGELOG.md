# Changelog

Bu dosya SDK'daki önemli değişiklikleri listeler.

This file documents notable changes in the SDK.

## Sürüm / Version

- Türkçe: Bu değişiklikler `0.5.0` sürümü için hazırlandı.
- English: These changes are prepared for version `0.5.0`.

## Türkçe

### 0.5.0

- Tüm yeni gönderilerde gönderici ve alıcı için adres ID veya satır içi adresin tam olarak biri doğrulanır.
- `create_shipment(...)` ile `isReturn=True` ve gönderici/alıcı için bağımsız ID veya satır içi adres seçimi kullanılarak iade gönderisi oluşturulabilir.
- `examples/incoming_shipment.py` eklendi.

### 0.4.0

#### Eklendi

- `create_return_transaction(...)` ile iadeyi oluşturup etiketi hemen satın alma akışı eklendi.
- İki yeni iade örneği eklendi:
  - `examples/return_shipment.py`
  - `examples/return_transaction.py`

#### Değişti

- `create_return_shipment(...)` artık shipment-only iade akışıdır ve etiketi satın almaz.
- İade dokümanı iki akışı ayrı anlatır.
- README örnekleri, etiketin daha sonra `accept_offer(...)` ile satın alınabileceğini açıklar.

## English

### 0.5.0

- All new shipment flows validate that each side provides exactly one address ID or inline address.
- `create_shipment(...)` supports independent returns with `isReturn=True` and either an address ID or an inline address for each side.
- Added `examples/incoming_shipment.py`.

### 0.4.0

#### Added

- Added `create_return_transaction(...)` for creating a return shipment and purchasing the label immediately.
- Added return examples for:
  - `examples/return_shipment.py`
  - `examples/return_transaction.py`

#### Changed

- `create_return_shipment(...)` now represents the shipment-only return flow and does not purchase the label.
- Return documentation now explains the two return flows separately.
- README examples now document that label purchase can be performed later with `accept_offer(...)`.
