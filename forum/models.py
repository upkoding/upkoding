from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.timezone import now
from sorl.thumbnail import ImageField, get_thumbnail

from account.models import User
from projects.models import Project
from .managers import ThreadAnswerManager


def topic_image(instance, filename):
    """
    Custom image path: forum/topics/123455678-hello-world.png
    """
    ts = int(now().timestamp())
    return 'forum/topics/{}-{}'.format(ts, filename)


class Topic(models.Model):
    TYPE_PROJECT = 0
    TYPE_CUSTOM = 1
    TYPES = (
        (TYPE_PROJECT, 'Project'),
        (TYPE_CUSTOM, 'Custom'),
    )

    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active'),
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    type = models.PositiveSmallIntegerField(
        'Type',
        choices=TYPES,
        default=TYPE_CUSTOM,
        db_index=True)
    status = models.PositiveSmallIntegerField(
        'Status',
        choices=STATUSES,
        default=STATUS_ACTIVE)
    project = models.OneToOneField(
        Project,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='forum_topic')
    description = models.TextField(blank=True, default='')
    thread_count = models.IntegerField(default=0)
    image = ImageField(
        upload_to=topic_image,
        blank=True,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-thread_count']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum:topic_detail', args=[self.slug, ])

    def image_url(self, size=64):
        """
        If topic have image, use it. Otherwise generate from default Gravatar image.
        """
        if self.image:
            return get_thumbnail(self.image, '{}x{}'.format(size, size), crop='center', quality=99).url
        return 'https://www.gravatar.com/avatar/{}?d=identicon&f=y&s={}'.format(self.pk, size)

    def inc_thread_count(self):
        self.thread_count = models.F('thread_count') + 1
        self.save()


class Thread(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True, db_index=True)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='forum_threads')
    description = models.TextField()
    status = models.PositiveSmallIntegerField(
        'Status',
        choices=STATUSES,
        default=STATUS_ACTIVE,
        db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum:thread_detail', args=[self.topic.slug, self.slug, self.pk])

    def add_participant(self, user: User):
        return ThreadParticipant.objects.get_or_create(thread=self, user=user)

    def inc_stat(self, stat_type: int):
        ThreadStat.inc_value(self, stat_type)


class ThreadStat(models.Model):
    TYPE_VIEW_COUNT = 0
    TYPE_ANSWER_COUNT = 1
    TYPES = (
        (TYPE_VIEW_COUNT, 'View Count'),
        (TYPE_ANSWER_COUNT, 'Answer Count'),
    )
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    type = models.SmallIntegerField(
        choices=TYPES,
        default=TYPE_VIEW_COUNT,
        db_index=True)
    value = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['thread', 'type'],
                name='forum_thread_stat_unique_thread_type')
        ]

    @classmethod
    def inc_value(cls, thread: Thread, stat_type: int):
        val, _ = cls.objects.get_or_create(thread=thread, type=stat_type)
        val.value = models.F('value') + 1
        val.save()


class ThreadParticipant(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'thread'],
                name='forum_thread_participant_unique_user_thread')
        ]

    def __str__(self):
        return '{} @ {}'.format(self.user.username, self.thread.title)


class ThreadAnswer(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active'),
    )

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='replies')
    status = models.PositiveSmallIntegerField(
        'Status',
        choices=STATUSES,
        default=STATUS_ACTIVE,
        db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ThreadAnswerManager()

    class Meta:
        ordering = ['pk']

    def owned_by(self, user):
        return self.user == user

    def add_participant(self, user: User):
        return ThreadAnswerParticipant.objects.get_or_create(thread_answer=self, user=user)

    def inc_stat(self, stat_type: int):
        ThreadAnswerStat.inc_value(self, stat_type)


class ThreadAnswerStat(models.Model):
    TYPE_REPLY_COUNT = 0
    TYPE_LIKE_COUNT = 1
    TYPES = (
        (TYPE_REPLY_COUNT, 'Reply Count'),
        (TYPE_LIKE_COUNT, 'Like Count'),
    )
    thread_answer = models.ForeignKey(ThreadAnswer, on_delete=models.CASCADE)
    type = models.SmallIntegerField(
        choices=TYPES,
        default=TYPE_REPLY_COUNT,
        db_index=True)
    value = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['thread_answer', 'type'],
                name='forum_thread_answer_stat_unique_thread_answer_type')
        ]

    @classmethod
    def inc_value(cls, thread_answer: ThreadAnswer, stat_type: TYPES):
        val, _ = cls.objects.get_or_create(thread_answer=thread_answer, type=stat_type)
        val.value = models.F('value') + 1
        val.save()


class ThreadAnswerParticipant(models.Model):
    thread_answer = models.ForeignKey(ThreadAnswer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'thread_answer'],
                name='forum_thread_answer_participant_unique_user_thread_answer')
        ]

    def __str__(self):
        return '{} @ {}'.format(self.user.username, self.thread_answer.pk)
