#!/bin/bash
# -- deploy_sagemaker_model.sh -------------------------------------------------
#
# SageMaker用モデルをデプロイするスクリプト
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

        構文: ./${ME} -r <region> -n <repository_name>

            <region>
                リージョン

            <repository_name>
                リポジトリー名

EOE
    exit 0

}

check_sanity() {

    [[ $(command -v aws) ]] \
        || whoopsie "Please install AWS CLI first."

}

delete_model() {

    region=$1
    image=$2

    aws sagemaker delete-endpoint \
        --region "${region}" \
        --endpoint-name "${image}-endpoint"

    aws sagemaker delete-endpoint-config \
        --region "${region}" \
        --endpoint-config-name "${image}-endpoint-config"

    aws sagemaker delete-model \
        --region "${region}" \
        --model-name "${image}-model" \

}

main() {

    local region=''
    local repository_name=''

    [[ $# -eq 0 ]] && display_usage

    while getopts n:r:h opt; do
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
            \?)
                whoopsie "Invalid option!"
            ;;
        esac
    done

    check_sanity

    delete_model "${region}" "${repository_name}"

}

whoopsie() {

    local message=$1

    echo "${message} Aborting..."
    exit 192

}

main "$@"

exit 0
