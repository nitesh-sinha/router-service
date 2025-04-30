Assumptions:
1. Healthcheck API performance mirrors actual business endpoint performance


Interesting issues:
1. response.raise_for_status() fired even for successful GET and POST. Could it be because localhost resolved to both IPv6 and IPv4 address. And IPv6 returned error in connection?
2. Adding logging for async calls
3. Debugging via IDE for async calls?
4. Healthcheck supposed to be sent every 10 seconds but sometimes it was delayed by a few seconds?
    a. TUrns out this was because the DEGRADED instance responds slowly to healthcheck request and that blocks sending healthcheck request out to HEALTHY and UNHEALTHY instances too since asyncio.gather waits for all tasks to complete.
    b. Fixed this by adding calculating wait time for complete healthcheck to complete for ALL instances and then sleep only for 10-<wait_time> seconds only instead of 10 seconds. 
    c. Then noticed that healthcheck time for DEGRADED instance skipped one extra 10 sec interval, so healthchecks happenned after 40 sec for those instances instead of 30 sec. Fixed this by  "instance.update_last_healthcheck_time(start_time)" # Use start_time instead of stop_time otherwise healthcheck for DEGRADED instance is skipped for one more 10sec interval
