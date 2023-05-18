#!/bin/bash
# -- deploy_sagemaker_image.sh -------------------------------------------------
#
# コンテナをECRにデプロイするスクリプト
#
# Copyright (c) 2023- AUCNET IBS
#
# ------------------------------------------------------------------------------

set -uo pipefail
set -e

readonly ME=${0##*/}

export AWS_PAGER=""

display_usage() {

    cat <<EOE

        コンテナをECRにデプロイするスクリプト

        構文: ./${ME} -r <region> -n <repository_name> -d <directory_path>

            <region>
                リージョン

            <repository_name>
                リポジトリー名

            <directory_path>
                Dockerfile の格納されているディレクトリーパス

EOE
    exit 0

}

check_sanity() {

    [[ $(command -v aws) ]] \
        || whoopsie "Please install AWS CLI first."

    [[ $(command -v docker) ]] \
        || whoopsie "Please install Docker first."

}

deploy() {

    region=$1
    image=$2
    path=$3

    account=$(aws sts get-caller-identity --query Account --output text)

    fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"

    aws ecr get-login-password \
        --region "${region}" \
        | docker login \
            --username AWS \
            --password-stdin "${account}".dkr.ecr."${region}".amazonaws.com

    docker build -t "${image}" "${path}"
    docker tag "${image}" "${fullname}"
    docker push "${fullname}"

}

main() {

    local region=''
    local repository_name=''
    local directory_path=''

    [[ $# -eq 0 ]] && display_usage

    while getopts d:n:r:h opt; do
        case $opt in
            h)
                display_usage
            ;;
            r)
                region=$OPTARG
            ;;
            n)
                repository_name=$OPTARG
            ;;
            d)
                directory_path=$OPTARG
            ;;
            \?)
                whoopsie "Invalid option!"
            ;;
        esac
    done

    check_sanity

    deploy "${region}" "${repository_name}" "${directory_path}"

}

whoopsie() {

    local message=$1

    echo "${message} Aborting..."
    exit 192

}

main "$@"

exit 0
