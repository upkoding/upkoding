from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from sorl.thumbnail import ImageField, get_thumbnail

from account.models import User
from .managers import TopicManager, ThreadAnswerManager


def topic_image(instance, filename):
    """
    Custom image path: forum/topics/123455678-hello-world.png
    """
    ts = int(now().timestamp())
    return "forum/topics/{}-{}".format(ts, filename)


class Topic(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="forum_topics"
    )

    # so we can have topic for many content types: Project, Class, Tutorial, Custom
    # BUT there should be only single topic for content_type and content_id combination.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "content_id")

    status = models.PositiveSmallIntegerField(
        "Status", choices=STATUSES, default=STATUS_ACTIVE
    )

    description = models.TextField(blank=True, default="")
    thread_count = models.IntegerField(default=0)
    image = ImageField(upload_to=topic_image, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TopicManager()

    class Meta:
        ordering = ["-thread_count"]
        # single topic for content_type and content_id combination
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "content_id"],
                name="forum_topic_unique_content_type_id",
            )
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "forum:topic_detail",
            args=[
                self.slug,
            ],
        )

    def image_url(self, size=64):
        """
        If topic have image, use it. Otherwise generate from default Gravatar image.
        """
        if self.image:
            return get_thumbnail(
                self.image, "{}x{}".format(size, size), crop="center", quality=99
            ).url
        return "https://www.gravatar.com/avatar/{}?d=identicon&f=y&s={}".format(
            self.pk, size
        )

    def inc_thread_count(self):
        self.thread_count = models.F("thread_count") + 1
        self.save()


class Thread(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True, db_index=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="threads")
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="forum_threads"
    )
    description = models.TextField()
    status = models.PositiveSmallIntegerField(
        "Status", choices=STATUSES, default=STATUS_ACTIVE, db_index=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TopicManager()

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "forum:thread_detail", args=[self.topic.slug, self.slug, self.pk]
        )

    def add_participant(self, user: User):
        return ThreadParticipant.objects.get_or_create(thread=self, user=user)

    def inc_stat(self, stat_type: int):
        ThreadStat.inc_value(self, stat_type)

    def get_stats(self):
        stats = ThreadStat.objects.filter(
            thread=self,
            type__in=[ThreadStat.TYPE_VIEW_COUNT, ThreadStat.TYPE_ANSWER_COUNT],
        )
        return {stat.get_type_display(): stat.value for stat in stats}


class ThreadStat(models.Model):
    TYPE_VIEW_COUNT = 0
    TYPE_ANSWER_COUNT = 1
    TYPES = (
        (TYPE_VIEW_COUNT, "view_count"),
        (TYPE_ANSWER_COUNT, "answer_count"),
    )
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    type = models.SmallIntegerField(
        choices=TYPES, default=TYPE_VIEW_COUNT, db_index=True
    )
    value = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["thread", "type"], name="forum_thread_stat_unique_thread_type"
            )
        ]

    @classmethod
    def inc_value(cls, thread: Thread, stat_type: int):
        val, _ = cls.objects.get_or_create(thread=thread, type=stat_type)
        val.value = models.F("value") + 1
        val.save()


class ThreadParticipant(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "thread"],
                name="forum_thread_participant_unique_user_thread",
            )
        ]

    def __str__(self):
        return "{} @ {}".format(self.user.username, self.thread.title)

    @classmethod
    def subscribed_to(cls, thread: Thread, exclude: User = None):
        """Returns subscribed participants."""
        if exclude:
            return (
                cls.objects.select_related("user")
                .filter(thread=thread, subscribed=True)
                .exclude(user=exclude)
            )
        return cls.objects.select_related("user").filter(thread=thread, subscribed=True)


class ThreadAnswer(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    )

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies"
    )
    status = models.PositiveSmallIntegerField(
        "Status", choices=STATUSES, default=STATUS_ACTIVE, db_index=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ThreadAnswerManager()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.message

    def owned_by(self, user):
        return self.user == user

    def add_participant(self, user: User):
        return ThreadAnswerParticipant.objects.get_or_create(
            thread_answer=self, user=user
        )

    def inc_stat(self, stat_type: int):
        ThreadAnswerStat.inc_value(self, stat_type)

    def get_stats(self):
        stats = ThreadAnswerStat.objects.filter(
            thread_answer=self,
            type__in=[
                ThreadAnswerStat.TYPE_REPLY_COUNT,
                ThreadAnswerStat.TYPE_LIKE_COUNT,
            ],
        )
        return {stat.get_type_display(): stat.value for stat in stats}


class ThreadAnswerStat(models.Model):
    TYPE_REPLY_COUNT = 0
    TYPE_LIKE_COUNT = 1
    TYPES = (
        (TYPE_REPLY_COUNT, "reply_count"),
        (TYPE_LIKE_COUNT, "like_count"),
    )
    thread_answer = models.ForeignKey(ThreadAnswer, on_delete=models.CASCADE)
    type = models.SmallIntegerField(
        choices=TYPES, default=TYPE_REPLY_COUNT, db_index=True
    )
    value = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["thread_answer", "type"],
                name="forum_thread_answer_stat_unique_thread_answer_type",
            )
        ]

    @classmethod
    def inc_value(cls, thread_answer: ThreadAnswer, stat_type: TYPES):
        val, _ = cls.objects.get_or_create(thread_answer=thread_answer, type=stat_type)
        val.value = models.F("value") + 1
        val.save()


class ThreadAnswerParticipant(models.Model):
    thread_answer = models.ForeignKey(ThreadAnswer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "thread_answer"],
                name="forum_thread_answer_participant_unique_user_thread_answer",
            )
        ]

    def __str__(self):
        return "{} @ {}".format(self.user.username, self.thread_answer.pk)

    @classmethod
    def subscribed_to(cls, thread_answer: ThreadAnswer, exclude: User = None):
        """Returns subscribed participants."""
        if exclude:
            return (
                cls.objects.select_related("user")
                .filter(thread_answer=thread_answer, subscribed=True)
                .exclude(user=exclude)
            )
        return cls.objects.select_related("user").filter(
            thread_answer=thread_answer, subscribed=True
        )
