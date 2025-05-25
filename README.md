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

## Load testing:
```bash
wrk -t4 -c100 -d30s -s post.lua http://localhost:8000/echo 
```

Other tools: Apache JMeter, Locust(Python)

### Test results:
One instance of the router-service could handle ~79 RPS with 400msec average latency and 0% error rate.

```bash
(venv) niteshsinha@Niteshs-MacBook-Pro router-service % wrk -t4 -c50 -d30s -s post.lua http://localhost:8000/echo
Running 30s test @ http://localhost:8000/echo
  4 threads and 50 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   624.98ms   86.75ms   1.04s    71.45%
    Req/Sec    20.40     12.06    79.00     80.89%
  2221 requests in 30.08s, 467.80KB read
  Socket errors: connect 0, read 0, write 0, timeout 11
  Non-2xx or 3xx responses: 23
Requests/sec:     73.84
Transfer/sec:     15.55KB
(venv) niteshsinha@Niteshs-MacBook-Pro router-service %
(venv) niteshsinha@Niteshs-MacBook-Pro router-service %
(venv) niteshsinha@Niteshs-MacBook-Pro router-service %
(venv) niteshsinha@Niteshs-MacBook-Pro router-service % wrk -t2 -c50 -d30s -s post.lua http://localhost:8000/echo
Running 30s test @ http://localhost:8000/echo
  2 threads and 50 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   619.44ms   89.41ms   1.78s    82.55%
    Req/Sec    40.11     20.57   121.00     76.71%
  2323 requests in 30.05s, 489.43KB read
  Socket errors: connect 0, read 0, write 0, timeout 7
  Non-2xx or 3xx responses: 19
Requests/sec:     77.31
Transfer/sec:     16.29KB
(venv) niteshsinha@Niteshs-MacBook-Pro router-service %
(venv) niteshsinha@Niteshs-MacBook-Pro router-service %
(venv) niteshsinha@Niteshs-MacBook-Pro router-service %
(venv) niteshsinha@Niteshs-MacBook-Pro router-service % wrk -t2 -c30 -d30s -s post.lua http://localhost:8000/echo
Running 30s test @ http://localhost:8000/echo
  2 threads and 30 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   392.09ms   38.67ms 584.83ms   83.60%
    Req/Sec    38.97     20.88   110.00     68.45%
  2287 requests in 30.05s, 482.41KB read
Requests/sec:     76.11
Transfer/sec:     16.05KB
```

Also tried increasing Uvicorn workers to 4 and noticed average RPS 



