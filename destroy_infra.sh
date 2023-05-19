#!/bin/bash
# -- destroy_infra.sh ----------------------------------------------------------
#
# インフラを削除するスクリプト
#
# Copyright (c) 2023- AUCNET IBS
#
# ------------------------------------------------------------------------------

set -uo pipefail
set -e

readonly ME=${0##*/}
readonly REGION="us-west-2"

export AWS_PAGER=""

display_usage() {

    cat <<EOE

        インフラを削除するスクリプト

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

destroy_iam_roles() {

    local account=$(aws sts get-caller-identity --query Account --output text)

    aws iam detach-role-policy \
        --role-name sagemaker-yolov7-train-role \
        --policy-arn "arn:aws:iam::${account}:policy/sagemaker-yolov7-train-role-policy"

    aws iam delete-policy \
        --policy-arn "arn:aws:iam::${account}:policy/sagemaker-yolov7-train-role-policy"

    aws iam delete-role \
        --role-name sagemaker-yolov7-train-role

    aws iam detach-role-policy \
        --role-name sagemaker-yolov7-serve-role \
        --policy-arn "arn:aws:iam::${account}:policy/sagemaker-yolov7-serve-role-policy"

    aws iam delete-policy \
        --policy-arn "arn:aws:iam::${account}:policy/sagemaker-yolov7-serve-role-policy"

    aws iam delete-role \
        --role-name sagemaker-yolov7-serve-role

}

destroy_ecr_repository() {

    local repo=$1

    aws ecr batch-delete-image \
        --region $REGION \
        --repository-name "${repo}" \
        --image-ids "$(aws ecr list-images --region $REGION --repository-name "${repo}" --query 'imageIds[*]' --output json)" || true

    aws ecr delete-repository \
        --region $REGION \
        --repository-name "${repo}"

}

main() {

    local repos=("train serve serve-inferentia serve-cpu serve-graviton")

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

    destroy_iam_roles

    for repo in "${repos[@]}"
    do
        destroy_ecr_repository "sagemaker-yolov7-${repo}"
    done

}

whoopsie() {

    local message=$1

    echo "${message} Aborting..."
    exit 192

}

main "$@"

exit 0
