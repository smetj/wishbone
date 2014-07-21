from wishbone import Actor


class ReverseData(Actor):
    '''**Sample module which reverses incoming events.**

    Parameters:

        - name (str):       The instance name.

        - capitalize(bool): When True capitalizes the
                            first letter.
                            Default: True

    Queues:

        - inbox:    Incoming events.

        - outbox:   Outgoing events.
    '''

    def __init__(self, name, size=100, frequency=1, capitalize=False):
        Actor.__init__(self, name, size, frequency)
        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

        self.capitalize = capitalize

    def preHook(self):
        self.logging.info("Hello from preHook")

    def postHook(self):
        self.logging.info("Goodbye from postHook")

    def consume(self, event):

        data = event["data"]

        data = [::-1]

        if self.capitalize:
            data = data.title()
        event["data"] = data

        self.queuepool.outbox.put(event)
