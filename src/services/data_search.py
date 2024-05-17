from typing import Any
from src.database.queries import OrmMethods
from src.database.models import DateOrm, ExchangeOrm, InstrumentOrm


async def data_search(search_params: dict[str, Any]):
    """
    Asynchronous function to search for data based on various filters.
    :param search_params: A dictionary with column names as keys (e.g., 'date', 'instrument')
     and filter values as values. Missing or None values are ignored in the search.
    :return: returns database results meeting 'validated_data' criteria via OrmMethods.find_data.
    """
    criteria = {
        DateOrm.date: search_params.get('date'),
        InstrumentOrm.name: search_params.get('instrument'),
        ExchangeOrm.name: search_params.get('exchange'),
        InstrumentOrm.iid: search_params.get('iid'),
    }
    conditions = [field == value for field, value in criteria.items() if value is not None]

    if search_params.get('date_from'):
        conditions.append(DateOrm.date >= search_params.get('date_from'))
    if search_params.get('date_to'):
        conditions.append(DateOrm.date <= search_params.get('date_to'))

    return await OrmMethods.find_data(conditions)
