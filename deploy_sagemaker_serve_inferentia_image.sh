#!/bin/bash
# -- deploy_sagemaker_serve_inferentia__image.sh -------------------------------
#
# Inferentia推論用コンテナをECRにデプロイするスクリプト
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

        Inferentia推論用コンテナをECRにデプロイするスクリプト

        構文: ./${ME}

EOE
    exit 0

}

check_sanity() {

    [[ $(command -v aws) ]] \
        || whoopsie "Please install aws first."

    [[ $(command -v docker) ]] \
        || whoopsie "Please install Docker first."

}

deploy() {

    ./deploy_sagemaker_image.sh \
        -r us-west-2 \
        -n "sagemaker-yolov7-serve-inferentia" \
        -d "sagemaker/serve_inferentia"

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