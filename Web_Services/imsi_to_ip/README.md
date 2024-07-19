# IMSI to IP API

IMSI to IP API provide a web service that get IMSI from user and return IP of user.

## Endpoints

> | Protocol      |  URL     |
> |---------------|-----------------|
> | HTTP          |  SERVER_IP:PORT/imsis/\<imsi>  

## Parameters

> | name      |  type     | data type   | description                                    |
> |-----------|-----------|-------------|------------------------------------------------|
> | imsi      |  required |      string |imsi of user

## Responses

> | http code     | content-type         | response            
> |---------------|----------------------|-------------------------------------
> |`201`          | `application/json`   | `ip,status`                             |

## Example 

> ```bash
>  curl http://127.0.0.1:5000/imsis/432459999909690
> ```
{ "IP":"37.221.13.227/32" , "status":"Active" }
