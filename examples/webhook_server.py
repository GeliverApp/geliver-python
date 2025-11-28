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
