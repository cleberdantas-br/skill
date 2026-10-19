# Hermes Checkout Assist

A Hermes plugin for assisted shopping with a visible browser. It uses Playwright/CDP for non-sensitive steps and deliberately blocks passwords, 2FA, payment details, Pix/bank transfers, and final order submission.

## Install

```bash
mkdir -p ~/.hermes/plugins
git clone https://github.com/cleberdantas-br/skill.git /tmp/hermes-checkout-assist
cp -R /tmp/hermes-checkout-assist/checkout-assist ~/.hermes/plugins/checkout-assist
hermes plugins enable checkout-assist
```

Then restart Hermes Desktop or run **Reload desktop plugins** from the command palette.

Google Chrome or Chromium is required. The first run may download Playwright via `npx`.
