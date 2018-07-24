# -*- coding: utf-8 -*-
# author :  liuboxun
# email  :  wmsjhappy@gmail.com
# date   :  2018/7/19 上午10:26
# desc   : 
# version:  1.0
#

from docker_registry_client.Image import Image
from docker_registry_client.Repository import RepositoryV2
from docker_registry_client._BaseClient import BaseClientV2, BaseClientV1

from docker_registry_client.DockerRegistryClient import DockerRegistryClient

host = 'http://172.16.0.36:5000'
config = {
    'api_timeout': 30
}
client1 = BaseClientV1(host, *config)
client2 = BaseClientV2(host, *config)

namespace = 'clibing'
respository = 'clibing/armhf-oracle-jdk'
tag = '8u171'

print client2.catalog()
print client2.get_repository_tags(respository)
print client2.check_status()

# image = Image(respository, client1)


# print client2.get_repository_tags(respository)

manifest_digest_new = client2.get_manifest_and_digest_new(respository, tag)
print("=" * 50)
print(manifest_digest_new[0])
print(manifest_digest_new[1])
try:
    print client2.delete_manifest(respository, manifest_digest_new[1])
except Exception as e:
    print(e)

size = 0
for layer in manifest_digest_new[0]['layers']:
    size += long(layer['size'])
print(size/1024)


manifest_digest = client2.get_manifest_and_digest(respository, tag)
print("+" * 50)
print(manifest_digest[0])
print(manifest_digest[1])

print("_" * 50)

try:
    print client2.delete_manifest(respository, manifest_digest[1])
except Exception as e:
    print(e)

drClient = DockerRegistryClient(host)
print("-" * 50)
print "namespaces", drClient.namespaces()
repositories = drClient.repositories(namespace)
print("*" * 50)
print repositories
for repository in repositories.keys():
    print repository
    rv2 = repositories[repository]
    for tag in rv2.tags():
        print "tag:", tag
        print(rv2.manifest(tag))




#
