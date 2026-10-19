# Checkout Assist

A Hermes plugin that opens a visible Chromium/Chrome window with a persistent profile and lets Hermes automate non-sensitive shopping steps through Playwright/CDP.

## Install on macOS

1. Unzip this archive.
2. Copy the `checkout-assist` folder to `~/.hermes/plugins/checkout-assist/`.
3. In Terminal, run:

   ```bash
   hermes plugins enable checkout-assist
   ```

4. In Hermes Desktop: **Settings → Plugins**, enable **Checkout Assist**; then use **⌘K → Reload desktop plugins**.
5. Start a new Hermes chat. Ask: `iniciar Checkout Assist com <URL>`.

## Safety

The tools refuse password, 2FA, card/bank, Pix, and final payment submission fields. The user must complete authentication and payment.

## Dependency

The first use downloads/runs the Playwright Node package through `npx`. Google Chrome or Chromium must be installed in `/Applications`.
