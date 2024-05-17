# QB_Challenge

## Description

This web service is designed to meet the requirements of the test assignment 
provided by 'QB' company. The service provides API endpoints to check the 
availability of financial instruments by date and time intervals and fetch 
instrument information by ID. Additionally, it supports streaming binary file 
data to clients.
You can find the detailed assignment in the 
[task](https://github.com/Srmrlt/QB_Challenge/tree/main/task) 
directory in this repository.


## Technologies Used

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* PostgreSQL
* Docker
* Docker Compose
* Nginx
* GitHub Actions

## Requirements

* [Docker](https://www.docker.com/get-started/)
* Docker Compose V2

## Local Setup and Deployment

1. **Clone the Repository**:
    ```shell
    git clone https://github.com/Srmrlt/QB_Challenge.git
    git switch FastAPI-main
    cd QB_Challenge/infra
    ```
2. **Environment Variables.** Copy the .env.dev file from the project infra folder
to a new file named .env and fill in/adjust the necessary environment variables:
    ```shell
    cp ../.env.example .env
    ```
3. **Building and Running the Containers.**
Use Docker Compose to build and start the containers:
    ```shell
    docker compose up --build -d
    ```
4. **Stopping and Removing Containers, Volumes, and Images**:
    ```shell
    docker compose down --rmi all -v
    ```
5. The project should now be running at http://localhost:80. 

## API Endpoints

Based on the test assignment, the following endpoints are implemented:

* ### Check Instrument Availability by Date:

`GET /api/isin_exists?date=YYYY-mm-dd&instrument=<instrument>&exchange=<exchange>`

* ### Check Availability by Time Interval:

`GET /api/isin_exists_interval?date_from=YYYY-mm-dd&date_to=YYYY-mm-dd&instrument=<instrument>&exchange=<exchange>`

* ### Get Instrument Info by ID:

`GET /api/iid_to_isin?date=YYYY-mm-dd&iid=<instrument_id>`

* ### Stream Binary File Data:

`GET /stream?date=YYYY-mm-dd&chunk_size=<size_in_bytes>`

## Additional Notes

Data generation and parsing into the database occur automatically 
upon project startup.
