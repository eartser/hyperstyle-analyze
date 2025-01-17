import ast
import json
from datetime import datetime
from typing import Dict, List


def str_to_dict(s: str) -> Dict:
    """ Load dict from string. """

    return json.loads(s)


def dict_to_str(d: Dict) -> str:
    """ Dump dict to string. """

    return json.dumps(d)


def list_to_str(ls: List) -> str:
    """ Dump dict to string. """

    return json.dumps(ls)


def str_to_datetime(s) -> datetime:
    """ Parse datetime from string. """

    return datetime.fromisoformat(s)


def parse_qodana_issues(s: str) -> str:
    """ Parse qodana issues from string and . """

    return list_to_str(list(map(ast.literal_eval, str_to_dict(s)['issues'])))
