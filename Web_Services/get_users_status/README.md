# GET Users Status in Tacs/eNodeB

This tool provides a web service to get `TAC` or `enodeb_id` then return active/inactive users.

## Endpoints

> | Protocol      |  URL                                         |
> |---------------|----------------------------------------------|
> | HTTP          |  SERVER_IP:PORT/users_status/tacs/\<id>      |
> | HTTP          |  SERVER_IP:PORT/users_status/enodebs/\<id>   |

## Parameters

> | name      |  type     | data type   | description  |
> |-----------|-----------|-------------|--------------|
> | tac       |  required | string      |TAC id        |
> | id        |  required | integer     |eNodeB id     |

## Responses

> | http code     | content-type         | response  |
> |---------------|----------------------|-----------|
> |`200`          | `application/json`   | `OK`      |
> |`404`          | `application/json`   |`NOT_FOUND`|

## Example

```bash
 curl http://127.0.0.1:5000/users_status/tacs/16

{"active_users": ["432459999956496", "432459999969402", "432459999951053", "432459999925646"],
"inactive_users": ["432459999956496", "432459999969402", "432459999951053", "432459999925646"]}
```

```bash
curl http://127.0.0.1:5000/users_status/enodebs/2282

{"active_users": ["432459999973744", "432459999962558", "432459999948481", "432459999922237", "432459999946060", "432459999908707", "432459999924609", "432459999946059","432459999947292"],
"inactive_users": ["432459999973744", "432459999962558", "432459999948481", "432459999922237", "432459999946060", "432459999908707",  "432459999959612"]}
```
