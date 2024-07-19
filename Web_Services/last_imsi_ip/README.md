# Get Last IMSI IP API

This tool provides a web service to get the last `IP` assigned to an `IMSI` and the last `IMSI` to which an `IP` assigned.

## Endpoints

> | Protocol      |  URL                                   |
> |---------------|----------------------------------------|
> | HTTP          |  SERVER_IP:PORT/ip/\<ip>               |
> | HTTP          |  SERVER_IP:PORT/imsi/\<imsi>           |

## Parameters

> | name      |  type     | data type   | description                                    |
> |-----------|-----------|-------------|------------------------------------------------|
> | ip        |  required |      string |ip of user                                      |
> | imsi      |  required |      string |imsi of user                                    |

## Responses

> | http code     | content-type         | response                           |
> |---------------|----------------------|-------------------------------------
> |`200`          | `application/json`   | `imsi`                             |
> |`200`          | `application/json`   | `ip`                               |

## Example 

> ```bash
>  curl http://127.0.0.1:5000/last_imsi/37.114.201.128
> ```
> {"ip":"37.114.201.128","last_imsi":"432459999959181"}


> ```bash
>  curl http://127.0.0.1:5000/last_ip/432459999921502
> ```
> {"imsi":"432459999921502","last_ip":"185.197.69.229"}