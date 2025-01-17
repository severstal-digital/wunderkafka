## Raw Bytes

### BytesConsumer

::: wunderkafka.BytesConsumer

### BytesProducer

::: wunderkafka.BytesProducer

## Schemaless

### SchemaLessJSONStringConsumer

::: wunderkafka.factories.schemaless.SchemaLessJSONStringConsumer

### SchemaLessJSONStringProducer

::: wunderkafka.factories.schemaless.SchemaLessJSONStringProducer

### SchemaLessJSONModelStringProducer

::: wunderkafka.factories.schemaless.SchemaLessJSONModelStringProducer

## Avro

### AvroConsumer

::: wunderkafka.AvroConsumer

### AvroProducer

::: wunderkafka.AvroProducer

### AvroModelProducer

::: wunderkafka.AvroModelProducer

## JSON

### JSONConsumer

::: wunderkafka.factories.json.JSONConsumer

### JSONProducer

::: wunderkafka.factories.json.JSONProducer

### JSONModelProducer

::: wunderkafka.factories.json.JSONModelProducer

## Mixed

These pre-configured consumers and producers are provided for
convenience and as explicit example of how to define own factories with
mixed (de)serializers.

!!! Note
    The naming follow producer API, where the key follows the value. That\'s
    why the classes are called:
    Value(de)Serializer + Key(de)Serializer.

### AVRO + String

#### AvroModelStringProducer

::: wunderkafka.factories.mixed.AvroModelStringProducer

#### AvroStringConsumer

::: wunderkafka.factories.mixed.AvroStringConsumer

### JSON + String

#### JSONModelStringProducer

::: wunderkafka.factories.mixed.JSONModelStringProducer

#### JSONStringConsumer

::: wunderkafka.factories.mixed.JSONStringConsumer

## TopicSubscription

::: wunderkafka.TopicSubscription

