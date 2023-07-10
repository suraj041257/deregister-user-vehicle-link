import constants
import message_constants
def user_vehicle_relation_exist(conn, phone_number, registration_number):
    """
    It checks if a user has a vehicle with a given registration number
    :param conn: the connection to the database
    :param phone_number: The phone number of the user who is trying to add the vehicle
    :param registration_number: The registration number of the vehicle
    :return: A boolean value.
    """

    with conn.cursor() as cur:
        relation_checking_query = '''
                                    SELECT * FROM user_vehicles
                                    WHERE user_id = (SELECT user_id FROM users WHERE phone = %s)
                                    AND vehicle_id = (SELECT id FROM vehicles WHERE registration_number = %s and vehicle_state NOT IN ('DEAD', 'SCRAPPED', 'DUMB'))
                                  '''
        cur.execute(relation_checking_query, (phone_number, registration_number))
        res = cur.fetchone()
        if res == None:
            return False
        return True

def fetch_vehicle_id_temp_reg_no(conn, emch_number, registration_number, chassis_number):
    """
    It returns the vehicle_id and temporary registration number or real registration number of vehicle which have the given registration number, chassis number or a
    temporary registration number (following the initial TC characters and last 3 digit EMCH number
    conventions)
    
    :param conn: Connection object to the database
    :param emch_number: EMCH number of the vehicle
    :param registration_number: The registration number of the vehicle
    :param chassis_number: The chassis number of the vehicle
    :return: The number of vehicles that meet the conditions.
    """

    with conn.cursor() as cur:
        # Req Vehicle contains those vehicles which meet atleast one of these conditions i.e. 
        # registration_number = given registration number,
        # chassis_number = given chassis_number
        # registration number = temp registration number (Following intial TC characters and last 3 digit EMCH number conventions)
        req_vehicle = '''
                        SELECT id,registration_number,chassis_number FROM vehicles
                        WHERE registration_number = %s
                            or chassis_number = %s 
                            or (SUBSTRING(registration_number, 1, 2) = 'TC'
                                AND SUBSTRING(registration_number, 8, 10) = %s
                                )
                            or (SUBSTRING(chassis_number, -3, LENGTH(chassis_number))) = %s
                      '''
        cur.execute(req_vehicle, (registration_number, chassis_number, emch_number, emch_number))
        res = cur.fetchall()
        return res



def make_relation_user_vehicle(conn, emch_number, registration_number, phone_number, chassis_number):
    """
    It takes in a connection object, a registration number and a phone number, and then it checks if the
    relation between the user and the vehicle already exists. If it does, it returns an error message.
    If it doesn't, it creates the relation between the user and the vehicle
    
    :param conn: The connection to the database
    :param registration_number: The registration number of the vehicle
    :param phone_number: The phone_number of the user who is registering the vehicle
    :return: A dictionary with a message key and a value of 'User Vehicle Successfully Linked.'
    """
    
    with conn.cursor() as cur:
    
        if(user_vehicle_relation_exist(conn, phone_number, registration_number)):
            print('User Vehicle Relation already exists.', registration_number, chassis_number, phone_number)
            return {
                    'error': 'Relation between given Phone Number and vehicle already exists.',
                    'data': [registration_number, chassis_number],
                    'scenario': 2
                   }
        # print("registration:", registration_number, phone_number) 
        
        is_user_financer_query: str = '''SELECT id FROM namor_users WHERE namor_users.phone = %s'''
        cur.execute(is_user_financer_query, (phone_number, ))
        res = cur.fetchone()
        # print("Is_FINANCER:", res)
        
                    
        
        try:
            if res:
                link_user = '''                        
                            INSERT INTO user_vehicles(vehicle_id, user_id, namor_user_id)
                            (SELECT subquery1.id, subquery2.user_id, %s
                            FROM (SELECT id FROM vehicles WHERE vehicles.registration_number = %s AND vehicle_state NOT IN ('DEAD', 'SCRAPPED', 'DUMB')) AS subquery1,
                                (SELECT user_id FROM users WHERE users.phone = %s) AS subquery2)
                            '''
                
                cur.execute(link_user, (res[0], registration_number, phone_number, ))
                conn.commit()
                # print("Namor USERS VEHICLES LINKED")
            else:
                link_user = '''                        
                            INSERT INTO user_vehicles(vehicle_id, user_id)
                            (SELECT subquery1.id, subquery2.user_id
                            FROM (SELECT id FROM vehicles WHERE vehicles.registration_number = %s AND vehicle_state NOT IN ('DEAD', 'SCRAPPED', 'DUMB')) AS subquery1,
                                (SELECT user_id FROM users WHERE users.phone = %s) AS subquery2)
                            '''
                
                cur.execute(link_user, (registration_number, phone_number, ))
                conn.commit()
                # print("USERS VEHICLES LINKED")
            
            return {'message': 'User Vehicle Successfully Linked.',
                    'data': [registration_number, chassis_number],
                    'scenario': 1
                    }
        except Exception as exc:
            print("Exception: make_relation_user_vehicle", exc)




def sanity_check(conn, emch_number, registration_number, chassis_number):
    """
    If there is only one vehicle with the given emch number, registration number and chassis number, and
    the registration number and chassis number match, then return True, else return False
    
    :param conn: the connection to the database
    :param emch_number: The number of the EMCH (the number on the sticker on the vehicle)
    :param registration_number: The registration number of the vehicle
    :param chassis_number: The chassis number of the vehicle
    :return: the number of rows in the table.
    """
    if count_emch_reg_chassis_no_vehicle(conn, emch_number, registration_number, chassis_number) == 1:
        return True
    return False

def is_phone_number_available(conn, phone_number):
    """
    This function takes in a connection object and a phone number and returns True if the phone number is
    available and False if it is not
    
    :param conn: the connection to the database
    :param phone_number: the phone_number to check
    :return: A boolean value.
    """

    try:
        with conn.cursor() as cur:
            phone_number_available = '''
                                    SELECT * FROM users
                                    WHERE phone = %s;
                                '''
            cur.execute(phone_number_available, (phone_number, ))
            res= cur.fetchone()
            if res == None:
                return False
            return True

    except Exception as exc:
        print("Exception: is_phone_number_available ", exc)
        



def reg_no_chassis_no_match(conn, registration_number, chassis_number):
    """
    It checks if the registration number and chassis number are unique.
    
    :param conn: the connection to the database
    :param registration_number: The registration number of the vehicle
    :param chassis_number: The chassis number of the vehicle
    :return: A boolean value.
    """

    with conn.cursor() as cur:
        req_vehicle = '''
                        SELECT registration_number, chassis_number FROM vehicles
                        WHERE registration_number = %s
                            or chassis_number = %s;
                      '''
        cur.execute(req_vehicle, (registration_number, chassis_number))
        res = cur.fetchall()
        if len(res) > 1:
            return False
        elif len(res) == 0:
            return True
        
        if(res[0][0]!=registration_number and res[0][1] != chassis_number): # When in DB, both RN and CN are temporary matching with EMCH (as count_emch_reg_chassis_no_vehicle function is already executed before this. )
            return True 
        if res[0][0] != registration_number or res[0][1] != chassis_number:
            return False
        return True

def count_emch_reg_chassis_no_vehicle(conn, emch_number, registration_number, chassis_number):
    """
    It returns the number of vehicles which have the given registration number, chassis number or a
    temporary registration number (following the initial TC characters and last 3 digit EMCH number
    conventions)
    
    :param conn: Connection object to the database
    :param emch_number: EMCH number of the vehicle
    :param registration_number: The registration number of the vehicle
    :param chassis_number: The chassis number of the vehicle
    :return: The number of vehicles that meet the conditions.
    """
    with conn.cursor() as cur:
        # Req Vehicle contains those vehicles which meet atleast one of these conditions i.e. 
        # registration_number = given registration number,
        # chassis_number = given chassis_number
        # registration number = temp registration number (Following intial TC characters and last 3 digit EMCH number conventions)
        req_vehicle = '''
                        SELECT * FROM vehicles
                        WHERE 
                                        (
                                            registration_number = %s
                                            or 
                                            (
                                                SUBSTRING(registration_number, 1, 2) = 'TC'
                                                    AND 
                                                SUBSTRING(registration_number, 8, 10) = %s
                                            ) 
                                            or 
                                            (
                                                chassis_number != 'N/A'
                                                AND
                                                chassis_number != ''
                                                AND 
                                                chassis_number = %s
                                            )
                                        )
                                        AND 
                                            vehicle_state NOT IN ('DEAD', 'SCRAPPED', 'DUMB');
                      '''
        cur.execute(req_vehicle, (registration_number, emch_number, chassis_number))
        res = cur.fetchall()

        return len(res)

def link_user_to_vehicle(conn, vehicle_linking_details):
    
    registration_number = vehicle_linking_details.get(constants.REGISTRATION_NUMBER_KEY, None)
    phone_number = vehicle_linking_details.get(constants.PHONE_KEY, None)
    emch_number = vehicle_linking_details.get(constants.EMCH_NUMBER_KEY, None)
    chassis_number = vehicle_linking_details.get(constants.CHASSIS_NUMBER_KEY, None)

    if sanity_check(conn, emch_number, registration_number, chassis_number):
        return make_relation_user_vehicle(conn,emch_number, registration_number, phone_number, chassis_number)
    else:
        return {
                'error' : 'Something Went Wrong. Contact Software Team.',
                'data': [registration_number, chassis_number],
                'scenario': 0
                }

def handle_link_vehicle_request(conn, vehicle_data: list, phone_number: str, response: dict):
    """Provides Response if Vehicle got linked or not

    Args:
        conn (_type_): DB Connection
        vehicle_data (list): 2D list of vehicle Details
        phone_number (str): phone number
        response (dict): response

    Returns:
        tuple: response, status_code
    """

    status_code: int = constants.STATUS_CODE_500
    response["scenario"] = 2
    response["data"] = {
        "linked": [],
        "not_linked": [],
    }
    
    message: str = message_constants.ERROR
    
    for i in range(len(vehicle_data)):   

        vehicle_linking_details: dict = {
            constants.REGISTRATION_NUMBER_KEY: vehicle_data[i][0],
            constants.CHASSIS_NUMBER_KEY: vehicle_data[i][1],
            constants.EMCH_NUMBER_KEY: vehicle_data[i][2],
            constants.PHONE_KEY: phone_number
            }
        msg = link_user_to_vehicle(conn, vehicle_linking_details)
        
        if msg['scenario'] != 1 :
            response["data"]["not_linked"].append([msg["data"][0], msg["data"][1], msg["error"]])
            
        else:
            response["data"]["linked"].append([msg["data"][0], msg["data"][1], message_constants.LINKED_MESSAGE])

    
    if len(response["data"]["linked"]) == len(vehicle_data):
        status_code = constants.STATUS_CODE_200
        message = message_constants.VEHICLE_LINKED_SUCCESSFULLY
        response["scenario"] = 1
    elif len(response["data"]["not_linked"]) == len(vehicle_data):
        status_code = constants.STATUS_CODE_200
        message = message_constants.NO_VEHICLE_LINKED
        response["scenario"] = 0
    elif len(response["data"]["linked"]) +  len(response["data"]["not_linked"]) == len(vehicle_data):
        status_code = constants.STATUS_CODE_200
        message = message_constants.PARTIAL_WRONG_MESSAGE
        response["scenario"] = 2
    response['message'] = message
    
    return response, status_code