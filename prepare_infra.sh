#!/bin/bash
# -- prepare_infra.sh ----------------------------------------------------------
#
# インフラを準備するスクリプト
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

        インフラを準備するスクリプト

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

create_iam_roles() {

    account=$(aws sts get-caller-identity --query Account --output text)

    aws iam create-policy \
        --policy-name sagemaker-yolov7-train-role-policy \
        --policy-document file://policy/sagemaker-yolov7-train-role-policy.json

    aws iam create-role \
        --role-name sagemaker-yolov7-train-role \
        --assume-role-policy-document file://policy/sagemaker-assume-role-policy.json

    aws iam attach-role-policy \
        --role-name sagemaker-yolov7-train-role \
        --policy-arn "arn:aws:iam::${account}:policy/sagemaker-yolov7-train-role-policy"

    aws iam create-policy \
        --policy-name sagemaker-yolov7-serve-role-policy \
        --policy-document file://policy/sagemaker-yolov7-serve-role-policy.json

    aws iam create-role \
        --role-name sagemaker-yolov7-serve-role \
        --assume-role-policy-document file://policy/sagemaker-assume-role-policy.json

    aws iam attach-role-policy \
        --role-name sagemaker-yolov7-serve-role \
        --policy-arn "arn:aws:iam::${account}:policy/sagemaker-yolov7-serve-role-policy"

}

create_ecr_repository() {

    aws ecr create-repository \
        --region $REGION \
        --repository-name "sagemaker-yolov7-train" \
        --image-scanning-configuration scanOnPush=true

    aws ecr set-repository-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-train" \
        --policy-text file://policy/ecr-repository-policy.json

    aws ecr put-lifecycle-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-train" \
        --lifecycle-policy-text file://policy/ecr-lifecycle-policy.json

    aws ecr create-repository \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve" \
        --image-scanning-configuration scanOnPush=true

    aws ecr set-repository-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve" \
        --policy-text file://policy/ecr-repository-policy.json

    aws ecr put-lifecycle-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve" \
        --lifecycle-policy-text file://policy/ecr-lifecycle-policy.json

    aws ecr create-repository \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-inferentia" \
        --image-scanning-configuration scanOnPush=true

    aws ecr set-repository-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-inferentia" \
        --policy-text file://policy/ecr-repository-policy.json

    aws ecr put-lifecycle-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-inferentia" \
        --lifecycle-policy-text file://policy/ecr-lifecycle-policy.json

    aws ecr create-repository \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-cpu" \
        --image-scanning-configuration scanOnPush=true

    aws ecr set-repository-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-cpu" \
        --policy-text file://policy/ecr-repository-policy.json

    aws ecr put-lifecycle-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-cpu" \
        --lifecycle-policy-text file://policy/ecr-lifecycle-policy.json

    aws ecr create-repository \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-graviton" \
        --image-scanning-configuration scanOnPush=true

    aws ecr set-repository-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-graviton" \
        --policy-text file://policy/ecr-repository-policy.json

    aws ecr put-lifecycle-policy \
        --region $REGION \
        --repository-name "sagemaker-yolov7-serve-graviton" \
        --lifecycle-policy-text file://policy/ecr-lifecycle-policy.json

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

    create_iam_roles

    create_ecr_repository

}

whoopsie() {

    local message=$1

    echo "${message} Aborting..."
    exit 192

}

main "$@"

exit 0
