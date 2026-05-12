"""
mock_bank_gateway.py — A fake bank payment portal served locally.

MockBank._get_gateway_payment_url_parameter() points here.
The go_to_bank_gateway proxy delivers the user to this view with GET params.

GET params supplied by MockBank._get_gateway_payment_parameter():
    tc            tracking code
    amount        amount in IRR
    callback      client callback URL
    sender        sender display name (optional)
    sender_bank   sender bank name (optional)
    receiver      receiver display name (optional)
    receiver_bank receiver bank name (optional)

The "Confirm Payment" button redirects to:
    {callback}&mock_status=SUCCESS&tc={tc}

The "Cancel" button redirects to:
    {callback}&mock_status=CANCEL&tc={tc}
"""

from django.http import HttpResponse


_PAGE = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Mock Bank Gateway — Sandbox</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }}
  .card {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    max-width: 480px;
    width: 100%;
    padding: 2.5rem 2rem;
    box-shadow: 0 24px 48px rgba(0,0,0,.5);
  }}
  .badge {{
    display: inline-block;
    background: #1f3a2b;
    color: #3fb950;
    border: 1px solid #238636;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .05em;
    padding: .25rem .8rem;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
  }}
  h1 {{
    font-size: 1.4rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: .4rem;
  }}
  .subtitle {{
    font-size: .875rem;
    color: #8b949e;
    margin-bottom: 2rem;
  }}
  .detail-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: .75rem 1.5rem;
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1.25rem 1rem;
    margin-bottom: 2rem;
    font-size: .875rem;
  }}
  .detail-grid .lbl {{ color: #8b949e; }}
  .detail-grid .val {{
    color: #e6edf3;
    font-weight: 600;
    word-break: break-all;
  }}
  .amount-row {{
    grid-column: 1 / -1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: .5rem;
    border-top: 1px solid #21262d;
    margin-top: .25rem;
  }}
  .amount-row .val {{
    font-size: 1.25rem;
    color: #58a6ff;
  }}
  .sep {{
    height: 1px;
    background: #21262d;
    margin: .5rem 0;
    grid-column: 1 / -1;
  }}
  .actions {{
    display: flex;
    gap: 1rem;
  }}
  .btn {{
    flex: 1;
    padding: .75rem 1rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity .15s, transform .1s;
    text-decoration: none;
    text-align: center;
  }}
  .btn:active {{ transform: scale(.97); }}
  .btn-confirm {{
    background: #238636;
    color: #fff;
  }}
  .btn-confirm:hover {{ opacity: .88; }}
  .btn-cancel {{
    background: #21262d;
    color: #f85149;
    border: 1px solid #f85149;
  }}
  .btn-cancel:hover {{ background: #2d1215; }}
  .footer {{
    margin-top: 1.75rem;
    font-size: .72rem;
    color: #484f58;
    text-align: center;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="badge">⚙ Sandbox — Mock Bank</div>
  <h1>Payment Confirmation</h1>
  <p class="subtitle">This is a simulated bank gateway. No real transaction will occur.</p>

  <div class="detail-grid">
    <span class="lbl">Tracking Code</span>
    <span class="val">{tc}</span>

    <div class="sep"></div>

    <span class="lbl">Sender</span>
    <span class="val">{sender}</span>

    <span class="lbl">Sender Bank</span>
    <span class="val">{sender_bank}</span>

    <div class="sep"></div>

    <span class="lbl">Receiver</span>
    <span class="val">{receiver}</span>

    <span class="lbl">Receiver Bank</span>
    <span class="val">{receiver_bank}</span>

    <div class="amount-row">
      <span class="lbl" style="font-size:.875rem">Amount (IRR)</span>
      <span class="val">{amount_fmt}</span>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-confirm" href="{confirm_url}">✓ Confirm Payment</a>
    <a class="btn btn-cancel"  href="{cancel_url}">✕ Cancel</a>
  </div>

  <p class="footer">Mock Bank Sandbox &bull; az-iranian-bank-gateways &bull; For development only</p>
</div>
</body>
</html>"""


def mock_bank_gateway_view(request):
    tc           = request.GET.get("tc", "")
    amount       = request.GET.get("amount", "0")
    callback     = request.GET.get("callback", "")
    sender       = request.GET.get("sender",       "علیرضا گلبایگانی  /  Alireza Golpaiganie")
    sender_bank  = request.GET.get("sender_bank",  "Saderat Bank")
    receiver     = request.GET.get("receiver",     "محمدعلی دهقان شورباخلو  /  Mohammad Ali Dehghan")
    receiver_bank = request.GET.get("receiver_bank", "Refah Bank")

    # format amount with commas
    try:
        amount_fmt = f"{int(amount):,}"
    except (ValueError, TypeError):
        amount_fmt = amount

    sep = "&" if "?" in callback else "?"

    confirm_url = f"{callback}{sep}mock_status=SUCCESS&tc={tc}"
    cancel_url  = f"{callback}{sep}mock_status=CANCEL&tc={tc}"

    html = _PAGE.format(
        tc=tc,
        sender=sender,
        sender_bank=sender_bank,
        receiver=receiver,
        receiver_bank=receiver_bank,
        amount_fmt=amount_fmt,
        confirm_url=confirm_url,
        cancel_url=cancel_url,
    )
    return HttpResponse(html, content_type="text/html; charset=utf-8")
