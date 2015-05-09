#! /bin/bash

set -e
root=$(pwd)
local_repo="${root}/local"
remote_repo="${root}/remote"

init_repo () {
    repo_dir=$1
    mkdir -p ${repo_dir}
    cd ${repo_dir}
    git init
}

init_repo ${remote_repo}

init_repo ${local_repo}
git remote add origin ${remote_repo}
git config user.name playground-user
git config user.email user@playground

for pkg in $@
do
    :
    mkdir ${local_repo}/${pkg}
    echo $(date) > ${local_repo}/${pkg}/deploy
done;

git add .
git commit -m 'Initial playground commit'
