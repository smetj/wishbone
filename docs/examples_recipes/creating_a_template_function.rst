Creating a template function
============================
.. _writing_a_template_function:
.. _creating_a_template_function:

Creating your own template function is easy.

In this example we will write a *fizzbuzz* template function which returns the
system's uptime in seconds.

* Your class must base :py:class:`wishbone.function.template.TemplateFunction``
* Your class must have a ``get()`` method which actually returns the desired data.
* Write a terse docstring as this will be used when issuing ``wishbone show --docs wishbone_external.function.template.uptime``.
* Install your template function along a similar entrypoint in ``setup.py``:

.. code-block:: python

  entry_points={
    'wishbone_external.function.template': [
        'uptime = wishbone_external.function.template.uptime:Uptime'
    ]
  }


**Create a class**

.. code-block:: python

    from wishbone.function.template import TemplateFunction
    from uptime import uptime


    class Uptime(TemplateFunction):
        '''
        Returns the uptime in seconds of the system.

        A Wishbone template function which returns the system's uptime in
        seconds.

        Args:
            None
        '''

        def get(self):
            '''
            The function mapped to the template function.

            Args:
                None

            Returns:
                float: Uptime in seconds.
            '''

            return uptime()

