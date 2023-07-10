import constants
import message_constants




def fetch_vehicle_details_by_phone_number(conn, phone_number: str):
    """
    This function fetches the registration number and chassis number of all the vehicles from the database which is already linked with user.
    :param:
        phone_number: Contains phone_number of the corresponding user
        
    :return: list of registration number and chassis number
    """
    with conn.cursor() as cur:
        get_vehicles = '''
                        Select registration_number, chassis_number from vehicles where id in 
                        (
                            SELECT vehicle_id FROM user_vehicles
                                WHERE 
                                    (
                                        user_id = (SELECT user_id FROM users WHERE phone = %s)                                          
                                    )
                                    AND
                                        vehicle_state NOT IN ('DEAD', 'SCRAPPED', 'DUMB')
                        )
                    '''
        cur.execute(get_vehicles, (phone_number, ))
        res = cur.fetchall()
        return res
def fetch_vehicles_details(conn, vehicle_linking_details):
    """
    This function fetches the registration number and chassis number of a vehicle from the database
    :param:
        vehicle_linking_details: Contains registration_number,phone_number,emch_number and chassis_number provided by user
        
    :return: registration number and chassis number
    """
    registration_number = vehicle_linking_details.get(constants.REGISTRATION_NUMBER_KEY, None) 
    emch_number = vehicle_linking_details.get(constants.EMCH_NUMBER_KEY, None) 
    chassis_number = vehicle_linking_details.get(constants.CHASSIS_NUMBER_KEY, None) 

    if emch_number != None:
        emch_number = emch_number[-3:]
    
    with conn.cursor() as cur:
        get_details = '''
                                SELECT registration_number,chassis_number FROM vehicles
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
        cur.execute(get_details, (registration_number, emch_number, chassis_number))
        res = cur.fetchall()
        if len(res) == 1:
            return {
                    "data": res
                   }
        if len(res) == 0:
            return {
                    "data":[],
                    "error":"error"
                   }
        if len(res) > 1:
            return {
                    "data": res,
                    "error": "error"
                   }

def handle_get_vehicle_request(conn, vehicle_data: list, response: dict):
    status_code = constants.STATUS_CODE_500
    correct_fetched_vehicles: list = []
    multiple_fetched_vehicles: list = []  
    empty_fetched_vehicles: list = []

    for i in range(len(vehicle_data)):

        vehicle_linking_details = {constants.REGISTRATION_NUMBER_KEY: vehicle_data[i][0],  constants.CHASSIS_NUMBER_KEY: vehicle_data[i][1], constants.EMCH_NUMBER_KEY: vehicle_data[i][2]}
        msg = fetch_vehicles_details(conn, vehicle_linking_details)

        if(vehicle_data[i][2] != ''):
            non_empty_key = vehicle_data[i][2]
        elif(vehicle_data[i][0]!=''):
            non_empty_key = vehicle_data[i][0]
        elif(vehicle_data[i][1]!=''):
            non_empty_key = vehicle_data[i][1]
        
        if len(msg['data']) == 1:
            correct_fetched_vehicles.append((non_empty_key, msg["data"][0][0], msg["data"][0][1]))

        elif len(msg['data']) > 1:
            for j in range(len(msg['data'])):
                multiple_fetched_vehicles.append((non_empty_key, msg["data"][j][0], msg["data"][j][1]))

        elif len(msg['data']) == 0:                        
            empty_fetched_vehicles.append((non_empty_key, message_constants.NO_REGISTRATION_MESSAGE, message_constants.NO_CHASSIS_MESSAGE))
    
    message: str = ""
    scenario: int = 1
    
    if len(correct_fetched_vehicles) == len(vehicle_data):
        message = message_constants.SCENARIO_1_VEHICLE_MESSAGE
        scenario = 1
        status_code = constants.STATUS_CODE_200
    elif len(empty_fetched_vehicles) == len(vehicle_data):
        message = message_constants.SCENARIO_0_VEHICLE_MESSAGE
        scenario = 0
        status_code = constants.STATUS_CODE_200
    elif len(multiple_fetched_vehicles) == len(vehicle_data):
        message = message_constants.SCENARIO_3_VEHICLE_MESSAGE
        scenario = 3
        status_code = constants.STATUS_CODE_200
    elif (len(multiple_fetched_vehicles) > 0 or  len(empty_fetched_vehicles) > 0 ) and len(correct_fetched_vehicles) > 0:  
        message: str = message_constants.SCENARIO_2_VEHICLE_MESSAGE
        scenario = 2
        status_code = constants.STATUS_CODE_200
    
    response["data"] = {
                        "correct_fetched_vehicles": correct_fetched_vehicles,
                        "multiple_fetched_vehicles": multiple_fetched_vehicles,
                        "empty_fetched_vehicles": empty_fetched_vehicles  
                        }
    
    response["message"] = message
    response["scenario"] = scenario

    return response, status_code