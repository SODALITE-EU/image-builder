#!/bin/sh

[ $# != 1 ] && echo "Usage: $0 input-file.yaml" && exit 1

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

input=$(get_abs_filename $1)

docker run -it -v $input:/input.yaml \
	   -v /var/run/docker.sock:/var/run/docker.sock \
	   --net=host \
	   sodaliteh2020/image-builder
