from typing import Dict, List, Union, Any

Field = Dict[str, Union[str, List[str]]]
# Just what we get from `from fastavro import parse_schema`
FastAvroParsedSchema = Union[str, list[Any], Dict[Any, Any]]
