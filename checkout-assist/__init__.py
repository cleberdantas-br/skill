"""Hermes registration for Checkout Assist."""
from . import schemas, tools


def register(ctx):
    ctx.register_tool(
        name="checkout_assist_start",
        toolset="checkout-assist",
        schema=schemas.CHECKOUT_ASSIST_START,
        handler=tools.checkout_assist_start,
    )
    ctx.register_tool(
        name="checkout_assist_step",
        toolset="checkout-assist",
        schema=schemas.CHECKOUT_ASSIST_STEP,
        handler=tools.checkout_assist_step,
    )
    ctx.register_tool(
        name="checkout_assist_status",
        toolset="checkout-assist",
        schema=schemas.CHECKOUT_ASSIST_STATUS,
        handler=tools.checkout_assist_status,
    )
