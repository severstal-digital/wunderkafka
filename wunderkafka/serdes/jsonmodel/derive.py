import json

from pydantic import BaseModel
from pydantic_core import CoreSchema
from pydantic.json_schema import DEFAULT_REF_TEMPLATE, JsonSchemaMode, JsonSchemaValue, GenerateJsonSchema


class JSONClosedModelGenerator(GenerateJsonSchema):
    def __init__(
        self,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        *,
        evolvable: bool = True,
    ) -> None:
        super().__init__(by_alias, ref_template)
        self.__evolvable = evolvable

    def generate(self, schema: CoreSchema, mode: JsonSchemaMode = "validation") -> JsonSchemaValue:
        json_schema = super().generate(schema, mode=mode)
        if self.__evolvable:
            key_additional_properties = "additionalProperties"
            key_definitions = "$defs"
            json_schema[key_additional_properties] = False
            definitions = json_schema.get(key_definitions, {})
            for definition in definitions:
                if definitions[definition].get("type") == "object":
                    json_schema[key_definitions][definition][key_additional_properties] = False
        return json_schema


def derive(model_type: type[BaseModel], schema_generator: type[GenerateJsonSchema]) -> str:
    return json.dumps(model_type.model_json_schema(schema_generator=schema_generator))
