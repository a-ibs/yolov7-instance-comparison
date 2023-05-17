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

        構文: ./${ME} -r <region> -n <repository_name> -p <s3_path>

            <region>
                リージョン

            <repository_name>
                リポジトリー名

            <s3_path>
                モデルファイルが格納されている S3 パス

EOE
    exit 0

}

check_sanity() {

    [[ $(command -v aws) ]] \
        || whoopsie "Please install aws first."

}

deploy() {

    region=$1
    image=$2
    s3_path=$3
    instance_type=$4

    account=$(aws sts get-caller-identity --query Account --output text)

    fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"

    # shellcheck disable=SC2140
    aws sagemaker create-model \
        --region "${region}" \
        --model-name "${image}-model" \
        --execution-role-arn "arn:aws:iam::${account}:role/sagemaker-yolov7-serve-role" \
        --primary-container Image="${fullname}",ModelDataUrl="s3://${S3_BUCKET}/${s3_path}"

    # shellcheck disable=SC2140
    aws sagemaker create-endpoint-config \
        --region "${region}" \
        --endpoint-config-name "${image}-endpoint-config" \
        --production-variants \
            VariantName="${image}-endpoint-variant",ModelName="${image}-model",InitialInstanceCount=1,InstanceType="${instance_type}",InitialVariantWeight=1.0

    aws sagemaker create-endpoint \
        --region "${region}" \
        --endpoint-name "${image}-endpoint" \
        --endpoint-config-name "${image}-endpoint-config"

}

main() {

    local region=''
    local repository_name=''
    local s3_path=''
    local instance_type=''

    [[ $# -eq 0 ]] && display_usage

    while getopts i:n:p:r:h opt; do
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
            p)
                s3_path=$OPTARG
            ;;
            i)
                instance_type=$OPTARG
            ;;
            \?)
                whoopsie "Invalid option!"
            ;;
        esac
    done

    check_sanity

    deploy "${region}" "${repository_name}" "${s3_path}" "${instance_type}"

}

whoopsie() {

    local message=$1

    echo "${message} Aborting..."
    exit 192

}

main "$@"

exit 0
