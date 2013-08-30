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

    def __init__(self, name, capitalize=False):
        Actor.__init__(self, name, setupbasic=True)
        self.capitalize=capitalize
        self.logging.info("Initialized")

    def consume(self, event):

        data = event["data"]

        data = [::-1]

        if self.capitalize == True:
            data = data.title()
        event["data"]=data

        self.queuepool.outbox.put(event)