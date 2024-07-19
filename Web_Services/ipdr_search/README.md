# Search in Ipdr Files API

Search in IPDRs API provides a web service that gets IP, start_time, end_time, service_id from user then returns all the records matching with those features.

## Endpoints

> | Protocol      |  URL                      |
> |---------------|---------------------------|
> | HTTP          |  SERVER_IP:PORT/ipdr      |

## Parameters

> | name      |  type     | data type   | description                                    |
> |-----------|-----------|-------------|------------------------------------------------|
> | IP        |  required | string      | ip in the `ddd.ddd.ddd.ddd_ss` format          |
> | from_date |  required | timestamp   |                                                |
> | to_date   |  required | timestamp   |                                                |
> | service_id|  optional | string      |                                                |

## Responses

> | http code     | content-type                      | response                  |
> |---------------|-----------------------------------|---------------------------|
> |`200`          | `application/json`                |`OK`                       |
> |`404`          | `application/json`                |`Not Found`                |  
> |`400`          | `application/json`                |`Bad Request`              |

## Example

```bash
  curl -X POST  http://localhost:5000/ipdr/ \-H 'Content-Type: application/json' \
  -d '{
    "from_date": 1687099400,
    "to_date": 1687099900,
    "IP": "142.250.201.138"
  }'

  output = 
  [
    {  
        "ipAddress": "142.250.201.138" ,
        "layerFourprotocol"  : "TCP" ,
        "layerThreeprotocol" : "IPX" ,
        "macAddress" : "",
        "serviceId" : "00543547-a263a4ed8-a1d0-c567eedbb8e8",
        "serviceType" : "WIRELESS" ,
        "sourceIpAddress" : "142.250.201.138" ,
        "sourcePort" : "443",
        "targetIpAddress" : "37.114.248.116",
        "targetPort" : "45120"
    }
  ]
