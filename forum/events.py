from .models import Thread, ThreadStat, ThreadParticipant, ThreadAnswer, ThreadAnswerStat, ThreadAnswerParticipant


class OnThreadCreated:
    def __init__(self, thread: Thread):
        self.instance = thread
        self.user = thread.user
        self.topic = thread.topic

        # add creator as thread participant
        self.instance.add_participant(self.user)

        # increment thread_count for instance's topic
        self.topic.inc_thread_count()

        # send notification to Topic subscribers
        self.notify_new_thread()

    def notify_new_thread(self):
        pass


class OnAnswerCreated:
    def __init__(self, answer: ThreadAnswer):
        self.instance = answer
        self.user = answer.user
        self.parent = answer.parent

        if self.parent:
            # thread answer reply: add creator as ThreadAnswerParticipant for its parent answer.
            self.parent.add_participant(self.user)

            # update ThreadAnswerStat
            self.parent.inc_stat(ThreadAnswerStat.TYPE_REPLY_COUNT)

            # send notifications to answer participants
            self.notify_new_reply()
        else:
            # thread answer: add creator as thread participant as well as answer participants
            self.instance.add_participant(self.user)
            self.thread = self.instance.thread
            self.thread.add_participant(self.user)

            # update ThreadStat
            self.thread.inc_stat(ThreadStat.TYPE_ANSWER_COUNT)

            # send notifications to thread participants
            self.notify_new_answer()

    def notify_new_answer(self):
        """Notify all users subscribed to a thread"""
        subscribers = ThreadParticipant.subscribed_to(self.thread, exclude=self.user)
        for p in subscribers:
            # TODO: Send notification
            print(p)

    def notify_new_reply(self):
        """Notify all users subscribed to an answer"""
        subscribers = ThreadAnswerParticipant.subscribed_to(self.parent, exclude=self.user)
        for p in subscribers:
            # TODO: Send notification
            print(p)
