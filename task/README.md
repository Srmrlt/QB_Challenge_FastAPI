# Test assignment for HDS

Your goal is to design and build a simple web-service that could serve a __large__ number of users concurently.

## Test Data
### Generate
Test data will be saved at the `WORKING_DIR/data`
```shell
pip install -r req.txt
python generate_bin.py
```

### Structure 
Files are structured via the layout in the file system itself, under the `data/` you will find a cascade of folders each representing a year, month and a date. For example: `data/2023/12/29/` will hold the data for `2023-12-29`. In each date folder there are:    
1. binary files `%INSTRUMENT%@%EXCHANGE%.dat` which hold some information about the instrument.    
2. `manifest.xml` which carries meta information about the binary files.      

## API Requirements:
Your task is to implement endpoints listed below.

1. Find availiability of the instrument by date. Endpoint: `/api/isin_exists`.   
1.1. Inputs: `date: str (YYYY-mm-dd)`, `instrument: str | None`, `exchange: str | None`.    
1.2. Response: on success `{ "result": list[Payload] }`, on failure return empty list.   
where `Payload` is:
```
class Payload:
    instrument: str
    exchange: str
    iid: int
    market_type: str
```
2. Query availiability by time interval. Endpoint: `/api/isin_exists_interval`.    
2.1. Inputs: `date: str (YYYY-mm-dd)`, `instrument: str`, `exchange: str`.     
2.2. Response: on success `{ "result": Payload }`, on failure `{ "result": None }`.     
3. Get instrument info by ID. Endpoint `/api/iid_to_isin`.    
3.1 Inputs: `date: str (YYYY-mm-dd)`, `iid: int`     
3.2. Response: `{ "result": Payload }`, on failure `{ "result": None }`    


## HTTPS stream:
1. Send binary file data in chunks.     
1.1 Inputs: `chunk_size: int` -- number of bytes sent at once.    
1.2. Response: HTTP stream transmitting bytes to the client in chunks.   
