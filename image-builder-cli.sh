#!/bin/sh

[ $# != 1 ] && echo "Usage: $0 input-file.yaml" && exit 1

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

input=$(get_abs_filename $1)

get_extra_volume_mounts() {
  # $1 : input file

  local_dockerfile=$(grep file:\/\/ $1 | sed -e 's/^.*file:\/\///')
  local_build_context=$(grep path: $1 | sed -e 's/^.*path:[ \t]*//')

  extra_mounts=""

  [ ! -z $local_dockerfile ] && extra_mounts="$extra_mounts -v $local_dockerfile:$local_dockerfile"
  [ ! -z $local_build_context ] && extra_mounts="$extra_mounts -v $local_build_context:$local_build_context"

  echo $extra_mounts
}

docker run -it -v $input:/input.yaml \
	   -v /var/run/docker.sock:/var/run/docker.sock \
	   $(get_extra_volume_mounts $1) \
	   --net=host \
	   sodaliteh2020/image-builder-cli
