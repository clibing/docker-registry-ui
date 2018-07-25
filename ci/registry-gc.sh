#!/usr/bin/env bash
# date    : 2018-07-25 11:56
# email   : wmsjhappy@gmail.com
# author  : clibing
# function: registry garbage gc support --dry-run
#           dry-run
# github  : https://github.com/clibing/dockerfile/tree/master/shell
set -e

CONTAINER_NAME=${CONTAINER_NAME:-"registry"}
REGISTRY_CONFIG=${REGISTRY_CONFIG:-"/etc/docker/registry/config.yml"}
DRY_RUN=${DRY_RUN:-"false"}

while getopts "n:r:d:" OPT; do
    case $OPT in
        n)
            CONTAINER_NAME=$OPTARG;;
        r)
            REGISTRY_CONFIG=$OPTARG;;
        d)
            DRY_RUN=$OPTARG;;
    esac
done

if [ "$DRY_RUN" == "true" ];then
        COMMAND="registry garbage-collect ${REGISTRY_CONFIG}"
else
        COMMAND="registry garbage-collect -d ${REGISTRY_CONFIG}"
fi

docker exec ${CONTAINER_NAME} ${COMMAND}