import os
import logging
import operator
from typing import Dict, List, Tuple, Union, Optional, NamedTuple
from pathlib import Path
from collections import defaultdict

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
)
logger = logging

# mypy cannot into constrained type at the time of on-knee writing of this script
IGNORE_PYDANTIC_TYPE = '# type: ignore[valid-type]'

GROUP_ID = 'group.id'

CLS_MAPPING = {
    'P': 'class RDProducerConfig(RDKafkaConfig):',
    'C': 'class RDConsumerConfig(RDKafkaConfig):',
    '*': 'class RDKafkaConfig(BaseSettings):',
}

TPL_MAPPING = {
    'P': 'PRODUCER_FIELDS = (',
    'C': 'CONSUMER_FIELDS = (',
    '*': 'COMMON_FIELDS = (',
}

TYPES_MAPPING = {
    'integer': 'int',
    'float': 'float',
    'string': 'str',
    'boolean': 'bool',
    'see dedicated API': 'Callable',
    'CSV flags': 'str',
    'pattern list': 'str',
}


class Row(NamedTuple):
    property_name: str
    property_belongs: str
    property_range: str
    property_default: str

    property_importance: str
    property_description: str

    @property
    def comment(self) -> bool:
        return '..' in self.property_range

    @property
    def deprecated(self) -> bool:
        # Markdown
        deprecated = '**deprecated'
        return self.property_description.casefold().startswith(deprecated)

    @property
    def name(self) -> str:
        return self.property_name.replace('.', '_')

    @property
    def cls(self) -> str:
        return CLS_MAPPING[self.property_belongs]

    @property
    def default(self) -> Optional[Union[str, bool, float]]:
        if not self.property_default:
            return None
        if self.type == 'boolean':
            return self.property_default.casefold() == 'true'
        if self.type == 'float':
            return float(self.property_default)
        if self.type in {'string', 'CSV flags'}:
            return "'{0}'".format(self.property_default)
        if self.type == 'enum value':
            class_name = ''.join([word.capitalize() for word in self.property_name.split('.')])
            return 'enums.{0}.{1}'.format(class_name, self.property_default)
        return self.property_default

    @property
    def range(self) -> Union[str, Tuple[str, str]]:
        delim = '..'
        if delim not in self.property_range:
            # search for bool
            pieces = [piece.strip().casefold() for piece in self.property_range.split(',') if piece.strip()]
            if set(pieces) == {'true', 'false'}:
                return 'bool'
            logger.warning("Couldn't treat range as bool either: {0}".format(self.property_range))
            return self.property_range
        pieces = [piece.strip() for piece in self.property_range.split(delim) if piece.strip()]
        if len(pieces) != 2:
            logger.warning("Couldn't convert range: {0}".format(self.property_range))
            return self.property_range
        ge, le = pieces
        return ge, le

    @property
    def annotation(self) -> str:
        if self.type == 'boolean':
            return TYPES_MAPPING[self.type]
        if not self.default:
            return 'Optional[{0}]'.format(TYPES_MAPPING[self.type])
        if self.type == 'string':
            return TYPES_MAPPING[self.type]
        if self.type == 'CSV flags':
            return TYPES_MAPPING[self.type]
        if '..' in self.property_range:
            ge, le = self.range                                                                           # type: ignore
            if self.type == 'integer':
                return 'conint(ge={0}, le={1})'.format(ge, le)
            elif self.type == 'float':
                return 'confloat(ge={0}, le={1})'.format(ge, le)
        if self.type == 'enum value':
            class_name = ''.join([word.capitalize() for word in self.property_name.split('.')])
            return 'enums.{0}'.format(class_name)
        err_msg = "You missed something, you, stupid! Check: {0} {1} {2}"
        raise ValueError(err_msg.format(self.name, self.property_range, self.default))

    @property
    def type(self) -> str:
        # logger.debug(self.property_description.split('Type: '))
        return self.property_description.split('Type: ')[-1].strip('*')

    def __str__(self) -> str:
        if self.property_name == GROUP_ID:
            return '    {0}: str'.format(self.name)
        if self.property_name == 'builtin.features':
            lines = ["', '.join(["]
            spaces = ' ' * 8
            for feat in self.default.strip('"').strip("'").split(','):                                    # type: ignore
                stripped = feat.strip()
                if stripped:
                    lines.append("{0}'{1}',".format(spaces, stripped))
            lines.append("    ])")
            return '    {0}: {1} = {2}'.format(self.name, self.annotation, '\n'.join(lines))
        if self.comment:
            left = '    {0}: {1} = {2}'.format(self.name, self.annotation, self.default)
            ws = 120 - len(left) - len(IGNORE_PYDANTIC_TYPE)
            if ws < 1:
                ws = 1
            return left + ws * ' ' + IGNORE_PYDANTIC_TYPE
        else:
            return '    {0}: {1} = {2}'.format(self.name, self.annotation, self.default)


def read_markdown(filename: Union[str, Path] = 'CONFIGURATION.md', *, cut: bool = False) -> List[str]:
    lines = []
    with open(filename, 'r') as fl:
        all_lines = [ln.strip() for ln in fl.read().split('\n') if ln.strip()]
        if not cut:
            return all_lines
    for line in all_lines:
        if line.startswith('## Topic configuration properties'):
            break
        lines.append(line)
    return lines


def write_python(lines: List[str], file_name: str) -> None:
    with open(file_name, 'w') as fl:
        for line in lines:
            fl.write('{0}\n'.format(line))


def parse_line(line: str) -> Optional[Row]:
    not_a_rows = ('#', '-', 'Property')
    for bad_start in not_a_rows:
        if line.startswith(bad_start):
            return None
    column_data = [piece.strip().replace('\|', '|') for piece in line.split(' | ')]
    if len(column_data) != 6:
        logger.warning("Couldn't parse: {0}".format(column_data))
        return None
    return Row(*column_data)


def parse(lines: List[str], *, allow_deprecated: bool = False) -> List[Row]:
    rows = []
    for line in lines:
        row = parse_line(line)
        if row is not None:
            if row.deprecated:
                if allow_deprecated is False:
                    logger.warning('Skipping {0} as deprecated'.format(row.property_name))
                else:
                    logger.warning('{0} is deprecated'.format(row.property_name))
                    rows.append(row)
            else:
                rows.append(row)
    logger.info('Total properties parsed: {0}'.format(len(rows)))
    return rows


def group(rows: List[Row]) -> Dict[str, List[Row]]:
    grps = defaultdict(list)
    for row in rows:
        grps[row.property_belongs].append(row)
    return grps


def generate_models(groups: Dict[str, List[Row]]) -> List[str]:
    properties = [
        '# I am not gonna to generate single type for every single range of conint/confloat.',
        '# https://github.com/samuelcolvin/pydantic/issues/156',
        '',
        'from typing import Callable, Optional',
        '',
        'from pydantic import conint, confloat',
        'from pydantic_settings import BaseSettings',
        '',
        "# Enums because we can't rely that client code uses linters.",
        '# Of course, it will fail with cimpl.KafkaException, but later, when Consumer/Producer are really initiated',
        'from wunderkafka.config.generated import enums'
    ]
    already_generated = set()
    for grp in sorted(groups):
        properties.append('')
        properties.append('')
        properties.append('{0}'.format(CLS_MAPPING[grp]))
        pre = []
        uniq = []
        for row in groups[grp]:
            if row.property_name in already_generated:
                logger.warning('Skipping generating second field ({0})'.format(row))
            else:
                if row.property_name == GROUP_ID:
                    pre.append(row)
                else:
                    uniq.append(row)
                already_generated.add(row.property_name)
        properties += [str(row) for row in sorted(pre, key=operator.attrgetter('name'))]
        properties += [str(row) for row in sorted(uniq, key=operator.attrgetter('name'))]

    return properties


def generate_fields(groups: Dict[str, List[Row]]) -> List[str]:
    properties = [
        "# Why so: not all configuration parameters of librdkafka may be easily replaced from '_' to '.',",
        "#   therefore, we can't convert on-the-fly from  `ssl_ca` without errors",
        "#   and we don't want to have a nice whitelist, which is arguable",
    ]
    for grp in sorted(groups):
        properties.append('{0}'.format(TPL_MAPPING[grp]))
        all_fields = sorted({row.property_name for row in groups[grp]})
        properties += ["    '{0}',".format(field) for field in all_fields]
        properties.append(')')
    return properties


def generate_enums(groups: Dict[str, List[Row]]) -> List[str]:
    properties = ['from enum import Enum']
    already_generated = set()
    for grp in sorted(groups):
        for row in groups[grp]:
            if row.type == 'enum value':
                if row.property_name in already_generated:
                    logger.warning('Skipping second enum for {0}'.format(row.property_name))
                else:
                    properties.append('')
                    properties.append('')
                    properties += generate_enum(row.property_name, row.property_range)
                    already_generated.add(row.property_name)
    return properties


def generate_enum(prop: str, rng: str) -> List[str]:
    cls_name = ''.join([word.capitalize() for word in prop.split('.')])
    header = 'class {0}(str, Enum):'.format(cls_name)
    flds = []
    for field in rng.split(','):
        flds.append("    {0} = '{0}'".format(field.strip()))
    return [header] + flds


Name = str
Version = str
Lines = List[str]
Files = Dict[Name, Lines]


def generate(lines: Dict[Version, Files]) -> Dict[Name, Lines]:
    dct: Dict[Name, Lines] = {}
    for file_name in ('enums.py', 'models.py', 'fields.py'):
        logger.info('Processing {0}'.format(file_name))
        s = set()
        for libversion in lines:
            content = '\n'.join(lines[libversion][file_name])
            s.add(content)
        if not len(s):
            raise ValueError('Nothing to compare')
        if len(s) == 1:
            logger.info('All generated files for {0} are equal, keeping just one'.format(file_name))
            dct[file_name] = lines[libversion][file_name]
        else:
            logger.warning("Generated files for {0} differs, merging it...".format(file_name))
            header = '# mypy: disable-error-code="no-redef"'
            if file_name == 'fields.py':
                header = '# mypy: disable-error-code="no-redef,assignment"'
            new_lines = [
                '# ToDo (tribunsky.kir): looks like that idea of dynamic import via imp depending on librdkafka',
                "#                       wasn't the worst idea, cause `if`s causes a lot of static checks problems.",
                header,
                '',
                'from wunderkafka import librdkafka',
                '',
            ]
            head, *tail = list(sorted(lines))
            new_lines.extend(lines[head][file_name])
            for libversion in tail:
                tpl = tuple(int(digit) for digit in libversion.split('.'))
                delimeter = [
                    '',
                    'if librdkafka.__version__ >= {0}:'.format(tpl)
                ]
                new_lines.extend(delimeter)
                new_lines.extend('    {0}'.format(line) for line in lines[libversion][file_name])
            new_lines.append('')
            dct[file_name] = new_lines
    return dct


def main() -> None:
    lines: Dict[Version, Files] = {}
    root_dir = Path(__file__).parent / 'versions'
    for sub_path in os.listdir(root_dir):
        path = root_dir / sub_path
        if path.is_dir():
            logger.info('{0}: handling...'.format(path))
            configuration_md = path / 'CONFIGURATION.md'
            grouped = group(parse(read_markdown(filename=configuration_md)))
            files = {
                'models.py': generate_models(grouped),
                'fields.py': generate_fields(grouped),
                'enums.py': generate_enums(grouped),
            }
            lines[sub_path] = files
        else:
            logger.info('{0}: skipping...'.format(path))
    dct = generate(lines)
    for file_name, content in dct.items():
        write_python(content, 'generated/{0}'.format(file_name))


def single() -> None:
    grouped = group(parse(read_markdown()))
    models = generate_models(grouped)
    write_python(models, 'models.py')
    fields = generate_fields(grouped)
    write_python(fields, 'fields.py')
    enums = generate_enums(grouped)
    write_python(enums, 'enums.py')


if __name__ == '__main__':
    main()
