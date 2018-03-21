from create.data_tests import parse_tests_results, load_tests


def test_parse_tests_results():
    results = [('First test', True), ('Second test', True)]
    assert parse_tests_results(results) == (True, None)
    results = [('First test', False), ('Second test', True)]
    assert parse_tests_results(results) == (False, ['First test'])


def test_load_tests(views_path, logger):
    cities_test = '''select (city = 'Paris') as correct_capital_of_france
from first.cities_temp
where country = 'France';

select (city = 'Ottawa')  as correct_capital_of_canada
from first.cities_temp
where country = 'Canada';'''

    assert cities_test == load_tests('first.cities', views_path, logger)

    countries_test = '''select (continent = 'Europe') as correct_continent_for_france
from first.countries_temp
where country = 'France';'''

    assert countries_test == load_tests('first.countries', views_path, logger)