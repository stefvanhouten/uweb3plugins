import uweb3plugins.core.paginators.columns as columns


def _single_get(item, key):
    try:
        val = item[key]
    except (KeyError, TypeError):
        val = getattr(item, key)

    try:
        return val()
    except TypeError:
        return val


def _recursive_getattr(item, keys):
    try:
        keys = keys.split(".")
    except AttributeError:
        pass

    if item is None:
        return None
    if len(keys) == 1:
        return _single_get(item, keys[0])
    else:
        return _recursive_getattr(_single_get(item, keys[0]), keys[1:])


def get_attr(item, attr):
    if isinstance(attr, columns.ConstantAttr):
        return attr.value

    if "." in attr:
        return _recursive_getattr(item, attr)
    else:
        return _single_get(item, attr)
