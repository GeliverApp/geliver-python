from __future__ import annotations
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Iterator
import httpx
from .types import Envelope, Shipment, Transaction, ListParams, ShipmentsListResponse, AddressesListResponse, ProviderAccountsListResponse, ParcelTemplatesListResponse, WebhooksListResponse, CitiesListResponse, DistrictsListResponse
from .requests import CreateShipmentRequest, UpdatePackageRequest, CreateAddressRequest


DEFAULT_BASE_URL = "https://api.geliver.io/api/v1"


@dataclass
class ClientOptions:
    token: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0
    max_retries: int = 2
    user_agent: Optional[str] = None


class GeliverError(Exception):
    def __init__(self, message: str, *, status: Optional[int] = None, code: Optional[str] = None, additional_message: Optional[str] = None, response_body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.additional_message = additional_message
        self.response_body = response_body


class GeliverClient:
    def __init__(self, options: ClientOptions) -> None:
        self._base_url = options.base_url.rstrip('/')
        self._token = options.token
        self._timeout = options.timeout
        self._max_retries = options.max_retries
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        if options.user_agent:
            headers["User-Agent"] = options.user_agent
        self._client = httpx.Client(base_url=self._base_url, headers=headers, timeout=self._timeout)

    # ---- low-level ----
    def _request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json_body: Any = None) -> Any:
        attempt = 0
        while True:
            try:
                res = self._client.request(method, path, params=params, json=json_body)
            except httpx.TimeoutException as e:
                attempt += 1
                if attempt > self._max_retries:
                    raise e
                self._backoff(attempt)
                continue

            if res.status_code >= 400:
                # try decode json
                payload: Any
                try:
                    payload = res.json()
                except Exception:
                    payload = res.text
                if self._should_retry(res.status_code) and attempt < self._max_retries:
                    attempt += 1
                    self._backoff(attempt)
                    continue
                code = payload.get("code") if isinstance(payload, dict) else None
                message = payload.get("message") if isinstance(payload, dict) else None
                addl = payload.get("additionalMessage") if isinstance(payload, dict) else None
                raise GeliverError(message or f"HTTP {res.status_code}", status=res.status_code, code=code, additional_message=addl, response_body=payload)

            data: Any
            try:
                env = Envelope.model_validate(res.json())
                if env.result is False:
                    raise GeliverError(env.message or 'API error', code=env.code, additional_message=env.additionalMessage, response_body=env.model_dump())
                if env.data is not None:
                    return env.data
                return res.json()
            except GeliverError:
                raise
            except Exception:
                return res.text

    def _should_retry(self, status_code: int) -> bool:
        return status_code == 429 or status_code >= 500

    def _backoff(self, attempt: int) -> None:
        base = 0.2 * (2 ** (attempt - 1))
        delay = min(2.0, base + 0.1)
        time.sleep(delay)

    # ---- resources: shipments ----
    def create_shipment(self, body: Any) -> Shipment:
        """Create a shipment using either recipientAddressID or an inline recipientAddress.
        Returns a typed Shipment model.
        """
        payload = body.model_dump(exclude_none=True) if hasattr(body, 'model_dump') else body
        if isinstance(payload.get("order"), dict):
            if not payload["order"].get("sourceCode"):
                payload["order"]["sourceCode"] = "API"
        if isinstance(payload.get('recipientAddress'), dict) and not payload['recipientAddress'].get('phone'):
            raise ValueError('recipientAddress.phone is required')
        for key in ("length","width","height","weight"):
            if key in payload and payload[key] is not None:
                payload[key] = str(payload[key])
        return Shipment.model_validate(self._request("POST", "/shipments", json_body=payload))

    def get_shipment(self, shipment_id: str) -> Shipment:
        return Shipment.model_validate(self._request("GET", f"/shipments/{shipment_id}"))

    def list_shipments(self, params: Optional[ListParams] = None) -> ShipmentsListResponse:
        p = params.model_dump(exclude_none=True) if isinstance(params, ListParams) else (params or {})
        data = self._request("GET", "/shipments", params=p)
        return ShipmentsListResponse.model_validate({**data, "data": data.get("data", [])})

    def iter_shipments(self, params: Optional[ListParams] = None) -> Iterator[Shipment]:
        p = params.model_dump(exclude_none=True) if isinstance(params, ListParams) else (params or {})
        page = 1
        while True:
            resp = self._request("GET", "/shipments", params={**p, "page": page})
            items = resp.get("data", [])
            for it in items:
                yield Shipment.model_validate(it)
            total_pages = resp.get("totalPages") or 0
            if not total_pages or page >= int(total_pages):
                break
            page += 1

    def update_package(self, shipment_id: str, body: Any) -> Shipment:
        payload = body.model_dump(exclude_none=True) if hasattr(body, 'model_dump') else body
        for key in ("length","width","height","weight"):
            if key in payload and payload[key] is not None:
                payload[key] = str(payload[key])
        return Shipment.model_validate(self._request("PATCH", f"/shipments/{shipment_id}", json_body=payload))

    def cancel_shipment(self, shipment_id: str) -> Shipment:
        return Shipment.model_validate(self._request("DELETE", f"/shipments/{shipment_id}"))

    def clone_shipment(self, shipment_id: str) -> Shipment:
        return Shipment.model_validate(self._request("POST", f"/shipments/{shipment_id}"))

    def create_return_shipment(self, shipment_id: str, body: Any) -> Shipment:
        payload = body.model_dump(exclude_none=True) if hasattr(body, 'model_dump') else body
        payload["isReturn"] = True
        return Shipment.model_validate(self._request("PATCH", f"/shipments/{shipment_id}", json_body=payload))

    def create_shipment_test(self, body: Any) -> Shipment:
        payload = body.model_dump(exclude_none=True) if hasattr(body, 'model_dump') else dict(body)
        if isinstance(payload.get("order"), dict):
            if not payload["order"].get("sourceCode"):
                payload["order"]["sourceCode"] = "API"
        if isinstance(payload.get('recipientAddress'), dict) and not payload['recipientAddress'].get('phone'):
            raise ValueError('recipientAddress.phone is required')
        for key in ("length","width","height","weight"):
            if key in payload and payload[key] is not None:
                payload[key] = str(payload[key])
        payload["test"] = True
        return Shipment.model_validate(self._request("POST", "/shipments", json_body=payload))

    # ---- resources: transactions ----
    def accept_offer(self, offer_id: str) -> Transaction:
        """Accept an offer (purchase label). Returns a Transaction with the last updated Shipment
        including barcode, labelURL, and tracking metadata.
        """
        return Transaction.model_validate(self._request("POST", "/transactions", json_body={"offerID": offer_id}))

    def create_transaction(self, body: Any) -> Transaction:
        """One-step label purchase. Post shipment details directly to /transactions.
        Body follows create_shipment fields (recipientAddress or recipientAddressID, dimensions as strings).
        """
        raw = body.model_dump(exclude_none=True) if hasattr(body, 'model_dump') else dict(body)
        payload: Dict[str, Any]
        wrapper_in: Optional[Dict[str, Any]] = None
        if isinstance(raw.get("shipment"), dict):
            wrapper_in = raw
            payload = dict(raw.get("shipment") or {})
        else:
            payload = raw

        if isinstance(payload.get("order"), dict) and not payload["order"].get("sourceCode"):
            payload["order"]["sourceCode"] = "API"
        if isinstance(payload.get('recipientAddress'), dict) and not payload['recipientAddress'].get('phone'):
            raise ValueError('recipientAddress.phone is required')
        for key in ("length","width","height","weight"):
            if key in payload and payload[key] is not None:
                payload[key] = str(payload[key])

        wrapper: Dict[str, Any] = {"shipment": payload}
        provider_account_id = (wrapper_in or {}).get("providerAccountID") if wrapper_in else None
        if provider_account_id is None:
            provider_account_id = payload.pop("providerAccountID", None)
        else:
            payload.pop("providerAccountID", None)
        if provider_account_id is not None:
            wrapper["providerAccountID"] = provider_account_id

        provider_service_code = (wrapper_in or {}).get("providerServiceCode") if wrapper_in else None
        if provider_service_code is None:
            provider_service_code = payload.pop("providerServiceCode", None)
        else:
            payload.pop("providerServiceCode", None)
        if provider_service_code is not None:
            wrapper["providerServiceCode"] = provider_service_code

        return Transaction.model_validate(self._request("POST", "/transactions", json_body=wrapper))

    # ---- helpers ----
    # Removed wait_for_offers helper; prefer webhooks or manual lightweight polling in tests.

    def wait_for_tracking_number(self, shipment_id: str, interval: float = 3.0, timeout: float = 180.0) -> Shipment:
        """Poll the shipment until a trackingNumber is available or timeout."""
        import time
        start = time.time()
        while True:
            s = self.get_shipment(shipment_id)
            if getattr(s, 'trackingNumber', None):
                return s
            if time.time() - start > timeout:
                raise TimeoutError('Timed out waiting for tracking number')
            time.sleep(interval)

    # ---- resources: addresses ----
    def create_address(self, body: Any) -> dict:
        payload = body.model_dump(exclude_none=True) if hasattr(body, 'model_dump') else body
        return self._request("POST", "/addresses", json_body=payload)

    def create_sender_address(self, body: dict) -> dict:
        data = dict(body)
        if not data.get('phone'):
            raise ValueError('phone is required for sender addresses')
        if not data.get('zip'):
            raise ValueError('zip is required for sender addresses')
        data["isRecipientAddress"] = False
        return self.create_address(data)

    def create_recipient_address(self, body: dict) -> dict:
        data = dict(body)
        if not data.get('phone'):
            raise ValueError('phone is required for recipient addresses')
        data["isRecipientAddress"] = True
        return self.create_address(data)

    def list_addresses(self, is_recipient_address: bool | None = None, limit: int | None = None, page: int | None = None) -> AddressesListResponse:
        params = {"isRecipientAddress": is_recipient_address, "limit": limit, "page": page}
        data = self._request("GET", "/addresses", params={k: v for k, v in params.items() if v is not None})
        return AddressesListResponse.model_validate({**data, "data": data.get("data", [])})

    def get_address(self, address_id: str) -> Address:  # type: ignore[name-defined]
        from .models import Address as AddressModel  # avoid circular import hints
        data = self._request("GET", f"/addresses/{address_id}")
        return AddressModel.model_validate(data)

    def delete_address(self, address_id: str) -> dict:
        return self._request("DELETE", f"/addresses/{address_id}")

    # ---- resources: webhooks ----
    def create_webhook(self, url: str, type: str | None = None) -> dict:
        payload = {"url": url}
        if type:
            payload["type"] = type
        return self._request("POST", "/webhook", json_body=payload)

    def list_webhooks(self) -> WebhooksListResponse:
        data = self._request("GET", "/webhook")
        return WebhooksListResponse.model_validate({**data, "data": data.get("data", [])})

    def delete_webhook(self, webhook_id: str) -> dict:
        return self._request("DELETE", f"/webhook/{webhook_id}")

    def test_webhook(self, type: str, url: str) -> dict:
        return self._request("PUT", "/webhook", json_body={"type": type, "url": url})

    # ---- label downloads ----
    def download_label_by_url(self, url: str) -> bytes:
        res = httpx.get(url)
        res.raise_for_status()
        return res.content

    def download_label_for_shipment(self, shipment_id: str) -> bytes:
        s = self.get_shipment(shipment_id)
        url = getattr(s, 'labelURL', None)
        if not url:
            raise GeliverError('Shipment has no labelURL')
        return self.download_label_by_url(url)

    def download_responsive_label_by_url(self, url: str) -> str:
        res = httpx.get(url)
        res.raise_for_status()
        return res.text

    def download_responsive_label_for_shipment(self, shipment_id: str) -> str:
        s = self.get_shipment(shipment_id)
        url = getattr(s, 'responsiveLabelURL', None) or getattr(s, 'responsiveLabelUrl', None)
        if not url:
            raise GeliverError('Shipment has no responsiveLabelURL')
        return self.download_responsive_label_by_url(url)

    # ---- parcel templates ----
    def create_parcel_template(self, body: dict) -> dict:
        return self._request("POST", "/parceltemplates", json_body=body)

    def list_parcel_templates(self) -> ParcelTemplatesListResponse:
        data = self._request("GET", "/parceltemplates")
        return ParcelTemplatesListResponse.model_validate({**data, "data": data.get("data", [])})

    def delete_parcel_template(self, template_id: str) -> dict:
        return self._request("DELETE", f"/parceltemplates/{template_id}")

    # ---- prices ----
    def list_prices(self, *, paramType: str, length: str, width: str, height: str, weight: str, distanceUnit: str | None = None, massUnit: str | None = None) -> dict:
        params = {
            "paramType": paramType,
            "length": length,
            "width": width,
            "height": height,
            "weight": weight,
            "distanceUnit": distanceUnit,
            "massUnit": massUnit,
        }
        return self._request("GET", "/priceList", params={k: v for k, v in params.items() if v is not None})

    # ---- providers ----
    def list_provider_accounts(self) -> ProviderAccountsListResponse:
        data = self._request("GET", "/provideraccounts")
        return ProviderAccountsListResponse.model_validate({**data, "data": data.get("data", [])})

    def create_provider_account(self, body: dict) -> dict:
        return self._request("POST", "/provideraccounts", json_body=body)

    def delete_provider_account(self, provider_account_id: str, *, is_delete_account_connection: bool | None = None) -> dict:
        params = {"isDeleteAccountConnection": is_delete_account_connection} if is_delete_account_connection is not None else None
        return self._request("DELETE", f"/provideraccounts/{provider_account_id}", params=params)

    # ---- geo ----
    def list_cities(self, country_code: str) -> CitiesListResponse:
        data = self._request("GET", "/cities", params={"countryCode": country_code})
        return CitiesListResponse.model_validate({**data, "data": data.get("data", [])})

    def list_districts(self, country_code: str, city_code: str) -> DistrictsListResponse:
        data = self._request("GET", "/districts", params={"countryCode": country_code, "cityCode": city_code})
        return DistrictsListResponse.model_validate({**data, "data": data.get("data", [])})

    # ---- organizations ----
    def get_balance(self, organization_id: str) -> dict:
        return self._request("GET", f"/organizations/{organization_id}/balance")
