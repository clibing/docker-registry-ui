#!/usr/bin/env bash

set -e

SPRING_ENV=${SPRING_ENV:-"dev"}

IMAGE_NAME=${IMAGE_NAME:-"none"}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"reg.linuxcrypt.cn"}
DOCKER_REGISTRY_USER=${DOCKER_REGISTRY_USER:-"gitlab"}
DOCKER_REGISTRY_PASSWORD=${DOCKER_REGISTRY_PASSWORD:-""}

while getopts "e:" OPT; do
    case $OPT in
        e)
            SPRING_ENV=$OPTARG;;
    esac
done

# online will update this
if [ "${SPRING_ENV}" == "cloud" ];then
    echo -e "SPRING_ENV: cloud"
    docker login ${DOCKER_REGISTRY} -u ${DOCKER_REGISTRY_USER} -p ${DOCKER_REGISTRY_PASSWORD}
    docker build -t ${IMAGE_NAME} --build-arg SPRING_PROFILE_ACTIVE=${SPRING_ENV} --build-arg PROJECT_BUILD_FINALNAME=${PROJECT_BUILD_FINALNAME} -f Dockerfile.x86_64 .
fi

# arm
if [ "${SPRING_ENV}" == "arm" ];then
    echo -e "SPRING_ENV: arm"
    docker build -t ${IMAGE_NAME} --build-arg SPRING_PROFILE_ACTIVE=${SPRING_ENV} --build-arg PROJECT_BUILD_FINALNAME=${PROJECT_BUILD_FINALNAME} -f Dockerfile.arm .
    # docker login ${DOCKER_REGISTRY} -u ${DOCKER_REGISTRY_USER} -p ${DOCKER_REGISTRY_PASSWORD}
    # docker -H ${BUILD_HOST} login ${DOCKER_REGISTRY} -u ${DOCKER_REGISTRY_USER} -p ${DOCKER_REGISTRY_PASSWORD}
fi

docker push ${IMAGE_NAME}
docker rmi ${IMAGE_NAME}
echo "Build image success --> $IMAGE_NAME"
