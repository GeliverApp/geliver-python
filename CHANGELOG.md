# Changelog

Bu dosya SDK'daki önemli değişiklikleri listeler.

This file documents notable changes in the SDK.

## Sürüm / Version

- Türkçe: Bu değişiklikler `0.4.0` sürümü için hazırlandı.
- English: These changes are prepared for version `0.4.0`.

## Türkçe

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
