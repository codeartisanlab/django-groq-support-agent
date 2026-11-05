import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .ai_agent import process_agent_query

def chat_view(request):
    return render(request, 'ai_aupport/chat.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat_endpoint(request):
    try:
        body = json.loads(request.body)
        user_text = body.get('message', '').strip()

        if not user_text:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        ai_response = process_agent_query(user_text)
        return JsonResponse({'reply': ai_response})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)