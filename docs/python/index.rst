======
Python
======

The most prominent Python parts invovled in writing a Wishbone server are:

:py:class:`wishbone.event.Event`
    Encapsulates the data traveling between the modules.

:py:class:`wishbone.actor.Actor`
    A baseclass for all module types.

:py:class:`wishbone.actorconfig.ActorConfig`
    Determines the characteristics of the actor based module.

:py:class:`wishbone.router.default.Default`
    Holds all module instances and organises the stream of events between them

:py:class:`wishbone.componentmanager.ComponentManager`
    A convenience function to easily load components by entry point.


Consider the following "hello world" example:


.. code-block:: python

    from wishbone.actorconfig import ActorConfig
    from wishbone.router.default import Default
    from wishbone.componentmanager import ComponentManager


    def main():

        router = Default()

        f = ComponentManager().getComponentByName("wishbone.function.module.append")

        f_instance = f(
            data="you_are_tagged",
            destination="tags"
        )

        router.registerModule(
            module="wishbone.module.input.generator",
            actor_config=ActorConfig(
                name='input'
            ),
            arguments={
                "payload"
            }
        )

        router.registerModule(
            module="wishbone.module.output.stdout",
            actor_config=ActorConfig(
                name='output',
                module_functions={
                    "inbox": [
                        f_instance
                    ]
                }
            ),
            arguments={
                "selection": None
            }
        )

        router.connectQueue('input.outbox', 'output.inbox')
        router.start()
        router.block()


    if __name__ == '__main__':
        main()

