docker container run \
  -dit \
  --rm \
  -p 8999:8888 \
  --name staff-db \
  --mount type=bind,source=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)/../,target=/home/jovyan/work \
  --mount type=bind,source=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)/../../DATA/staff-db,target=/home/jovyan/work/data \
  kmrachet/staff-db:jupy3.12.7
