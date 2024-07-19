
# IP to IMSI API

IP to IMSI API provide a web service that get IP from user and return IMSI of user.

## Endpoints

> | Protocol      |  URL     |
> |---------------|-----------------|
> | HTTP          |  SERVER_IP:PORT/ips/\<ip>

## Parameters

> | name      |  type     | data type   | description                                    |
> |-----------|-----------|-------------|------------------------------------------------|
> | ip        |  required | string      | ip in the `ddd.ddd.ddd.ddd_ss` format  |

## Responses

> | http code     | content-type                      | response
> |---------------|-----------------------------------|--------------------------
> | `201`         | `application/json`                | `imsi, status`            |
> |`successfully` |                                   |
> |`None`         |                                   |

## Example 

> ```bash
>  curl http://127.0.0.1:5000/ips/81.91.155.246
> ``` 
> { "imsi":"432459999909690" , "status":"Active" }


