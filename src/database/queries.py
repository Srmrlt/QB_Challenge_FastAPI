from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload, load_only
from src.database.database import engine, session_factory, Base
from src.database.models import ExchangeOrm, InstrumentOrm


class OrmMethods:
    @staticmethod
    async def create_tables():
        """
        Asynchronously create all tables in the database using metadata.
        This should be called to initialize the database schema.
        """
        async with engine.connect() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()

    @staticmethod
    async def delete_tables():
        """
        Asynchronously drop all tables in the database.
        This will remove all data and the schema from the database.
        """
        async with engine.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.commit()

    @staticmethod
    async def add_new_data(model, attributes):
        """
        Asynchronously add new data to the database if it does not already exist.
        :param model: The ORM model class to which the data should be added.
        :param attributes: A dictionary of attributes to be set on the new model instance.
        :return: The ID of the new or existing data.
        """
        async with session_factory() as session:
            async with session.begin():
                data = await session.execute(select(model).filter_by(**attributes))
                data = data.scalars().first()
                if data is None:
                    new_data = model(**attributes)
                    session.add(new_data)
                    await session.flush()  # Fix changes to get an id of a new data
                    return new_data.id

    @staticmethod
    async def find_data(search_conditions: list):
        """
        Asynchronously find data in the database based on specified search conditions.
        :param search_conditions: A list of conditions to filter the data.
        :return: A list of found data items.
        """
        async with session_factory() as session:
            instrument_load_list = [InstrumentOrm.name, InstrumentOrm.iid, InstrumentOrm.storage_type]
            query = (select(InstrumentOrm)
                     .join(InstrumentOrm.exchange)
                     .join(ExchangeOrm.date)
                     .options(joinedload(InstrumentOrm.exchange)
                              .load_only(ExchangeOrm.name)
                              )
                     .options(load_only(*instrument_load_list))
                     .filter(and_(*search_conditions))
                     )

            result = await session.execute(query)
            return result.scalars().all()
