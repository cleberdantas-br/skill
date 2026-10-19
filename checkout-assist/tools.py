"""Visible Chromium + Playwright CDP bridge for assisted checkout."""
from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("PLUGIN_DATA", PLUGIN_DIR / "data"))
PROFILE_DIR = DATA_DIR / "chromium-profile"
PORT = 9225
STATE_PATH = DATA_DIR / "session.json"

SENSITIVE = ("password", "senha", "cvv", "card", "cartao", "cartão", "otp", "2fa", "token", "pix", "payment", "pagamento")
FINALIZE = ("finalizar", "confirmar pedido", "place order", "pagar", "pay now")


def _result(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


def _chrome_binary() -> str | None:
    candidates = list(Path("/root/.agent-browser/browsers").glob("chrome-*/chrome"))
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    for candidate in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ):
        if Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def _cdp_info() -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1.5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def _node(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Run a short Playwright CDP interaction without shell interpolation."""
    DATA_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    request_path = DATA_DIR / "request.json"
    request_path.write_text(json.dumps({"action": action, **payload}), encoding="utf-8")
    script = r'''
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const req = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9225');
  const contexts = browser.contexts();
  const pages = contexts.flatMap(c => c.pages());
  const page = pages[pages.length - 1] || await contexts[0].newPage();
  if (req.action === 'navigate') await page.goto(req.url, {waitUntil:'domcontentloaded', timeout:30000});
  if (req.action === 'click') await page.locator(req.selector).first().click({timeout:15000});
  if (req.action === 'fill') await page.locator(req.selector).first().fill(req.text, {timeout:15000});
  await page.waitForTimeout(400);
  const result = {url: page.url(), title: await page.title(), text: (await page.locator('body').innerText()).slice(0, 4000)};
  console.log(JSON.stringify(result));
  await browser.close();
})().catch(error => { console.error(error.stack || String(error)); process.exit(1); });
'''
    script_path = DATA_DIR / "bridge.cjs"
    script_path.write_text(script, encoding="utf-8")
    completed = subprocess.run(
        ["npx", "-y", "-p", "playwright", "node", str(script_path), str(request_path)],
        text=True, capture_output=True, timeout=90,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "Playwright bridge failed")
    return json.loads(completed.stdout)


def checkout_assist_start(url: str) -> str:
    if not url.startswith(("https://", "http://")):
        return _result({"ok": False, "error": "Only http(s) URLs are allowed."})
    running = _cdp_info()
    if not running:
        chrome = _chrome_binary()
        if not chrome:
            return _result({"ok": False, "error": "No Chromium binary was found. Install a Chromium-family browser first."})
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            return _result({"ok": False, "error": "No graphical display is available for a visible browser. Run this from the Hermes Desktop host session."})
        PROFILE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        log = open(DATA_DIR / "chromium.log", "a", encoding="utf-8")
        process = subprocess.Popen(
            [chrome, f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE_DIR}", "--no-first-run", "--no-default-browser-check", url],
            stdout=log, stderr=log, start_new_session=True,
        )
        for _ in range(30):
            time.sleep(0.5)
            running = _cdp_info()
            if running:
                break
        if not running:
            return _result({"ok": False, "error": "Chromium launched but CDP did not become ready. See chromium.log.", "pid": process.pid})
    try:
        view = _node("snapshot", {})
        STATE_PATH.write_text(json.dumps({"started": time.time(), "url": view["url"]}), encoding="utf-8")
        return _result({"ok": True, "message": "Visible checkout browser is ready. The assistant can now take non-sensitive steps while you watch.", **view})
    except Exception as exc:
        return _result({"ok": False, "error": str(exc)})


def checkout_assist_step(action: str, selector: str | None = None, url: str | None = None, text: str | None = None) -> str:
    if action == "fill":
        candidate = f"{selector or ''} {text or ''}".lower()
        if any(word in candidate for word in SENSITIVE):
            return _result({"ok": False, "error": "Refusing to fill a password, payment, banking, or verification field."})
    if action == "click" and any(word in (selector or "").lower() for word in FINALIZE):
        return _result({"ok": False, "error": "Refusing a final-order or payment submission control."})
    if action == "navigate" and not (url or "").startswith(("https://", "http://")):
        return _result({"ok": False, "error": "navigate requires an http(s) URL."})
    if not _cdp_info():
        return _result({"ok": False, "error": "No running Checkout Assist browser. Start one first."})
    try:
        payload = {"selector": selector, "url": url, "text": text}
        result = _node(action, payload)
        return _result({"ok": True, **result})
    except Exception as exc:
        return _result({"ok": False, "error": str(exc)})


def checkout_assist_status() -> str:
    info = _cdp_info()
    if not info:
        return _result({"running": False, "message": "No Checkout Assist browser is running."})
    try:
        view = _node("snapshot", {})
        return _result({"running": True, **view})
    except Exception as exc:
        return _result({"running": True, "error": str(exc)})
