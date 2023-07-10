import constants, message_constants
from fetch_vehicles_details import fetch_vehicle_details_by_phone_number

def modify_null_values(response: list) -> list:
    """Converts Null value to Not Found string

    Args:
        res (list): data of users (2D list)
    
    Return:
        res (list): data of users (2D list)
    """
    users: list = [[] for i in range(len(response))]
    for res in range(len(response)):
        for details in range(len(response[res])):
            users[res].append(response[res][details])
            if response[res][details] is None: 
                users[res][details] = message_constants.NOT_FOUND_MESSAGE
    return users


def handle_get_user_request(conn, user_linking_details: dict, response: dict) -> tuple:
    
    response = fetch_user_details(conn, user_linking_details)
    response["vehicles_details_response"] = []
    if response['scenario'] == 0:
        status_code = constants.STATUS_CODE_200
    elif response['scenario'] == 1:
        status_code = constants.STATUS_CODE_200
        phone_number: str = response["response"][0][2]
        response["vehicles_details_response"] = fetch_vehicle_details_by_phone_number(conn, phone_number)

    elif response['scenario'] == 2:
        status_code = constants.STATUS_CODE_200

    return response, status_code


def fetch_user_details(conn, user_linking_details: dict):
    """
    This function fetches the Username, Phone, email and Full Name of a user from the database
    :param:
        user_linking_details: Contains phone number provided by user
        
    :return: Username, Phone, email and Full Name of a user
    """
    
    phone_number = user_linking_details.get(constants.PHONE_KEY, '') 
    email_id = user_linking_details.get(constants.EMAIL_KEY, '')
    username = user_linking_details.get(constants.USERNAME_KEY, '')
    user_type = user_linking_details.get(constants.USER_TYPE_KEY, '')

    if user_type == constants.OWNER:
        with conn.cursor() as cur:
            get_user_details = '''
                                select username, email, phone, full_name from users where (phone is not null and phone!='N/A' and phone!='' and phone=%s) or (email is not null and email!='N/A' and email!='' and email=%s) or (username is not null and username!='N/A' and username!='' and username=%s);
                                ''' 
            cur.execute(get_user_details, (phone_number, email_id, username))

            res = cur.fetchall()

            res = modify_null_values(res)

            if(len(res) == 1):
                return {
                        "message": "Owner Found",
                        "response": res,
                        "scenario": 1
                    }
            
            if len(res) > 1:
                return {
                        "message": "Multiple Owners found. Please re-check your Entries or Contact Software Team ",
                        "response": res,
                        "scenario": 2
                    }
            if len(res) == 0:
                return {
                        "message": "No Owner Found in Database. Please re-check your Entries.",
                        "response": res,
                        "scenario": 0
                    }
        
    if user_type == constants.FINANCER:
        with conn.cursor() as cur:
            get_user_details = '''
                                select username,email,phone,organization from namor_users where (phone is not null and phone!='N/A' and phone!='' and phone=%s) or (email is not null and email!='N/A' and email!='' and email=%s) or (username is not null and username!='N/A' and username!='' and username=%s);
                                '''
            cur.execute(get_user_details, (phone_number, email_id, username))

            res = cur.fetchall()
            if(len(res) == 1):
                return {
                        "message": "FINANCER Found",
                        "response": res,
                        "scenario": 1
                    }
        
            if(len(res) > 1):
                return {
                        "message": "Multiple Financers found. Please re-check your Entries or Contact Software Team ",
                        "response": res,
                        "scenario": 2
                    }
            if(len(res) == 0):
                return {
                        "message": "No Financers found. Please re-check your Entries or Contact Software Team ",
                        "response": res,
                        "scenario": 0
                    }

    return {
            "message": "No User Found in Database. Please re-check your Entries.",
            "response": None,
            "scenario": 0
            }
 
