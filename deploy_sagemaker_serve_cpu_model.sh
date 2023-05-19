#!/bin/bash
# -- deploy_sagemaker_serve_cpu_model.sh ---------------------------------------
#
# CPU推論モデルをデプロイするスクリプト
#
# Copyright (c) 2023- AUCNET IBS
#
# ------------------------------------------------------------------------------

set -uo pipefail
set -e

readonly ME=${0##*/}

export AWS_PAGER=""
export AWS_REGION="us-west-2"
export INSTANCE_TYPE="ml.m5.xlarge"

display_usage() {

    cat <<EOE

        CPU推論モデルをデプロイするスクリプト

        構文: ./${ME}

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

    ./deploy_sagemaker_model.sh \
        -r "${AWS_REGION}" \
        -n "sagemaker-yolov7-serve-cpu" \
        -p "yolov7_sample/serve/model.tar.gz" \
        -i "${INSTANCE_TYPE}"

}

main() {

    while getopts h opt; do
        case $opt in
            h)
                display_usage
            ;;
            \?)
                whoopsie "Invalid option!"
            ;;
        esac
    done

    check_sanity

    deploy

}

whoopsie() {

    local message=$1

    echo "${message} Aborting..."
    exit 192

}

main "$@"

exit 0
