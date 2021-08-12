import base64
from django.db import models
from django.conf import settings

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
    LANGS = [
        (LANG_NODEJS, 'NodeJS'),
        (LANG_PYTHON, 'Python'),
    ]

    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    STATUSES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    status = models.SmallIntegerField(
        'Status', choices=STATUSES, default=STATUS_INACTIVE)
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

    run_result = models.JSONField('Result', blank=True, null=True)
    expected_output = models.CharField(
        'Expected output', max_length=250, blank=True, default='')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'#{self.pk} {self.get_language_display()}'

    @property
    def source_code(self) -> str:
        blocks = []
        for i in range(1, CodeBlock.NUM_BLOCKS+1):
            block = getattr(self, f'block_{i}_code')
            if block:
                blocks.append(block)
        return '\n'.join(blocks)

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
    def output_match(self) -> bool:
        # no run or nothing to compare with
        if not self.expected_output or not self.run_result:
            return False
        # run/api error
        if self.run_result and self.run_result.get('error'):
            return False
        # strerr or stdout not match
        if self.run_result_stderr or self.run_result_stdout != self.expected_output:
            return False
        return True

    def run_source_code(self, stdin: str = None):
        result, err = judge0_client.submit(
            language_id=self.language,
            source_code=self.source_code,
            stdin=stdin
        )
        self.run_result = {
            'result': result,
            'error': str(err) if err else None
        }
        self.save()
