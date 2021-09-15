from django.contrib import admin

from .models import CodeBlock
from .forms import CodeBlockAdminForm


@admin.register(CodeBlock)
class CodeBlockAdmin(admin.ModelAdmin):
    list_filter = ('language',)
    list_display = ('id', 'language', 'run_count', 'last_run',)
    fieldsets = (
        (None, {'fields': ('language',)}),
        ('Block 1', {'fields': ('block_1_ro', 'block_1_code', )}),
        ('Block 2', {'fields': ('block_2_ro', 'block_2_code', )}),
        ('Block 3', {'fields': ('block_3_ro', 'block_3_code', )}),
        ('Output and stats', {
         'fields': ('expected_output', 'run_result', 'run_count', 'last_run')})
    )
    form = CodeBlockAdminForm

    def response_change(self, request, obj):
        if 'run' in request.GET:
            obj.run_source_code()
        return super().response_change(request, obj)
