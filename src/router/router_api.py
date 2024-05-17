from typing import Annotated
from fastapi import APIRouter, Depends
from src.services.data_search import data_search
from src.schema import (Payload,
                        IsinExistsFilterSchema,
                        IsinExistsIntervalFilterSchema,
                        IidToIsinFilterSchema,
                        )

router_api = APIRouter(
    prefix="/api",
    tags=['API'],
)


@router_api.get("/isin_exists")
async def isin_exists(
        attr: Annotated[IsinExistsFilterSchema, Depends()]
) -> list[Payload]:
    s_attr = attr.model_dump()
    response = await data_search(s_attr)
    return validate_response(response)


@router_api.get("/isin_exists_interval")
async def isin_exists_interval(
        attr: Annotated[IsinExistsIntervalFilterSchema, Depends()]
) -> list[Payload]:
    s_attr = attr.model_dump()
    response = await data_search(s_attr)
    return validate_response(response)


@router_api.get("/iid_to_isin")
async def iid_to_isin(
        attr: Annotated[IidToIsinFilterSchema, Depends()]
) -> list[Payload]:
    s_attr = attr.model_dump()
    response = await data_search(s_attr)
    return validate_response(response)


def validate_response(response) -> list[Payload]:
    """
    Validates and transforms a list of objects into a list of Payload objects.
    :param response: A list of objects to be validated and transformed.
    :return: A list of Payload objects constructed from the input objects.
    """
    payload = [
        Payload(
            instrument=item.name,
            exchange=item.exchange.name,
            iid=item.iid,
            storage_type=item.storage_type,
        )
        for item in response
    ]
    return payload
