# Wunderkafka

## Unreleased

### Added

- This changelog file with some info about old versions
- Consumer now may return `StreamResult` instead of the decoded message. This allows returning additional information about message processing and handle errors w/o raising exceptions

### Changed

- Updated minimal required version of `dataclasses-avroschema` to `0.53.0`. Prior versions doesn't pass library's test suites against `pydantic V2` and require effort to implement

### Fixed

- Nested `BaseModel`-inherited structures are not supported for schema derivation
- `sphinx` docs were broken for some time (since `v0.12.0`, update to `pydantic V2`)
- Config generator of `librdkafka` options now generates code which is more compliant with PEP-8
- Annotations for describing avro Schemas are updated as in `fastavro`

## v0.14.2 (2023-11-17)

### Fixed

- Check if `cmd_init` is set for the HTTP client

## v0.14.1 (2023-10-24)

### Added 

- HTTP client may be initialized with `cmd_kinit` argument. When provided, the client starts its own thread to handle kerberos ticket (awaits `kinit` to be present in runtime environment) 

## v0.14.0 (2023-10-10)

### Fixed

- Set default timeout for subprocess calls of `klist` and `kinit`.

## v0.13.1 (2023-09-29)

### Fixed

- Unexpected suffixes from `confluent_kafka.libversion()` are now removed

## v0.13.0 (2023-09-28)

### Added

- Possibility to use multiple keytabs like librdkafka does

### Fixed

- Multiple bugs related to kerberos-related functionality 

## v0.12.0 (2023-08-29)

### Added

- Configurations of librdkafka up to 2.2.0

### Changed

- From now support only `pydantic V2`
- Kerberos-related functionality is now optional for a package

### Fixed

- Now some builtin-features are checked in runtime and don't raise errors due to absent system dependencies
- `urlparse` paths in tests for schema registry stub in a file system
