# High Usage Users

This tool provides a web service to get `from_date` and `to_date` and `volume_threshold`, then return imsi of users with usage higher than volume_threshold.

## Endpoints

> | Protocol      |  URL                                   |
> |---------------|----------------------------------------|
> | HTTP          |  SERVER_IP:PORT/high_usage_users       |

## Body

> | name              |  type     | data type        | default | description         |
> |-------------------|-----------|------------------|---------|-------------        |
> |from_date          |  required |string            |   -     |start time with '%Y-%m-%d'
> |to_date            |  required |string            |   -     |end time with '%Y-%m-%d' |
> |volume_threshold   |  required |integer           |   -     |it is volume that compare usage and  its unit is GB |

## Responses

> | http code     | content-type         | response                           |
> |---------------|----------------------|-------------------------------------
> |`200`          | `application/json`   | `result`                           |
> |`400`          | `application/json`   | `Bad Request`                      |
> |`500`          | `application/json`   | `Internal Server Error`

## Example

```bash
curl -X POST
-H "Content-Type: application/json"
-d '{
"volume_threshold": 1000,
"from_date": "1401-12-10",
"to_date": "1401-12-17"
}'http://localhost:5000/high_usage_users/

{"432459999921503": 264.7057199990377}
```
