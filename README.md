# docker-registry-ui

run 
> If you don't configure account password authentication, ignore the 'USER' and 'PASSWD' please!

```
docker run -d -p 8080:8080 -e HOST='registry_host' -e PORT='registry_port' -e USER='registry_user' -e PASSWD='registry_pass' lioncui/docker-registry-ui
```
