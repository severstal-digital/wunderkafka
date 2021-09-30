Advanced Examples
=================

As you've just seen in :doc:`quickstart`, we couldn't eliminate all the boilerplate which is needed to start consumer/producer with ease.

So let's see, what we can do here.

Redefining configs
------------------

So yes, you may still consider that you need something like this in your code base:

.. literalinclude:: ../../examples/factory_config.py

And all this effort is needed to end up with something like:

.. literalinclude:: ../../examples/factory.py

Isn't that simple?

Yet Another Framework?
----------------------

Wunderkafka is written with pluggability in mind (and of course assumptions about what may be needed will be broken), so in its core is a little too general. It is intended to provide relatively simple way to rebuild your own pipeline with minimum effort.

.. literalinclude:: ../../examples/factory_consumer.py

Looks java'sh? I know, forgive me that.

If you like to use inheritance, there is nice examples in :code:`wunderkafka.factories` to start with. Or check :doc:`advanced_API` (currently to-be-done).

As you can see it is pretty straightforward and you can write your own containers for schema handling or (de)serialization, still running above performant :code:`librdkafka`.

It's also simple enough to redefine every part of the (de)serializing pipeline with specific implementation. For example, if there is need to keep message's schema in message itself, it is possible to define stub instead of schema registry and write own header (un)packer.
