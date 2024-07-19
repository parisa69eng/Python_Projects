# Charging Department

## Users Usage API

### Get users' usage in **the last year**

#### URL

> | Protocol      |  URL     |
> |---------------|-----------------|
> | HTTP          |  172.20.13.2:6161/\<imsi\>    |
> | HTTP          |  172.20.13.3:6161/\<imsi\>    |


#### Parameters

> | name      |  type     | data type   | description                                    |
> |-----------|-----------|-------------|------------------------------------------------|
> | from |  required | string      | Start persian date in the `YYYY-MM-DD` format  |
> | to   |  required | string      | End persian date in the `YYYY-MM-DD` format    |


##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `201`         | `text/plain;charset=UTF-8`        | `Configuration created successfully`                                |
> | `400`         | `application/json`                | `{"code":"400","message":"Bad Request"}`                            |
> | `405`         | `text/html;charset=utf-8`         | None                                                                |

##### Example URL

> ```bash
>  curl http://172.20.13.2:6161/cdrs/imsis/imsi?from=1402-01-10&to=1402-01-20
> ```