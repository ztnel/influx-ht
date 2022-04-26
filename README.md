# High Throughput Data Aggregation

Modified: 2022-04

Python Influx client for storing Near Real-Time data.

## Quickstart
You will need docker engine and `docker-compose` installed on your system. Installing docker is system dependant see [here](https://docs.docker.com/get-docker/) for installation instructions. You can install docker compose through pip:
```bash
python3 -m pip install docker-compose
```

```bash
docker-compose up
```

Once the services spin up head to http://localhost:8086 on your local browser to login to the influx client. The username and password for this instance is defined [here](.env) feel free to change any of the default influx config I have set.

### Teardown
To teardown the services and resources:
```bash
docker-compose down --rmi all
```

## License
This project is licensed under the terms of the [MIT License](LICENSE)