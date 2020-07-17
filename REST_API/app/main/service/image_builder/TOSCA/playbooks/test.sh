registry_ip=$1
test_path=tests/tests-yaml
image_names=tests/image_names

# Usage: ./test.sh [registry_ip]

# remove old images
echo "Cleaning old docker test images..."
docker rmi $(docker images | grep tests | tr -s ' ' | cut -d ' ' -f 1,2 --output-delimiter=:) > /dev/null 2>&1

# transform tests to yaml
echo "Moving json tests to yaml..."
ansible-playbook --connection=local --inventory localhost, -e 'ansible_python_interpreter="/usr/bin/python3"' -e @tests/params.yaml -e registry_ip="${registry_ip}" tests/json_to_yaml.yml >/dev/null

echo "Testing..."
COUNTER=1
return_code=0
for path in "$test_path"/* ; do

  # run test on image builder
  stack_trace=$( ansible-playbook --connection=local --inventory localhost, -e 'ansible_python_interpreter="/usr/bin/python3"' -e @"${path}" -e building_workdir=workdir builder/build.yml -vvv 2>&1)

  filename=$(basename "$path")
  test_name="${filename%.*}"
  image_name="$image_names/$test_name.txt"

  # read image_name
  while IFS= read -r line
  do

    # remove image, inspect return_value (images exists or not)
    docker_image_name="${line/registry_ip/$registry_ip}"
    docker rmi ${docker_image_name} > /dev/null
    RESULT=$?
    if [[ $RESULT -eq 0 ]]; then
      echo "TEST $COUNTER....$docker_image_name.....OK"
    else
      echo "TEST $COUNTER....$docker_image_name.....FAILED"
      return_code=1
      echo "-------------------------Stacktrace for TEST $COUNTER-------------------------"
      echo "$stack_trace"
      echo "----------------------End of stacktrace for TEST $COUNTER---------------------"
    fi

    COUNTER=$((COUNTER+1))

  done < "$image_name"

done

echo Cleaning up...
# clean workdir
rm -rf builder/workdir/

# remove remaining docker test images
docker rmi $(docker images | grep tests | tr -s ' ' | cut -d ' ' -f 1,2 --output-delimiter=:) > /dev/null 2>&1

echo Done.
exit $return_code

