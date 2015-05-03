#! /bin/bash

root=$(pwd)
repos="${root}/repos"
local_repo="${repos}/local"
remote_repo="${repos}/remote"
init_repo () {
    set -e
    repo_dir=$1
    mkdir -p ${repo_dir}
    cd ${repo_dir}
    git init
}

init_repo ${remote_repo}

init_repo ${local_repo}
git remote add origin ${remote_repo}

for pkg in $@
do
    :
    mkdir ${local_repo}/${pkg}
    echo $(date) > ${local_repo}/${pkg}/deploy
done;

git add .
git commit -m a
