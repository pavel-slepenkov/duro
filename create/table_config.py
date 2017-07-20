from typing import Dict

from utils.utils import DistSortKeys


def load_dist_sort_keys(config: Dict) -> DistSortKeys:
    distkey = f'distkey("{config["distkey"]}")' if config.get('distkey') else ''
    diststyle = f'diststyle {config["diststyle"]}' if config.get(
        'diststyle') else ''
    sortkey = f'sortkey("{config["sortkey"]}")' if config.get('sortkey') else ''

    # noinspection PyArgumentList
    return DistSortKeys(distkey, diststyle, sortkey)


def add_dist_sort_keys(table: str, query: str, config: Dict) -> str:
    keys = load_dist_sort_keys(config)
    return f'''CREATE TABLE {table}_temp
            {keys.distkey} {keys.sortkey} {keys.diststyle}
            AS ({query});'''


def load_grant_select_statements(table: str, config: Dict) -> str:
    return f'''GRANT SELECT ON {table}_temp TO {config['grant_select']}'''