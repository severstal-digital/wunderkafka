from typing import Dict, List, Union

Field = Dict[str, Union[str, List[str]]]
# Just what we get from `from fastavro import parse_schema`
FastAvroParsedSchema = Union[str, List[Any], Dict[Any, Any]]
