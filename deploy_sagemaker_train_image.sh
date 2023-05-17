#!/bin/bash
# -- deploy_sagemaker_train_image.sh -------------------------------------------
#
# トレーニング用コンテナをECRにデプロイするスクリプト
#
# Copyright (c) 2023- AUCNET IBS
#
# ------------------------------------------------------------------------------

set -uo pipefail
set -e

readonly ME=${0##*/}

export AWS_PAGER=""
export AWS_REGION="us-west-2"

display_usage() {

    cat <<EOE

        トレーニング用コンテナをECRにデプロイするスクリプト

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

    ./deploy_sagemaker_image.sh \
        -r "${AWS_REGION}" \
        -n "sagemaker-yolov7-train" \
        -d "sagemaker/train"

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
