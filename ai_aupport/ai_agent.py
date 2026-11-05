import os
import json
from groq import Groq
from .models import Order

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model definition
MODEL_NAME = "openai/gpt-oss-120b"

def lookup_order_status(order_number: str) -> str:
    clean_id = order_number.strip().upper()
    try:
        order = Order.objects.get(order_number__iexact=clean_id)
        return json.dumps({
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "product": order.product_name,
            "status": order.get_status_display(),
            "total_amount": str(order.total_amount),
            "estimated_delivery": order.estimated_delivery.strftime("%d %b %Y"),
        })
    except Order.DoesNotExist:
        return json.dumps({
            "error": f"Order ID '{clean_id}' hamare system mein nahi mila. Kripya correct ID check karein."
        })

TOOL_FUNCTIONS = {
    "lookup_order_status": lookup_order_status,
}

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order_status",
            "description": "Fetch order details like live status, product name, and delivery date from the database using an order number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "The unique order reference number, e.g. ORD-1001",
                    }
                },
                "required": ["order_number"],
            },
        },
    }
]

def process_agent_query(user_message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are an intelligent customer support assistant for Code Artisan Lab's store. "
                "Be polite and reply in natural Hinglish. "
                "Whenever a customer asks about an order or delivery date, ALWAYS invoke the lookup_order_status tool."
            ),
        },
        {"role": "user", "content": user_message},
    ]

    try:
        # Step A: Primary inference call
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=GROQ_TOOLS,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=800,
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Step B: Check tool invocation
        if tool_calls:
            messages.append(response_message)

            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                if fn_name in TOOL_FUNCTIONS:
                    tool_result = TOOL_FUNCTIONS[fn_name](**fn_args)

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": fn_name,
                        "content": tool_result,
                    })

            # Step C: Final turn
            final_turn = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.3,
            )
            return final_turn.choices[0].message.content

        return response_message.content

    except Exception as exc:
        return f"Support service issue: {str(exc)}"