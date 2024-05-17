import os
from typing import Any
from lxml import etree
from inflection import underscore as camel_to_snake
from sqlalchemy.exc import SQLAlchemyError
from src.database.queries import OrmMethods
from src.database.models import *


async def parse_data():
    try:
        # Parsing the xml files in data directory
        await _parse_directory('data')
    except Exception as e:
        raise Exception(f'Error parsing data: {e}')


async def _parse_directory(root_dir: str):
    """
    Walk through the directories and parse 'manifest.xml' in each subdirectory.
    :param root_dir: The root directory from which to start the walk.
    """
    for subdir, dirs, files in os.walk(root_dir):
        if 'manifest.xml' in files:
            path = os.path.join(subdir, 'manifest.xml')
            try:
                # Parse the manifest file to extract and save data to the database
                await _parse_manifest(path)
            except etree.XMLSyntaxError as e:
                print(f'XML syntax error in {path}: {e}')
            except Exception as e:
                print(f'Error parsing {path}: {e}')


async def _parse_manifest(xml_path: str):
    """
    Parse the XML manifest file,
    create or update database records for the date, exchanges, and instruments.
    :param xml_path: The file path of the manifest XML.
    """
    root = _parse_xml_file(xml_path)

    # Read Date from file
    date_pk = await _process_manifest_date(root)

    #  Read Exchange params from file
    for exchange in root.xpath('.//Exchange'):
        exchange_pk = await _process_exchange(exchange, date_pk)

        #  Read Instrument params from file
        for instrument in exchange.xpath('.//Instrument'):
            await _process_instrument(instrument, exchange_pk)


def _parse_xml_file(path: str):
    """
    Parses an XML file and returns its root element.
    :param path: The file system path to the XML file.
    :return: An Element object which is the root of the XML tree.
    """
    tree = etree.parse(path)
    return tree.getroot()


def _sqlalchemy_exception_handler(func):
    """
    Decorator to handle SQLAlchemy exceptions for asynchronous functions.
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            raise Exception(f'Database error in {func.__name__}: {e}')
    return wrapper


@_sqlalchemy_exception_handler
async def _process_manifest_date(root):
    """
    Asynchronously processes and stores date data in the database.
    :param root: An Element object which is the root of the XML tree.
    """
    date = root.find('Date').text
    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    return await OrmMethods.add_new_data(DateOrm, {'date': date})


@_sqlalchemy_exception_handler
async def _process_exchange(exchange, date_pk):
    """
    Asynchronously processes and stores exchange data in the database with associated date primary key.
    :param exchange: The object representing the exchange.
    :param date_pk: The primary key (integer) of the date to which this exchange belongs.
    """
    attributes = _get_attributes(exchange, ['Name', 'Location'])
    attributes['date_id'] = date_pk
    return await OrmMethods.add_new_data(ExchangeOrm, attributes)


@_sqlalchemy_exception_handler
async def _process_instrument(instrument, exchange_pk):
    """
    Asynchronously processes and stores instrument data in the database with associated exchange primary key.
    :param instrument: The object representing the instrument.
    :param exchange_pk: The primary key (integer) of the exchange to which this instrument belongs.
    """
    attributes: dict[str, Any] = _get_attributes(
        instrument,
        ['Name', 'StorageType', 'Levels', 'Iid', 'AvailableIntervalBegin', 'AvailableIntervalEnd']
    )
    attributes['iid'] = int(attributes['iid'])
    attributes['available_interval_begin'] = (
        datetime.datetime.strptime(attributes['available_interval_begin'], '%H:%M').time())
    attributes['available_interval_end'] = (
        datetime.datetime.strptime(attributes['available_interval_end'], '%H:%M').time())
    attributes['exchange_id'] = exchange_pk
    await OrmMethods.add_new_data(InstrumentOrm, attributes)


def _get_attributes(element, attrs: list[str]) -> dict[str, str]:
    """
    Extracts specified attributes from an element and returns them as a dictionary with snake_case keys.
    :param element: The object or element from which attributes are to be extracted.
    :param attrs: A list of attribute names (strings) that are to be extracted from the element.
    :return: A dictionary where keys are the snake_case versions of the attribute names provided in 'attrs'.
    """
    return {camel_to_snake(attr): element.get(attr) for attr in attrs}
