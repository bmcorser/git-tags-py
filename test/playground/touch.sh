#! /bin/bash

root=$(pwd)
repos="${root}/repos"
local_repo="${repos}/local"

cd ${local_repo}

for pkg in $@
do
    :
    echo $(date) > ${local_repo}/${pkg}/deploy
done;

git add .
git commit -m "Commit on $(date)"
