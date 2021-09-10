from django.contrib import admin

from .models import CodeBlock
from .forms import CodeBlockAdminForm


@admin.register(CodeBlock)
class CodeBlockAdmin(admin.ModelAdmin):
    list_filter = ('language',)
    list_display = ('id', 'language', 'run_count', 'last_run',)
    fields = (
        'language',
        'block_1_code',
        'block_1_ro',
        'block_2_code',
        'block_2_ro',
        'block_3_code',
        'block_3_ro',
        'expected_output',
        'run_result',
        'run_count',
        'last_run',
    )
    form = CodeBlockAdminForm

    def response_change(self, request, obj):
        if 'run' in request.GET:
            obj.run_source_code()
        return super().response_change(request, obj)
