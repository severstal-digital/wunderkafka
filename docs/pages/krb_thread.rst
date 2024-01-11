Kerberos Thread
===============

Version librdkafka < 1.7.0
--------------------------

Introduction
^^^^^^^^^^^^


Prior to version 1.7.0, updating kinit via librdkafka could result in a lockup.
Because of this, when using a version less than 1.7.0, by default used our thread to update kerberos tickets.


Standard behavior
^^^^^^^^^^^^^^^^^

By default, 1 thread is raised to update all tickets and the timeout for all updates is 60 seconds.

To set timeout manually you need to

.. literalinclude:: ../../examples/manual_krb_timeout.py

Bottleneck
^^^^^^^^^^

Updating of kerberos tickets is done sequentially one by one.
