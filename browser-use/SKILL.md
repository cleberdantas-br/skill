---
name: browser-use
description: Control a user's local Chrome through Browser Use CDP.
version: 0.1.0
author: Cleber Dantas (cleberdantas-br), Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [browser, chrome, cdp, automation, browser-use]
    related_skills: [autonomous-ai-agents:computer-use]
---

# Browser Use for Hermes

Use Browser Use to operate the user's local Chrome through CDP. This is for interactive, JavaScript-heavy, logged-in, or bot-protected sites where a normal web fetch is insufficient. It controls the Chrome visible on the same Mac as the local Hermes gateway.

This skill is based on Browser Use's official Browser Harness workflow. It does not bypass website security, passwords, MFA, payment confirmation, or CAPTCHAs.

## When to Use

- The user asks the agent to open, navigate, fill, or click through a website in their local Chrome.
- The task needs an existing signed-in browser session or rendered JavaScript.
- The user wants to watch the browsing task in Chrome.
- A direct page fetch has failed or cannot perform the interaction.

Do not use for public pages that can be read with `web_extract` or `web_search`. Do not use a cloud browser unless the user explicitly chooses it and Browser Use Cloud is authenticated.

## Prerequisites

- macOS, Google Chrome or Chromium, and a **local** Hermes gateway on the same Mac.
- Python 3.12 and `uv`.
- Browser Use CLI installed with `terminal`:

```bash
uv tool install --python 3.12 --upgrade --force browser-use
```

- First connection may require Chrome remote-debugging approval. Keep the original Browser Use command running; in a second `terminal` call run:

```bash
browser-use mac-approve
```

If macOS reports an accessibility requirement, the user must grant Accessibility access to the app launching Browser Use (usually Terminal or Hermes) in **System Settings → Privacy & Security → Accessibility**, then run `browser-use mac-approve` once more.

## How to Run

Use `terminal` for Browser Use commands. Start with one normal local daemon and reuse it across the task. Do not create extra browser instances or duplicate tabs without a reason.

```bash
browser-use <<'PY'
new_tab('https://example.com')
wait_for_load()
print(page_info())
PY
```

On later turns, inspect existing tabs before navigating:

```bash
browser-use <<'PY'
print(list_tabs())
print(page_info())
PY
```

Use accessibility data to identify controls, click, then verify the expected page state:

```bash
browser-use <<'PY'
ax = cdp('Accessibility.getFullAXTree')['nodes']
for n in ax:
    if n.get('role', {}).get('value') == 'button':
        print(n.get('name', {}).get('value'), n.get('backendDOMNodeId'))
PY
```

## Procedure

1. Confirm the task needs browser interaction and that the local Mac gateway is being used. Completion: the target is not merely a fetchable public page.
2. Check the CLI and Chrome connection with `terminal(command="browser-use --doctor")`. Completion: the daemon is healthy or the precise setup issue is known.
3. Reuse a matching tab from `list_tabs()`; otherwise call `new_tab(url)` once. Completion: `page_info()` identifies the expected page.
4. Inspect controls through the accessibility tree, perform one action at a time, and verify after each action. Completion: observed page state matches the requested step.
5. Pause before credentials, account selection ambiguity, passwords, MFA/2FA, card/bank/Pix details, CAPTCHA resolution, or final order submission. Completion: tell the user exactly what needs their action.
6. Keep the tab open when the user needs to review or finish it. Close only task-created tabs that are no longer needed.

## Safety Rules

- Never enter, request, copy, or expose passwords, one-time codes, card details, CVV, bank credentials, or Pix payment data.
- Do not click buttons that submit or confirm a final order, payment, transfer, subscription, or account deletion unless the user gives explicit confirmation immediately before that click.
- Stop on login walls unless Chrome already has an unambiguous active session and no password, MFA, or consent step is required.
- Do not evade CAPTCHAs, bot checks, access controls, or website terms.
- Do not call `activate_tab()` unless the user explicitly asks to foreground or visibly switch Chrome tabs.

## Pitfalls

- Browser Use controls Chrome only when it runs on the same Mac as Chrome. A remote Hermes gateway cannot open or control the user's local Chrome.
- A macOS remote-debugging prompt is normal on first use. Preserve the original command and use `browser-use mac-approve`; do not start a second daemon.
- Local Chrome is one shared browser lane. Serialize browser interactions rather than having multiple agents switch tabs simultaneously.
- If the daemon becomes stale, run `browser-use --doctor` before restarting anything.

## Verification

- `browser-use --doctor` reports a usable Browser Use installation.
- `page_info()` confirms the expected URL and page title after navigation.
- Each click or fill has a page-state check rather than being assumed successful.
- The user can see the relevant Chrome tab and completes any sensitive or payment step personally.
