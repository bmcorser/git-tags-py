#! /bin/bash

root=$(pwd)
local_repo="${root}/local"
remote_repo="${root}/remote"
pkgs=(a b c d e)
init_repo () {
    repo_dir=$1
    mkdir ${repo_dir}
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

tag release a b c d -m a
