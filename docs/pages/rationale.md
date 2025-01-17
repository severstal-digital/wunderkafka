
## Rationale

```txt
Das ist wunderbar!
```

## What we are about?

-   [Cloudera](https://www.cloudera.com/) installation with its own
    schema registry
-   [Apache Avro™](https://avro.apache.org/) is used
-   Installation requires features which are fully supported by
    [librdkafka](https://github.com/edenhill/librdkafka), but not
    bundled in confluent-kafka python wheel
-   Constant need to use producers and consumer, but without one-screen
    boilerplate
-   Frequent need to consume not purely *events*, but *fairly recent
    events*
-   Frequent need to handle a large number of events

So, that's it.

If you suffer from the same problems, you may don't need to reinvent
your own wheel, you can try ours.

## What about other projects?

Corresponding to [ASF
wiki](https://cwiki.apache.org/confluence/display/KAFKA/Clients#Clients-Python)
there are plenty of python clients.

-   [confluent-kafka](https://pypi.org/project/confluent-kafka/) is a
    de-facto standard, but doesn't work out-of-the-box for us, as
    mentioned above
-   [Kafka Python](https://github.com/dpkp/kafka-python) is awesome, but
    not as performant as confluent-kafka
-   pykafka [here](https://github.com/Parsely/pykafka) and
    [here](https://github.com/dsully/pykafka) looks unmaintained: has
    been archived
-   [pykafkap](https://github.com/urbanairship/pykafkap) has only
    producer and looks unmaintained: no updates since 2014
-   [brod](https://github.com/datadog/brod) is not maintained in favor
    of Kafka Python.

## What's next?

For now, it's a homebrew, so it lacks some of the features which may be
useful outside of our use-cases.

ToDo:

-   add configurations for multiple versions of librdkafka
-   check against confluent installation
-   add `async`/`await` syntax
-   parallelize (de)serialization on CPU
-   add distributed lock on producers
-   add on-the-fly model derivation to consumer
-   ???
