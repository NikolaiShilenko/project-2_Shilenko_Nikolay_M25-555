

def parse_where(where_str):
    """Парсит условие WHERE в словарь."""
    if not where_str:
        return None

    where_str = where_str.strip()

    if "=" in where_str:
        parts = where_str.split("=", 1)
        col = parts[0].strip()
        val = parts[1].strip()

        # преобразование будет в _convert_value
        return {col: val}

    return None


def parse_set(set_str):
    """Парсит условие SET в словарь."""
    if not set_str:
        return None

    set_str = set_str.strip()
    result = {}

    if "," in set_str:
        parts = set_str.split(",")
        for part in parts:
            if "=" in part:
                col, val = part.split("=", 1)
                result[col.strip()] = val.strip()
    elif "=" in set_str:
        col, val = set_str.split("=", 1)
        result[col.strip()] = val.strip()

    return result
