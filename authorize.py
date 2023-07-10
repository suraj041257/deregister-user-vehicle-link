
import json
from boto3 import client as boto3_client
import constants

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,PATCH',
    'Content-Type': 'application/json'
}

def auth(token: str):
    """
    It takes a token as an argument, and returns the result of invoking the authorizer lambda function
    with the token and the resource identifier
    
    :param token: The token that was passed in the request
    :type token: str
    :return: The response from the authorizer lambda function.
    """
    
    if token == None:
        res = {
            'statusCode': 401,
            'headers': headers,
            'body': json.dumps('Not Authorized')
        }
        return res
    else:

        lambda_client = boto3_client('lambda')

        payload_data = {
            'token': token,
            'resource_identifier': constants.SHEPHERD_RESOURCE_AUTHORIZER_IDENTIFIER
        }
        
        res = lambda_client.invoke(
                    FunctionName = constants.AUTHORIZER_ARN,
                    Payload = json.dumps(payload_data)
                )
        return json.loads(res['Payload'].read())