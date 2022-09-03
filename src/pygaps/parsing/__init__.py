# pylint: disable=W0614,W0611,W0622
# flake8: noqa
# isort:skip_file
from pygaps.utilities.exceptions import ParsingError

_PARSER_PRECISION = 8

from .csv import isotherm_from_csv
from .csv import isotherm_to_csv
from .aif import isotherm_from_aif
from .aif import isotherm_to_aif
from .excel import isotherm_from_xl
from .excel import isotherm_to_xl
from .isodb import isotherm_from_isodb
from .json import isotherm_from_json
from .json import isotherm_to_json
from .sqlite import isotherms_from_db
from .sqlite import isotherm_delete_db
from .sqlite import isotherm_to_db
from .sqlite import adsorbates_from_db
from .sqlite import adsorbate_delete_db
from .sqlite import adsorbate_to_db
from .sqlite import materials_from_db
from .sqlite import material_delete_db
from .sqlite import material_to_db

_COMMERCIAL_FORMATS = {
    'smsdvs': ('xlsx', ),
    'bel': ('csv', 'xl', 'dat'),
    'mic': ('xl', ),
    '3p': ('xl', ),
    'qnt': ('txt-raw', ),
}


def isotherm_from_commercial(path, manufacturer, fmt, **options):
    """
    Parse aa file generated by commercial apparatus.

    Parameters
    ----------
    path: str
        the location of the file.
    manufacturer : {'mic', 'bel', '3p'}
        Manufacturer of the apparatus.
    fmt : {'xl', 'txt', ...}
        The format of the import for the isotherm.

    Returns
    -------
    PointIsotherm
    """
    import pandas
    from pygaps.core.pointisotherm import PointIsotherm
    from adsorption_file_parser import read

    meta, data = read(path, manufacturer, fmt, **options)
    data = pandas.DataFrame(data)

    meta['loading_key'] = 'loading'
    meta['pressure_key'] = 'pressure'

    # TODO pyGAPS does not yet handle saturation pressure recorded at each point
    # Therefore, we use the relative pressure column as our true pressure,
    # ignoring the absolute pressure column
    if 'pressure_relative' in data.columns:
        data['pressure'] = data['pressure_relative']
        data = data.drop('pressure_relative', axis=1)
        meta['pressure_mode'] = 'relative'
        meta['pressure_unit'] = None
    elif 'pressure_saturation' in data.columns:
        data['pressure'] = data['pressure'] / data['pressure_saturation']
        meta['pressure_mode'] = 'relative'
        meta['pressure_unit'] = None

    return PointIsotherm(isotherm_data=data, **meta)
