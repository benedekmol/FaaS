import json
import time

def lambda_handler(event, context):
    
    # Measure function invocation delay: subtract time of invocation from the 
    # current time, i.e., the time when the invocation arrived to the receiver
    # 
    lambda_function_invocation_delay = (time.time() - event["ts"]) * 1000
    
    # Log to CloudWatch.
    print(f"Lambda function invocation delay [ms]: {lambda_function_invocation_delay}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('')
    }
