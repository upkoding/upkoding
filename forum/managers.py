from django.db import models


class ThreadAnswerManager(models.Manager):

    def active(self):
        """
        Returns active answers only.
        Usage:
            `ThreadAnswer.objects.active()`
        Which is equivalent to:
            `ThreadAnswer.objects.all(status=1)`
        """
        return self.filter(status=self.model.STATUS_ACTIVE)
