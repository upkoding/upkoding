from django.contrib import admin

from .models import CodeBlock
from .forms import CodeBlockAdminForm


class CodeBlockAdmin(admin.ModelAdmin):
    model = CodeBlock
    list_filter = ('status', 'language',)
    form = CodeBlockAdminForm

    def response_change(self, request, obj):
        if 'run' in request.GET:
            obj.run_source_code()
        return super().response_change(request, obj)


admin.site.register(CodeBlock, CodeBlockAdmin)