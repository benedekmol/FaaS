import json
import boto3
import os

INVOCATION_TYPE = os.environ.get('INVOCATION_TYPE',None)
RECIEVER_FUNCTION = os.environ.get('RECEIVER_FUNCTION',"cloud-native-invoker")
REGION = os.environ.get('REGION',"eu-central-1")
results = ""

lambda_client = boto3.client('lambda', REGION)

def lambda_handler(event, context):
    if INVOCATION_TYPE:
        for i in range(100):
            name = f"TestResult{i}"
            db_name = {"name": name}
            response = lambda_client.invoke(FunctionName=RECIEVER_FUNCTION,
                                            InvocationType=INVOCATION_TYPE,
                                            Payload=json.dumps(db_name))

            

    return {
        'statusCode': 200,
        'body': json.dumps('')
    }

