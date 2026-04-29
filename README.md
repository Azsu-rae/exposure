
Create an **image** \[T\]agged `user_service`:

```
docker build -f services/user_service/Dockerfile -t user_service .
```

*Create* and *start* a **container** from an image:

```
docker run -p 8000:8000 --env-file services/user_service/.env --add-host=host.docker.internal:host-gateway user_service
```
