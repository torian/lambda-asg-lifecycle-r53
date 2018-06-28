# AWS AutoScalingGroup LifeCycleHook lambda

AWS Lambda function that runs through SNS notification when a lifecycle hook
is triggered from an ASG.

The lambda function will fetch availability zones from the auto scaling group
and will create a subdomain on `Route53` of the form `<asg-name>-<az>.<domain>`,
and will add or remove instances from it.

## Environment variables

| Variable      | Kind       | Default     | Notes |
|---------------|------------|-------------|-------|
| `AWS_REGION`  | Optional   | `us-east-2` | - |
| `AWS_PROFILE` | Optional   | empty       | Only needed when running from local |
| `LOGLEVEL`    | Optional   | `INFO`      | - |
| `DRY_RUN`     | Optional   | `True`      | Simulate what would be done |
| `R53_DOMAIN`  | check note | `empty`     | Specify which `Route53` zone to use by domain. Takes precedence over `R53_ZONE_ID` |
| `R53_ZONE_ID` | check note | `empty`     | Specify which `Route53` zone to use bu zone id |

**NOTE**: If `R53_DOMAIN` and `R53_ZONE_ID` are empty, the lambda function will raise an error

## Testing locally

One option is to use `python-lambda-local`, which can be installed through `pip`.

Export the variable `LOCAL=False`, and the related slack vars. Then, run:

```
$> python-lambda-local \
  -f lambda_handler \
  -l asg_event \
  -t 5 \
  aws_lambda.py tests/events/sns-lifecycle-launch.json
```

## Deploying

Make sure to have a lambda function created wit the name of this repo, and that
you export the following variables:

  * `AWS_REGION`
  * `AWS_PROFILE`

```
$> ./build.sh

```

