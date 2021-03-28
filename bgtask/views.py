from django.http import JsonResponse
from django.views.generic import View


class ApiKeyRequiredView(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TaskHandler(ApiKeyRequiredView):
    def get(self, request, key, *args, **kwargs):
        return JsonResponse({'key': key})
