from src.sources.base import APIConfig, APIEndpointConfig


def _get_nested_value(data: dict, path: str) -> any:
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            raise KeyError(f"Path '{path}' not found in data. Failed at key '{key}'")
    return current


def extract_items(
    data: dict, endpoint_config: APIEndpointConfig, source: APIConfig
) -> list[dict]:
    json_entrypoint = (
        endpoint_config.json_entrypoint
        if endpoint_config.json_entrypoint is not None
        else source.json_entrypoint
    )
    if json_entrypoint is not None:
        result = _get_nested_value(data, json_entrypoint)
        return result if isinstance(result, list) else [result]
    return data if isinstance(data, list) else [data]
