import base64
from django.db import models
from django.conf import settings
from django.utils.timezone import now

from .services import Judge0
judge0_client = Judge0(api_key=settings.JUDGE0_API_KEY)


class CodeBlock(models.Model):
    """
    CodeBlock represents a runnable code that are
    splitted into smaller blocks (writable or read only)
    and will be combined into single code when passed to the evaluator.

    For simplicity we split the code into 5 blocks
    where each block can be set readonly or writable, the writable
    block is the ones that user need to fill themself.
    """
    NUM_BLOCKS = 5

    LANG_NODEJS = Judge0.LANG_NODE12
    LANG_PYTHON = Judge0.LANG_PYTHON3
    LANG_GO = Judge0.LANG_GO113
    LANG_RUBY = Judge0.LANG_RUBY2
    LANGS = [
        (LANG_NODEJS, 'javascript'),
        (LANG_PYTHON, 'python'),
        (LANG_GO, 'go'),
        (LANG_RUBY, 'ruby')
    ]

    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    STATUSES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    language = models.SmallIntegerField(
        'Language', choices=LANGS, default=LANG_NODEJS)

    # block 1
    block_1_title = models.CharField(
        '#1 Title', max_length=100, blank=True, default='')
    block_1_desc = models.TextField(
        '#1 Description', blank=True, default='', help_text='Markdown')
    block_1_hint = models.CharField(
        '#1 Hint', max_length=250, blank=True, default='')
    block_1_code = models.TextField(
        '#1 code', blank=True, default='')
    block_1_ro = models.BooleanField('#1 Readonly', default=True)

    # block 2
    block_2_title = models.CharField(
        '#2 Title', max_length=100, blank=True, default='')
    block_2_desc = models.TextField(
        '#2 Description', blank=True, default='', help_text='Markdown')
    block_2_hint = models.CharField(
        '#2 Hint', max_length=250, blank=True, default='')
    block_2_code = models.TextField(
        '#2 code', blank=True, default='')
    block_2_ro = models.BooleanField('#2 Readonly', default=True)

    # block 3
    block_3_title = models.CharField(
        '#3 Title', max_length=100, blank=True, default='')
    block_3_desc = models.TextField(
        '#3 Description', blank=True, default='', help_text='Markdown')
    block_3_hint = models.CharField(
        '#3 Hint', max_length=250, blank=True, default='')
    block_3_code = models.TextField(
        '#3 code', blank=True, default='')
    block_3_ro = models.BooleanField('#3 Readonly', default=True)

    # block 4
    block_4_title = models.CharField(
        '#4 Title', max_length=100, blank=True, default='')
    block_4_desc = models.TextField(
        '#4 Description', blank=True, default='', help_text='Markdown')
    block_4_hint = models.CharField(
        '#4 Hint', max_length=250, blank=True, default='')
    block_4_code = models.TextField(
        '#4 code', blank=True, default='')
    block_4_ro = models.BooleanField('#4 Readonly', default=True)

    # block 5
    block_5_title = models.CharField(
        '#5 Title', max_length=100, blank=True, default='')
    block_5_desc = models.TextField(
        '#5 Description', blank=True, default='', help_text='Markdown')
    block_5_hint = models.CharField(
        '#5 Hint', max_length=250, blank=True, default='')
    block_5_code = models.TextField(
        '#5 code', blank=True, default='')
    block_5_ro = models.BooleanField('#5 Readonly', default=True)

    run_count = models.IntegerField(default=0)
    run_result = models.JSONField('Result', blank=True, null=True)
    expected_output = models.TextField(blank=True, default='')

    last_run = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'#{self.pk} {self.get_language_display()}'

    def get_custom_language_display(self):
        if self.language == self.LANG_GO:
            return 'golang'
        return self.get_language_display()

    def get_blocks(self) -> list:
        blocks = []
        for i in range(1, CodeBlock.NUM_BLOCKS+1):
            title = getattr(self, f'block_{i}_title', None)
            desc = getattr(self, f'block_{i}_desc', None)
            hint = getattr(self, f'block_{i}_hint', None)
            code = getattr(self, f'block_{i}_code', None)
            readonly = getattr(self, f'block_{i}_ro', True)
            if title or desc or hint or code:
                blocks.append({
                    'block_id': i,
                    'title': title,
                    'desc': desc,
                    'hint': hint,
                    'code': code,
                    'code_md': f'```\n{code}\n```',
                    'readonly': readonly,
                })
        return blocks

    @property
    def source_code(self) -> str:
        blocks = []
        for i in range(1, CodeBlock.NUM_BLOCKS+1):
            block = getattr(self, f'block_{i}_code')
            if block:
                blocks.append(block)
        return '\n\n'.join(blocks)

    @property
    def run_status(self):
        if not self.run_result:
            return None
        return self.run_result.get('result').get('status')

    @property
    def compile_output(self) -> str:
        if not self.run_result:
            return None
        compile_output = self.run_result.get('result').get('compile_output')
        return base64.b64decode(compile_output).decode().strip() if compile_output else None

    @property
    def run_result_stderr(self) -> str:
        if not self.run_result:
            return None
        stderr = self.run_result.get('result').get('stderr')
        return base64.b64decode(stderr).decode().strip() if stderr else None

    @property
    def run_result_stdout(self) -> str:
        if not self.run_result:
            return None
        stdout = self.run_result.get('result').get('stdout')
        return base64.b64decode(stdout).decode().strip() if stdout else None

    @property
    def is_output_match(self) -> bool:
        # no run or nothing to compare with
        if not self.expected_output or not self.run_result:
            return False
        if self.expected_output and self.run_status.get('id') == Judge0.STATUS_ACCEPTED:
            return True
        return False

    @property
    def is_run_accepted(self) -> bool:
        if not self.run_result:
            return False
        if self.run_status.get('id') == Judge0.STATUS_ACCEPTED:
            return True
        return False

    @property
    def is_expecting_output(self) -> bool:
        return self.expected_output.strip() != ''

    def run_result_summary(self):
        return {
            'status': self.run_status,
            'stdout': self.run_result_stdout,
            'stderr': self.run_result_stderr,
            'compile_output': self.compile_output,
            'expected_output': self.expected_output,
            'is_expecting_output': self.is_expecting_output,
            'is_output_match': self.is_output_match,
            'run_count': self.run_count,
            'last_run': self.last_run.timestamp(),
        }

    def run_source_code(self, stdin: str = None):
        result, err = judge0_client.submit(
            language_id=self.language,
            source_code=self.source_code,
            stdin=stdin,
            expected_output=self.expected_output.strip() if self.is_expecting_output else None
        )
        self.run_result = {
            'result': result,
            'error': str(err) if err else None
        }
        self.run_count = models.F('run_count') + 1
        self.last_run = now()
        self.save()
