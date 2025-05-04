# Router Service

A routing service that distributes traffic across multiple downstream application instances based on their health status. It currently implements `round-robin` routing algorithm but can be extended to include other types of more sophisticated routing algorithms. It has inbuilt health monitoring capabilities.

## Features

- Load balancing(Round-Robin) across multiple application instances
- Health monitoring of application instances
- Configurable routing algorithms, health check intervals and thresholds
- Automatic instance health status tracking (Currently supports these 3 health statuses - `HEALTHY`, `DEGRADED`, `UNHEALTHY`)

## Usage

1. Clone the repository:
```bash
git clone git@github.com:nitesh-sinha/router-service.git
cd router-service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The service is configured via `config.json`:

```json
{
  "app_instances": [
    "http://localhost:9001",
    "http://localhost:9002",
    "http://localhost:9003",
    "http://localhost:9004"
  ],
  "healthcheck_response_time_threshold": 5,
  "health_check_interval": 10,
  "degraded_check_interval": 30,
  "router_port": 8000,
  "routing_algorithm": "round_robin"
}
```

Configuration parameters:
- `app_instances`: List of application instance URLs
- `healthcheck_response_time_threshold`: Maximum response time (in seconds) before marking an instance as DEGRADED
- `health_check_interval`: Time interval (in seconds) between health checks for HEALTHY and UNHEALTHY instances
- `degraded_check_interval`: Time interval (in seconds) between health checks for DEGRADED instances
- `router_port`: Port on which the router service will run
- `routing_algorithm`: Currently supports "round_robin"

## Health Monitoring

The service continuously monitors the health of application instances. It categorizes the app instances into one of 3 states:

- **HEALTHY**: Instance responds to healthchecks within the configured threshold.
- **DEGRADED**: Instance responds to healthchecks but exceeds the threshold
- **UNHEALTHY**: Instance fails to respond(healthchecks never reach the instance)

Health checks are performed:
- Every `health_check_interval` seconds for HEALTHY and UNHEALTHY instances
- Every `degraded_check_interval` seconds for DEGRADED instances


## Testing the Service

1. As a pre-requisite, run a few downstream application instances which this router can route the traffic to. As an example, you can run https://github.com/nitesh-sinha/customhttpserver on multiple ports locally.
2. Configure the `protocol://IP_address:port` information of the running downstream instances as `app_instances` in `config.json` of router-service.
3. Run this router-service using one of the 2 methods described below. By default, it runs at port 8000 and exposes an endpoint called `/echo`
4. Test by sending POST request with JSON body to the router-service:
```bash
curl -v -X POST --header 'Content-Type: application/json' http://127.0.0.1:8000/echo -d '{"gameid": "coolknight", "payment":"500", "currency": "INR", "timestamp": "2025-05-04T12:00:00Z"}'
```

- Steps to run this router-service:

### Using the run script
```bash
./run.sh
```

### Manual execution
```bash
PYTHONPATH=$PYTHONPATH:. python main.py
```


## Logging

Router-service writes logs to `router.log` file.