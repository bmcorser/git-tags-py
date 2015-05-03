#! /bin/bash

root=$(pwd)
local_repo="${root}/local"

cd ${local_repo}

for pkg in $@
do
    :
    echo $(date) > ${local_repo}/${pkg}/deploy
done;

git add .
git commit -m "Commit on $(date)"
