from typing import Dict, List, Union, Any

Field = dict[str, Union[str, list[str]]]
# Just what we get from `from fastavro import parse_schema`
FastAvroParsedSchema = Union[str, list[Any], dict[Any, Any]]
