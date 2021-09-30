from typing import Dict, List, Union

Field = Dict[str, Union[str, List[str]]]
FastAvroParsedSchema = Dict[str, Union[bool, str, List[Field]]]
