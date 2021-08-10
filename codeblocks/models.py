from django.db import models

from account.models import User


class CodeBlock(models.Model):
    """
    CodeBlock represents a runnable code that are
    splitted into smaller blocks (writable or read only)
    and will be combined into single code when passed to the evaluator.

    For simplicity we split the code (into 5 blocks) in single model
    instead of having separate model(record) for each block, should be
    enough for common case.
    """
    LANG_NODEJS = 0
    LANGS = [
        (LANG_NODEJS, 'NodeJS'),
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
        '#1 Keterangan', blank=True, default='')
    block_1_hint = models.CharField(
        '#1 Hint', max_length=250, blank=True, default='')
    block_1_code = models.TextField(
        '#1 code', blank=True, default='')
    block_1_ro = models.BooleanField('#1 Readonly', default=True)

    # block 2
    block_2_title = models.CharField(
        '#2 Title', max_length=100, blank=True, default='')
    block_2_desc = models.TextField(
        '#2 Keterangan', blank=True, default='')
    block_2_hint = models.CharField(
        '#2 Hint', max_length=250, blank=True, default='')
    block_2_code = models.TextField(
        '#2 code', blank=True, default='')
    block_2_ro = models.BooleanField('#2 Readonly', default=True)

    # block 3
    block_3_title = models.CharField(
        '#3 Title', max_length=100, blank=True, default='')
    block_3_desc = models.TextField(
        '#3 Keterangan', blank=True, default='')
    block_3_hint = models.CharField(
        '#3 Hint', max_length=250, blank=True, default='')
    block_3_code = models.TextField(
        '#3 code', blank=True, default='')
    block_3_ro = models.BooleanField('#3 Readonly', default=True)

    # block 4
    block_4_title = models.CharField(
        '#4 Title', max_length=100, blank=True, default='')
    block_4_desc = models.TextField(
        '#4 Keterangan', blank=True, default='')
    block_4_hint = models.CharField(
        '#4 Hint', max_length=250, blank=True, default='')
    block_4_code = models.TextField(
        '#4 code', blank=True, default='')
    block_4_ro = models.BooleanField('#4 Readonly', default=True)

    # block 5
    block_5_title = models.CharField(
        '#5 Title', max_length=100, blank=True, default='')
    block_5_desc = models.TextField(
        '#5 Keterangan', blank=True, default='')
    block_5_hint = models.CharField(
        '#5 Hint', max_length=250, blank=True, default='')
    block_5_code = models.TextField(
        '#5 code', blank=True, default='')
    block_5_ro = models.BooleanField('#5 Readonly', default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def run(self):
        pass
