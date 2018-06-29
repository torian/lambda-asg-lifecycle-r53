
PYTHON_VERSION=${PYTHON_VERSION:-2.7}
PROJECT_NAME=asg-lifecycle-hook
BUILD_PREFIX=./build

AWS_REGION=${AWS_REGION:-us-east-1}
AWS_PROFILE=${AWS_PROFILE:-default}

AWS_S3_BUCKET=${AWS_S3_BUCKET:-''}
AWS_S3_PREFIX=${AWS_S3_PREFIX:-''}

[ ! -d ${BUILD_PREFIX} ] && mkdir ${BUILD_PREFIX}

# Use docker to install packages into a target directory
docker run \
  --rm -ti \
  -v ${PWD}:/opt \
  -w /opt \
  python:${PYTHON_VERSION}-alpine \
  /bin/sh -c \
    "pip install -r requirements-${PYTHON_VERSION}.txt -t ${BUILD_PREFIX}"

# Add relevant code to build directory
cp -r \
  ./aws_lambda.py \
  ./asg_event \
  ${BUILD_PREFIX}

rm -f ${PROJECT_NAME}.zip
find ./ -type f -name "*.pyc" -exec rm -f \{} \;
find ./ -type d -name "__pycache__" -exec rm -rf \{} \;

# Build zip package to be deployed to AWS
pushd ${BUILD_PREFIX} && zip -r ../${PROJECT_NAME}.zip ./ -x "*.pyc" "*.swa" "*.swp" && popd

if [ -z "${AWS_S3_BUCKET}" ] || [ -z "${AWS_S3_PREFIX}" ]; then
  echo "S3 Bucket or S3 prefix not defined, skipping artifact upload"
  exit 1
fi

[ -n "${AWS_PROFILE}" ] && PROFILE="--profile ${AWS_PROFILE}"

aws s3 \
  ${PROFILE} \
  --region  ${AWS_REGION} \
  cp ${PROJECT_NAME}.zip s3://${AWS_S3_BUCKET}/${AWS_S3_PREFIX}/${PROJECT_NAME}/
 
aws lambda \
  ${PROFILE} \
  --region  ${AWS_REGION} \
  update-function-code \
    --function-name ${PROJECT_NAME} \
    --s3-bucket ${AWS_S3_BUCKET} \
    --s3-key ${AWS_S3_PREFIX}/${PROJECT_NAME}/${PROJECT_NAME}.zip \
    --publish
