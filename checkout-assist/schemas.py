"""Tool schemas for Checkout Assist."""

CHECKOUT_ASSIST_START = {
    "name": "checkout_assist_start",
    "description": (
        "Launch a visible Chromium window controlled through Playwright for a user-approved shopping URL. "
        "Use this to prepare a purchase while the user watches. It never enters passwords, one-time codes, "
        "card data, or submits payment."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Approved product or store URL to open."},
        },
        "required": ["url"],
    },
}

CHECKOUT_ASSIST_STEP = {
    "name": "checkout_assist_step",
    "description": (
        "Perform one non-sensitive Playwright action in the visible Checkout Assist browser. "
        "Allowed actions are navigate, click, fill, and snapshot. Refuse password, payment, 2FA, banking, "
        "or final-order submission steps."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["navigate", "click", "fill", "snapshot"]},
            "selector": {"type": "string", "description": "CSS selector for click or fill."},
            "url": {"type": "string", "description": "URL for navigate."},
            "text": {"type": "string", "description": "Text for fill. Never use for secrets or payment data."},
        },
        "required": ["action"],
    },
}

CHECKOUT_ASSIST_STATUS = {
    "name": "checkout_assist_status",
    "description": "Show whether the visible Checkout Assist Chromium/Playwright session is running and its current URL/title.",
    "parameters": {"type": "object", "properties": {}},
}
