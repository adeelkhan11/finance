from finance.csvfile import CSVFile


def test_check_order():
    assert(CSVFile.check_order(['a', 'b', 'c']) == 'ascending')
    assert(CSVFile.check_order(['a', 'B', 'c']) == 'unknown')
    assert(CSVFile.check_order([5, 7, 11]) == 'ascending')
    assert(CSVFile.check_order(['a', 'd', 'c']) == 'unknown')
    assert(CSVFile.check_order([8, 11, 7]) == 'unknown')
    assert(CSVFile.check_order(['c', 'B', 'a']) == 'unknown')
    assert(CSVFile.check_order(['c', 'b', 'a']) == 'descending')
    assert(CSVFile.check_order([10, 7, 3]) == 'descending')


def test_get_value_type():
    assert(CSVFile.get_value_type('1.0') == ('1.0', 'decimal'))
    assert(CSVFile.get_value_type('1') == ('1', 'integer'))
    assert(CSVFile.get_value_type('a') == ('a', 'text'))
    assert(CSVFile.get_value_type('1.0a') == ('1.0a', 'text'))
    assert(CSVFile.get_value_type('2017-01-23') == ('2017-01-23', 'date'))
    assert(CSVFile.get_value_type('23/01/2017') == ('2017-01-23', 'date'))


def test_get_pivot():
    assert(CSVFile._get_pivot([['a', 'b'], ['c', 'd']]) == [['a', 'c'], ['b', 'd']])


def test_get_column_types():
    type_table = [
        ['integer', 'decimal', 'decimal', 'text', 'date', 'date', 'null'],
        ['integer', 'decimal', 'null',    'text', 'date', 'date', 'null'],
        ['integer', 'decimal', 'decimal', 'text', 'date', 'text', 'null']
    ]

    result = CSVFile.get_column_types(type_table)

    assert(result == ['integer', 'decimal', 'nullable decimal', 'text', 'date', 'text', 'null'])
