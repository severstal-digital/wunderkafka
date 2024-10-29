Raw Bytes
=========

BytesConsumer
-------------

.. autoclass:: wunderkafka.BytesConsumer
   :members:

BytesProducer
-------------

.. autoclass:: wunderkafka.BytesProducer
   :members:


Schemaless
==========

SchemaLessJSONStringConsumer
----------------------------

.. autoclass:: wunderkafka.factories.schemaless.SchemaLessJSONStringConsumer
   :members:

SchemaLessJSONStringProducer
----------------------------

.. autoclass:: wunderkafka.factories.schemaless.SchemaLessJSONStringProducer
   :members:


SchemaLessJSONModelStringProducer
---------------------------------

.. autoclass:: wunderkafka.factories.schemaless.SchemaLessJSONModelStringProducer
   :members:

Avro
====

AvroConsumer
------------

.. autoclass:: wunderkafka.AvroConsumer
   :members:
   :inherited-members:

AvroProducer
------------

.. autoclass:: wunderkafka.AvroProducer
   :members:
   :inherited-members:

AvroModelProducer
-----------------

.. autoclass:: wunderkafka.AvroModelProducer
   :members:
   :inherited-members:

JSON
====

JSONConsumer
------------

.. autoclass:: wunderkafka.factories.json.JSONConsumer
   :members:
   :inherited-members:

JSONProducer
------------

.. autoclass:: wunderkafka.factories.json.JSONProducer
   :members:
   :inherited-members:

JSONModelProducer
-----------------

.. autoclass:: wunderkafka.factories.json.JSONModelProducer
   :members:
   :inherited-members:

Mixed
=====

These pre-configured consumers and producers are provided for convenience and as explicit example of how to define own factories with mixed (de)serializers.

.. note::
   The naming follow producer API, where the key follows the value. That's why the classes are called `{Value(de)Serializer`+`{Key(de)Serializer`}.

AVRO + String
-------------

AvroModelStringProducer
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: wunderkafka.factories.mixed.AvroModelStringProducer
   :members:
   :inherited-members:

AvroStringConsumer
^^^^^^^^^^^^^^^^^^

.. autoclass:: wunderkafka.factories.mixed.AvroStringConsumer
   :members:
   :inherited-members:

JSON + String
-------------

JSONModelStringProducer
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: wunderkafka.factories.mixed.JSONModelStringProducer
   :members:
   :inherited-members:

JSONStringConsumer
^^^^^^^^^^^^^^^^^^

.. autoclass:: wunderkafka.factories.mixed.JSONStringConsumer
   :members:
   :inherited-members:

TopicSubscription
=================

.. autoclass:: wunderkafka.TopicSubscription
   :members:
   :inherited-members:
   :noindex:
