# Summary of Findings

Modified: 2022-04

## Purpose
This demo aims to understand the considerations and limitations involving high throughout streaming and data storage for systems that want to operate at near real-time.

Below I highlight some of the main takeways:

## Data Retention Policy
As the amount of data increases the queries become significantly slower. This works against a systems need for near real time analytics. In order to allow for speedy queries on short-term data we need to specify a data retention policy. This will define how long data is kept before being automatically removed by an internal garbage collection mechanism.

For NRT systems a short data retention policy is neccssary in order to act on the data at low latency. Therefore the benefit/cost ratio is the desired span of data vs the tolerable latency.

## Batch Writing
At the end of the day, writing to any database requires file I/O. The rate at which we write to the database is critical for reducing overhead. If we write a large batch of aggregated data every second, we will have efficient read and writes at the cost of a 1 second latency. On the contrary, writing a single sample every microsecond will result in large computing overhead and possibly will cause inaccurate writing timestamps due to file I/O bottlenecking. The benefit/cost ratio is the system performance vs the tolerable latency.

A synchronous fixed batch write will allow us to adjust a batch size to optimize the benefit/cost ratio. Finding the optimal batch write is system dependant.