import json
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import CodeBlock
from .forms import CodeBlockTesterAdminForm


class AdminCodeBlockTester(UserPassesTestMixin, View):
    template_name = 'admin/codeblocks/code_block_tester.html'
    default_context = {
        'title': 'Code Block Tester',
        'has_permission': True,
    }

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('admin:index'))

    def get(self, request):
        codeblock = CodeBlock()
        form = CodeBlockTesterAdminForm(instance=codeblock)

        return render(request, self.template_name, {
            'form': form,
            **self.default_context
        })

    def post(self, request):
        form = CodeBlockTesterAdminForm(request.POST, instance=CodeBlock())
        codeblock = form.save(commit=False)
        codeblock.run_source_code(save=False)
        run_result = codeblock.run_result_summary()
        del run_result['run_count']
        del run_result['is_expecting_output']
        del run_result['last_run']

        return render(request, self.template_name, {
            'form': form,
            'run_result': json.dumps(run_result, indent=4),
            **self.default_context
        })
