import os
import datetime
import aiofiles
from typing import Any, AsyncGenerator
from fastapi import HTTPException


async def configure_stream_response(request_data: dict[str, Any]) -> dict[str, Any]:
    """
    Prepares parameters for a StreamingResponse based on validated data.
    :param request_data: Dictionary of validated data needed for setting up the response.
    :return: Dictionary with 'content' and 'headers' keys, ready to be used in a StreamingResponse.
    """
    chunk_size = request_data.get('chunk')
    date_as_path = request_data.get('date')
    filename = request_data.get('filename')
    file_path = _create_file_path(date_as_path, filename)
    file_size = os.path.getsize(file_path)
    headers = {
        'Content-Length': str(file_size),
        'Content-Disposition': f'attachment; filename="{os.path.basename(file_path)}"',
    }
    content = _read_file_in_chunks(file_path, chunk_size)

    return {
        'content': content,
        'headers': headers,
    }


def _create_file_path(date_as_path: datetime.date, filename: str) -> str:
    """
    Asynchronously create file path and check if file exists, raise error if not.
    """
    file_path = os.path.join('data',
                             str(date_as_path.year),
                             str(date_as_path.month),
                             str(date_as_path.day),
                             filename
                             )
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return file_path


async def _read_file_in_chunks(file_path: str, chunk_size: int) -> AsyncGenerator[bytes, Any]:
    """
    Asynchronously read a file in chunks of a specified size.

    :param file_path: The path to the file to be read.
    :param chunk_size: The size of each chunk to read, in bytes.
    :return: An iterator over the chunks of the file.
    """
    try:
        async with aiofiles.open(file_path, 'rb') as file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while reading the file: {e}")
