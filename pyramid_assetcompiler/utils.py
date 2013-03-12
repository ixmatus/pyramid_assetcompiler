# vim:fileencoding=utf-8:ai:ts=4:sts:et:sw=4:tw=80:
from pyramid_assetcompiler.compat import string_types

def as_string(value):
    result = ''
    if isinstance(value, string_types):
        result = value.strip()
    return result

def as_cr_separated_list(value):
    if isinstance(value, string_types):
        value = [_f for _f in [x.strip() for x in value.splitlines()] if _f]
    return value

def as_list(value):
    values = as_cr_separated_list(value)
    result = []
    for value in values:
        subvalues = value.split()
        result.extend(subvalues)
    return result
