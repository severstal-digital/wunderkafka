Quickstart
==========

.. raw:: html

   <figure><blockquote style="margin: 0;"><p style="padding: 15px;background: #eee;border-radius: 5px;">Talk is cheap. Show me the code.</p></blockquote><figcaption style="text-align: right;">—Linus Torvalds</figcaption></figure>


Consumer
--------

.. literalinclude:: ../../examples/consumer.py

What you can (and can't see here):

- as you probably already guessed, we may need all that serious clumsy security stuff
- by the way, config is powered with `pydantic <https://pypi.org/project/pydantic/>`_. So you can see all configuration parameters for supported :code:`librdkafka` version just in your IDE/text editor. No more searching with :code:`Ctrl + F` through :code:`CONFIGURATION.md` and dictionaries.
- you may subscribe to multiple topics via single timestamp or timedelta (per topic definition is also supported)
- by default, you don't need to close consumer manually (though, you can still do it). :code:`atexit` is used.

More differences are on the way

AvroConsumer
------------

.. literalinclude:: ../../examples/consumer_avro.py

- keys may be ignored, which is totally optional, but may be useful.
- the main advantage here is that messages may be consumed with a batch even with avro deserialization, despite of the original API. It saves time. Really.

Multiple subscriptions example:

.. literalinclude:: ../../examples/consumer_avro_multiple_subscriptions.py

Let's move on.

AvroProducer
------------

Let's skip raw producer, as we can see all benefits in AvroProducer either.

.. literalinclude:: ../../examples/producer_avro.py

- instead of *producing* message we are thinking in terms of *sending* message. No big deal as original :code:`produce()` is still under the hood, but we automatically use :code:`poll()` for asynchronous communication and :code:`flush()` to await that message is sent. This behaviour is hidden by :code:`blocking` which is :code:`False` by default.
- by the way, :code:`atexit` is also used here: producer will try to :code:`flush()`. Nothing is guaranteed if something sudden will happen with process, but manual close is also in danger in that case.
- less boilerplate with text schemas. You may also load it simply from files (via specific "store"), but wait for a minute, you may won't want to use them.

AvroModelProducer
-----------------

What if you don't believe in everything-as-code and want more dynamics? Let's consider the next few lines:

.. literalinclude:: ../../examples/producer_avro_model.py

- just like the previous example, but the schema derived from the model itself. :code:`dataclasses` are also supported, thanks to `dataclasses-avroschema <https://pypi.org/project/dataclasses-avroschema/>`_! Unfortunately, it will work only for python 3.7 or later, but previous examples are fully-compatible with 3.6. After all, 3.6 reaches end of life in december 2021.

Conclusion
----------

This is a simple API for "daily" usage.

You still can use original rich API of confluent-kafka if needed, but from now you have some fast track.
