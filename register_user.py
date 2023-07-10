import constants
import message_constants

#TODO: Notify end user for successful creation. Call RDS only one time.
def is_phone_registered(conn, phone, user_type):
    """
    It checks if the phone number is already registered in the database
    
    :param conn: the connection to the database
    :param phone: The phone number of the user
    :return: A boolean value.
    """
    
    with conn.cursor() as cur:
        if(user_type == constants.FINANCER):
            phone_available = '''
                                SELECT * from namor_users where phone = %s;
                            '''
            cur.execute(phone_available, (phone, ))
            res = cur.fetchall()
            if res == []:
                phone_available = '''
                            SELECT * from users where phone = %s;
                          '''
                cur.execute(phone_available, (phone, ))
                res = cur.fetchall()
                if len(res) == 0:
                    return False
                else:
                    return True
            else:
                return True
        
        phone_available = '''
                            SELECT * from users where phone = %s;
                          '''
        cur.execute(phone_available, (phone, ))
        res = cur.fetchall()
        if len(res) == 0:
            return False
        return True


def is_email_registered(conn, email, user_type):
    """
    This function takes in a connection object and an email address and returns True if the email
    address is already registered in the database and False if it is not.
    
    :param conn: the connection to the database
    :param email: the email address of the user
    :return: A boolean value.
    """

    if(email == None or email == ''):
        return False
                  
    with conn.cursor() as cur:
        if(user_type == constants.FINANCER):
            email_available = '''
                                SELECT * from namor_users where email = %s;
                            '''
            cur.execute(email_available, (email, ))
            res = cur.fetchall()
            if len(res) == 0:
                email_available = '''
                            SELECT * from users where email = %s;
                          '''
                cur.execute(email_available, (email, ))
                res = cur.fetchall()
                if len(res) == 0:
                    return False
                else:
                    return True
            else:
                return True

        email_available = '''
                            SELECT * from users where email = %s;
                          '''
        cur.execute(email_available, (email, ))
        res = cur.fetchall()
        if len(res) == 0:
            return False
        return True
        
def is_username_registered(conn, username, user_type):
    """
    This function takes in a connection object and a username and returns True if the username is
    already registered in the database and False otherwise
    
    :param conn: the connection to the database
    :param username: the username of the user
    :return: A boolean value.
    """
                 
    with conn.cursor() as cur:
        if(user_type == constants.FINANCER):
            username_available = '''
                                SELECT * from namor_users where username = %s;
                            '''
            cur.execute(username_available, (username, ))
            res = cur.fetchall()
            if len(res) == 0:
                username_available = '''
                            SELECT * from users where username = %s;
                          '''
                cur.execute(username_available, (username, ))
                res = cur.fetchall()
                if len(res) == 0:
                    return False
                else:
                    return True
            else:
                return True

        username_available = '''
                            SELECT * from users where username = %s;
                          '''
        cur.execute(username_available, (username, ))
        res = cur.fetchall()
        if len(res) == 0:
            return False
        return True


def register_user_on_shepherd(conn, user_details: dict):
    """
    It takes a connection to the database and a dictionary of user details and registers the user on the
    database.
    
    :param conn: Connection to the database
    :param user_details: A dictionary containing the following keys:
    :type user_details: Dict
    :return: A dictionary with a key of 'message' and a value of 'User Successfully Registered.'
    """
    # print("Userdetails", user_details)
    phone = user_details.get(constants.PHONE_KEY, None)
    email = user_details.get(constants.EMAIL_KEY, None)
    name = user_details.get(constants.NAME_KEY, None)
    username = user_details.get(constants.USERNAME_KEY, None)
    password = user_details.get(constants.PASSWORD_KEY, None)
    user_type = user_details.get(constants.USER_TYPE_KEY, None)
    
    if email == None or email == '':
        email = None
    
    if phone == None:
       return {'error' : 'Please Enter Phone Number.'}, constants.STATUS_CODE_200
    
    if name == None:
        return {'error': 'Please Enter Name.'}, constants.STATUS_CODE_200

    if username == None:
        return {'error': 'Please Enter Username.'}, constants.STATUS_CODE_200
    
    if password == None:
        return {'error': 'Please Enter Password.'}, constants.STATUS_CODE_200

    if is_username_registered(conn, username, user_type):
        return {'error': 'This username is already registered. Please Select a different username.'}, constants.STATUS_CODE_200

    if is_phone_registered(conn, phone, user_type):
        return {'error': 'Phone is already registered.'}, constants.STATUS_CODE_200
    
    if is_email_registered(conn, email, user_type):
        return {'error': 'Email is already registered.'}, constants.STATUS_CODE_200


    try:
        with conn.cursor() as cur:
                                
            if(user_type == constants.FINANCER):
                
                organization_name: str = name

                if email == None or email == '':
                    insert_new_user = '''
                                INSERT INTO namor_users (username, password, organization, phone, is_active, is_verified)
                                VALUES(%s, crypt(%s, gen_salt('bf') ), %s, %s, 't', 't');
                                '''
                    cur.execute(insert_new_user, (username, password, organization_name, phone))
                
                else:
                    insert_new_user = '''
                                INSERT INTO namor_users (username, email, password, organization , phone, is_active, is_verified)
                                VALUES(%s, %s, crypt(%s, gen_salt('bf') ), %s, %s, 't', 't');
                                '''
                    cur.execute(insert_new_user, (username, email, password, organization_name, phone))
                
                

            customer_name: str = name

            if email == None or email == '':
                insert_new_user = '''
                            INSERT INTO users (username, password, full_name, phone)
                            VALUES(%s, crypt(%s, gen_salt('bf') ), %s, %s);
                            '''
                cur.execute(insert_new_user, (username, password, customer_name, phone))
            
            else:
                insert_new_user = '''
                            INSERT INTO users (username, email, password, full_name, phone)
                            VALUES(%s, %s, crypt(%s, gen_salt('bf') ), %s, %s);
                            '''
                cur.execute(insert_new_user, (username, email, password, customer_name, phone))
            
            conn.commit()
            
            
            if(user_type == constants.FINANCER):
                
                get_user_id: str = '''
                                        SELECT user_id from users WHERE phone = %s;
                                        '''
                cur.execute(get_user_id, (phone, ))
                user_ids = cur.fetchone()
                
                get_role_id: str = '''
                                        SELECT id from roles WHERE name = 'FINANCER';
                                        '''
                cur.execute(get_role_id, ( ))
                role_ids = cur.fetchone()
                print(user_ids, role_ids)
                
                insert_into_user_role: str = '''
                    INSERT INTO user_role(user_id, role_id) 
                    VALUES (%s, %s);
                '''
                cur.execute(insert_into_user_role, (user_ids[0], role_ids[0], ))
            
            conn.commit()

    except Exception as exc:
        print("User Registration: ", exc, phone, email, name, username, password, user_type)
        return { 
                'error': message_constants.ERROR
        }, constants.STATUS_CODE_500
           
    return {
            'message' : 'User Successfully Registered.'
           }, constants.STATUS_CODE_200


