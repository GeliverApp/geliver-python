from fastapi import FastAPI, Request
from geliver import verify_webhook

app = FastAPI()

@app.post("/webhooks/geliver")
async def webhook(req: Request):
    body = await req.body()
    ok = verify_webhook(body, req.headers, enable_verification=False)
    if not ok:
        return {"status": "invalid"}
    event = await req.json()
    # TODO: handle event
    return {"status": "ok"}

