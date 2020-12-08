import boto3
import time
import json
import os
import time


from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# How much data to write in DynamoDB.
DYAMODB_WRITE_SIZE = int(os.environ.get('PAYLOAD_SIZE', 1))
# How to invoke the RECEIVER_FUNCTION: synchronous call "RequestResponse", asynchronous "Event".
INVOCATION_TYPE = os.environ.get('INVOCATION_TYPE', None)
# How big payload to add when calling the RECEIVER_FUNCTION.
INVOCATION_PAYLOAD_SIZE = int(os.environ.get('PAYLOAD_SIZE', 0))
# Which other Lambda function to call.
RECEIVER_FUNCTION = os.environ.get('RECEIVER_FUNCTION', 
                                   "cloud-native-temalabor-tester-receiver")
# In what region the RECEIVER_FUNCTION is.
REGION = os.environ.get('REGION', "eu-central-1")

# Creates a lambda client object that will be used when calling the RECEIVER_FUNCTION.
lambda_client = boto3.client('lambda', REGION)

# Creates a dynamodb object that will be used when reading/writing Amazon DynamoDB.
dynamodb = boto3.client('dynamodb', REGION)
# Name of the DynamoDB table.
dynamodb_table = "cloudNativeTemalaborTesterDb"

# A function for doing some test computation.
def test_compute_function():
    # For now it waits for 0.1 sec.
    time.sleep(0.1)


def lambda_handler(event, context):
    
    # Prepare a payload with the specified number of `a' characters and a 
    # timestamp that carries the time of invocation.
    function_invocation_payload = {"p":  "a" * INVOCATION_PAYLOAD_SIZE,
                                   "ts": time.time()}
    
    # Call the RECEIVER_FUNCTION using INVOCATION_TYPE.
    if INVOCATION_TYPE:
        response = lambda_client.invoke(FunctionName=RECEIVER_FUNCTION,
                                        InvocationType=INVOCATION_TYPE,
                                        Payload=json.dumps(
                                            function_invocation_payload))
        # Record the time spent while waiting for the function invocation to return,
        # i.e., invocation blocking delay.
        function_invocation_blocking_delay = (time.time() - function_invocation_payload["ts"]) * 1000
    else:
        function_invocation_blocking_delay = 0
    
    # Measure the time of executing the compute function.
    compute_function_invocation_start = time.time()
    test_compute_function()
    compute_function_execution_delay = (time.time() - compute_function_invocation_start) * 1000
    
    # A key for writing and reading DynamoDB.
    dynamodb_test_key = "testWrite"
    
    # Measure the time of writing to DynamoDB.
    dynamodb_write_start = time.time()
    # Write DYAMODB_WRITE_SIZE number of `a' characters to dynamo_table with the key dynamodb_test_key.
    #write_response = dynamo_table.put_item(Item={ 'key': "id", 'payload': "a" * DYAMODB_WRITE_SIZE})
    dynamodb.put_item(TableName=dynamodb_table, Item={
        'id': {'S': dynamodb_test_key}, # `S' means string.
        'payload': {'S': "a" * DYAMODB_WRITE_SIZE}})
    dynamodb_write_delay = (time.time() - dynamodb_write_start) * 1000
    
    # Measure the time of reading from DynamoDB.
    dynamodb_read_start = time.time()
    # Query key dynamodb_test_key from dynamo_table.
    response = dynamodb.get_item(
            TableName = dynamodb_table,
            Key = {
                'id' : { 'S': 'testWrite'}
            }
        )
    print(response['Item'])
    # read_response = dynamo_table.query(KeyConditionExpression=Key('key').eq(dynamodb_test_key))
    dynamodb_read_delay = (time.time() - dynamodb_read_start) * 1000
    
    # Collect results.
    results = {"function invocation blocking delay [ms]": function_invocation_blocking_delay,
               "compute function execution blocking [ms]": compute_function_execution_delay,
               "dynamodb write delay [ms]": dynamodb_write_delay, 
               "dynamodb read delay [ms]": dynamodb_read_delay}
    
    # Print results to Amazon CloudWatch.
    print(results)
    
    name = event["name"]
    #name = os.environ.get('')
    
    # Write test resutls to DynamoDB.
    dynamodb.put_item(TableName=dynamodb_table, Item={
        'id': {'S': name},
        'functionBlocking': {'N': str(function_invocation_blocking_delay)}, # `N' means number
        'computeFunctionExecution': {'N': str(compute_function_execution_delay)},
        'dynamodbWrite': {'N': str(dynamodb_write_delay)},
        'dynamodbRead': {'N': str(dynamodb_read_delay)},
        
    })
    
    # Return results. These can be handled in, e.g., an SDK call.
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
