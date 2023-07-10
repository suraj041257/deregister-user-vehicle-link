'''
    This lambda will be used to handle all the operations related to
    registering any user on Shepherd and link any user to vehicle on Shepherd.
'''
import os
import json
import psycopg2
from register_user import register_user_on_shepherd
from link_user_vehicle import handle_link_vehicle_request
from fetch_vehicles_details import handle_get_vehicle_request
from fetch_user_details import handle_get_user_request
from authorize import auth
import constants
import jwt
from monitor import monitor_api_calls

HEADERS = {
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,PATCH",
    "Content-Type": "application/json",
}

database_config = {
    "user": os.environ["user"],
    "password": os.environ["password"],
    "host": os.environ["host"],
    "port": os.environ["port"],
    "dbname": os.environ["database"],
}


def lambda_handler(event, context):
    
    response: dict = {}
    status_code: int = constants.STATUS_CODE_500
    
    if "httpMethod" in event:
        method = event["httpMethod"]
    else:
        method = event["context"]["http-method"]
    
    resource = event["resource"]
    
    
    if "resource" in event:
        token = event["multiValueHeaders"].get(constants.TOKEN_KEY, None)[0]
        res = auth(token)
    else:
        token = event["params"]["header"].get(constants.TOKEN_KEY, None)
        res = auth(token)

    if res['statusCode'] != constants.STATUS_CODE_200:
        return res
    
    token_payload = jwt.decode(token, constants.JWT_SECRET)
    updated_by = token_payload["user_id"]
    
    monitor_api_calls((resource + '_' + method).lower(), updated_by.lower())
    
    with psycopg2.connect(**database_config) as conn:
        
        if method == "PUT":
            user_details_body = json.loads(event.get("body", {}))
            user_details = user_details_body.get("params", {})
            response, status_code = register_user_on_shepherd(conn, user_details)
            
        elif method == "GET":
            user_linking_details = event["queryStringParameters"]
            get_user_details: int  = int(user_linking_details.get("get_user_details", 0))
            
            if get_user_details == 1:
                response, status_code = handle_get_user_request(conn, user_linking_details, response)
       
        elif method == 'POST':
            
            body = json.loads(event.get("body", {}))

            if len(body) == 0:
                body = event["queryStringParameters"]
            
            params = body.get("params", {})

            vehicle_data: list = params.get("vehicleData", [])
            get_vehicle_details: int = params.get("get_vehicle_details", 0)
            link_vehicles: int = params.get("link_vehicles", 0)
            phone_number: str = params.get("phone_number", '')
            
            if get_vehicle_details == 1:
                response, status_code = handle_get_vehicle_request(conn, vehicle_data, response)

            elif link_vehicles == 1:
                response, status_code = handle_link_vehicle_request(conn, vehicle_data, phone_number, response)
                
    return {
            "statusCode": status_code, 
            "headers": HEADERS, 
            "body": json.dumps(response)
          }
 
