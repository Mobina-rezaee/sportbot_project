import requests
import telebot
import os
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove , InlineKeyboardMarkup, InlineKeyboardButton 
import mysql.connector
from datetime import datetime
from config import * 


user_info=dict()  #{cid, {'first_name': '', 'last_name': '' ,'email_address':'', 'phone_number':1}}
user_steps=dict()
user_sup_message=dict() # {cid, {'message': ''}}
user_exercise_info=dict() # {cid: {'gender': '', 'age': 17 ,'height':175, 'weight':70, 'goal':'', 'exercise_time':''} , ...}
coach_info = dict() # {cid, {'first_name': '', 'last_name': '' ,'email_address':'', 'phone_number':1,'coach_expertise':''}}
user_records = []
coach_dict = dict() # {coach_id : 'coach_name' , ... ,} to get all coaches ids
plan_dict = dict () # {cid : {'cid' : '' , 'coach_id' : '' , 'plan_type': '' , 'price' : 000 , 'plan_date': '' }, ...}





commands = {
    'start'         : 'start the bot',
    'help'          : 'help',
}

coach_commands = {
    'users_info'     : 'get last users info update',
}


admin_commands = {
    'support_message'     : 'get last support message',
}


                                            






def insert_cust_info(cust_id , cust_name , cust_lastname, cust_email , cust_phonenumber , registery_date , privilage ,  receipt_confirmed):
    conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    SQL_Query = """ insert into  customer(cust_id , cust_name , cust_lastname,  cust_email , cust_phonenumber , registery_date , privilage ,  receipt_confirmed)
    values (%s , %s , %s ,%s, %s,%s ,%s ,%s );"""
    cursor.execute(SQL_Query, (cust_id , cust_name , cust_lastname,  cust_email , cust_phonenumber , registery_date , privilage ,  receipt_confirmed))
    conn.commit()
    cursor.close()
    conn.close()


def insert_coach_info(coach_id , coach_name , coach_lastname,  coach_email , coach_phonenumber , coach_expertise,registery_date):
    conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    SQL_Query = """ insert into  coach(coach_id, coach_name , coach_lastname,  coach_email , coach_phonenumber , coach_expertise, registery_date )
    values (%s , %s , %s ,%s, %s,%s ,%s );"""
    cursor.execute(SQL_Query, (coach_id, coach_name , coach_lastname,  coach_email , coach_phonenumber , coach_expertise, registery_date))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_info(cid):
    conn = mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    SQL_Quary = "SELECT cust_name,cust_lastname,cust_email FROM customer WHERE cust_id=%s"
    cursor.execute(SQL_Quary, (cid,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res


def update_wallet(cid, amount):
    conn = mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE customer SET wallet= wallet + ? WHERE cust_id =?", (amount,cid))
    conn.commit()
    conn.close()


def get_all_coaches():
    global coach_dict 
    conn = mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor=conn.cursor()
    cursor.execute("select coach_id,coach_name from coach")
    coaches = cursor.fetchall()
    for coach_id , coach_name in coaches:
        coach_dict[coach_id] = coach_name
    conn.commit()
    conn.close()
    return coach_dict

get_all_coaches()


def get_user_step(cid):
    return user_steps.setdefault(cid, 0)


bot = telebot.TeleBot(BOT_TOKEN)
hideboard = ReplyKeyboardRemove()
def listener(messages):
    for m in messages:
        if m.content_type=='text':
            print(str(m.chat.first_name)+"["+str(m.chat.id)+"]:"+m.text)




bot.set_update_listener(listener)


def check_user_registered(cid):
            conn = mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
            cursor = conn.cursor(dictionary=True)
            SQL_Quary = "SELECT * FROM customer WHERE cust_id=%s"
            cursor.execute(SQL_Quary, (cid,))
            if cursor.fetchone():
                return True
            else:
                return False

def check_coach_registered(cid):
            conn = mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
            cursor = conn.cursor(dictionary=True)
            SQL_Quary = "SELECT * FROM coach WHERE coach_id=%s"
            cursor.execute(SQL_Quary, (cid,))
            if cursor.fetchone():
                return True
            else:
                return False


@bot.message_handler(commands=['start'])
def send_menu(message):
    cid = message.chat.id
    cname = message.chat.first_name
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('sign up' , callback_data='sign up'), InlineKeyboardButton('exercise plan' , callback_data='exercise plan'))
    markup.add(InlineKeyboardButton('support', callback_data='support') , InlineKeyboardButton('myplan', callback_data='my plan'))
    
    bot.send_message(cid , f''' User  {cname} you can use the following buttons to continue using the robot ''' , reply_markup=markup)





@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:  
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    # if cid in coach_ids:
    #     help_text += "***Coach commands:*** \n"
    #     for key in coach_commands:  
    #         help_text += "/" + key + ": "
    #         help_text += coach_commands[key] + "\n"
    # if cid in admin_id:
    #     help_text += "***admin commands:*** \n"
    #     for key in admin_commands:  
    #         help_text += "/" + key + ": "
    #         help_text += admin_commands[key] + "\n"
    bot.send_message(cid, help_text) 


@bot.callback_query_handler(func= lambda call : True)
def call_back_handler(call):
    is_button_clicked = False
    cid = call.message.chat.id
    data = call.data
    mid = call.message.message_id 
    call_id = call.id 
    

    if data == 'sign up':
        if check_user_registered(cid):
            bot.send_message(cid, 'You have already registered before.')
        elif check_coach_registered(cid):
            bot.send_message(cid, 'You have already registered before.')
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('normal user')
            markup.add('coach')
            bot.send_message(cid,'I register in bot as:', reply_markup=markup)
            bot.register_next_step_handler(call.message, handle_registration)
             
        



    elif data == 'support':
        if check_user_registered(cid):
           bot.send_message(cid , 'please send your message:')
           bot.answer_callback_query(call_id, 'support selected!')
           user_steps[cid]= 300
        
        else :
            bot.send_message(cid , 'you have to signup first')




    elif data == 'exercise plan':
        if check_user_registered(cid):
           markup = ReplyKeyboardMarkup(resize_keyboard=True)
           markup.add('Male')
           markup.add('female')
           bot.send_message(cid,'choos your gender',reply_markup=markup)
           markup = hideboard
           bot.answer_callback_query(call_id, 'exercise program selected!')
           user_steps[cid]= 400
        
        else :
            bot.send_message(cid , 'you have to signup first')



    elif data == 'my plan':
        bot.answer_callback_query(call_id, 'myplan selected!')
        cid = call.message.chat.id
        conn = mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
        cursor = conn.cursor()
        SQL_Quary = "SELECT receipt_confirmed FROM customer WHERE cust_id=%s"
        cursor.execute(SQL_Quary, (cid,))
        res = cursor.fetchone()
        if res and res[0]==1:
             photos_dir = os.path.join(os.getcwd(), 'pictures')
             file_format = 'jpg' 
             bot.send_photo(cid, photo=open(os.path.join(photos_dir, f'result.{file_format}'), 'rb'))
             cursor.execute("UPDATE customer SET receipt_confirmed = %s WHERE cust_id =%s", (0,cid))
             user_steps[cid] = 1000

        
        elif res and res[0]==0:
            bot.send_message(cid, "there is a problem with your receipt confirmation or your information")
        
        else:
             bot.send_message(cid, "there is no plan for you yet")




    elif data == 'confirm':
        index = user_records[0]
        plan_dict.setdefault(index, {'cust_id': 0 , 'coach_id':0, 'plan_type':'sportplan', 'price':300000, 'plan_date':datetime.now()})
        plan_dict['cust_id']= index
        bot.send_message(user_records[0], f"Your payment receipt has been confirmed")
        conn = mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE customer SET receipt_confirmed = %s where cust_id = %s" , (1,index)) #1 is true 0 is false
        conn.commit()
        conn.close()

        markup = InlineKeyboardMarkup()
        coach_confirm = InlineKeyboardButton('confirm', callback_data='coach_confirm')
        markup.add(coach_confirm)

        for coach_id , coach_name in coach_dict.items():
            user_info = user_exercise_info[index]
            gender = user_info['gender']
            age = user_info['age']
            height = user_info['height']
            weight = user_info['weight']
            goal = user_info['goal']
            exercise_time = user_info['exercise_time']
        
            user_details = (
            f" User: {index}\n"
            f" Gender: {gender}\n"
            f" Age: {age}\n"
            f" Height: {height}\n"
            f" Weight: {weight}\n"
            f" Goal: {goal}\n"
            f" Times of exercise :  {exercise_time}"
            )
            
            bot.send_message(coach_id, user_details, reply_markup= markup)
        
        


    elif data == 'coach_confirm':
           x = user_records[0]
           bot.edit_message_reply_markup(cid, message_id=call.message.message_id, reply_markup=None)
           bot.send_message(cid,'dear coach please send the plan photo')
           plan_dict['coach_id']= cid

           conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
           cursor = conn.cursor()
           SQL_Query = """ insert into  plan( cust_id , coach_id , plan_type , price , plan_date )
           values (%s ,%s, %s,%s ,%s);"""
           cursor.execute(SQL_Query, (x , cid , 'sport', 300000 , datetime.now()))
           conn.commit()
           cursor.close()
           conn.close()
           
           user_records.remove(x)
           user_steps[cid]=500
       
    

            


    elif data=='reject':
        try:
            index = user_records[0]
            bot.send_message(user_records[0], "Your payment receipt has been rejected")
            user_records.remove(index)
        except Exception as e:
            bot.send_message(admin_id,'an error happened, please try to reject again later')



    elif data == 'support_received':
        bot.edit_message_reply_markup(cid, message_id=call.message.message_id, reply_markup=None)
        send_menu(call.message)


         


        
        

def handle_registration(message):
    cid = message.chat.id
    user_type = message.text

    if message.text == 'normal user':
        user_steps[cid] = 100
        bot.send_message(cid,'please enter your name:')
    elif message.text == 'coach':
        user_steps[cid] = 600
        bot.send_message(cid,'please enter your name:')
    else:
        bot.send_message(cid, 'Invalid user type. Please try again.')
        bot.register_next_step_handler(message, handle_registration)
    


# sign up steps (100 to 140)
  
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 100)
def process_first_name(message):
    cid = message.chat.id
    user_info.setdefault(cid, {'first_name': '', 'last_name': '' ,'email_address':'', 'phone_number':1})
    user_info[cid]['first_name'] = message.text
    user_steps[cid] = 110
    bot.send_message(cid, 'please enter your last name:')

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 110)
def process_last_name(message):
    cid = message.chat.id
    last_name = message.text
    user_info[cid]['last_name'] = last_name
    user_steps[cid] = 120
    bot.send_message(cid, 'please enter your email address')

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 120)
def process_address(message):
    cid = message.chat.id
    email_address = message.text
    user_info[cid]['email_address'] = email_address
    user_steps[cid] = 130
    bot.send_message(cid, 'please enter your phone number ')

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 130)
def process_phone_number(message):
    cid = message.chat.id
    phone_number = message.text
    try:
        phone_number= str(int(phone_number))
    except ValueError:
        bot.send_message(cid , "invalid phone number")
        return
    user_info[cid]['phone_number']=phone_number
    first_name = user_info[cid]['first_name']
    last_name = user_info[cid]['last_name']
    email_address= user_info[cid]['email_address']
    full_name = f'{first_name} {last_name} '
    text = f''' You have successfully signed up

If the information below is correct, confirm it :       



Full name : {full_name}
Email : {user_info[cid]['email_address']}
Phone number : {user_info[cid]['phone_number']}
 '''
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('yes')
    markup.add('no')
    bot.send_message(cid , text, reply_markup=markup)
    user_steps[cid]=140
    
    

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 140)
def yes_process(message):
    cid = message.chat.id
    if message.text == 'yes':
        markup = hideboard
        bot.send_message(cid, 'information confirmed✅', reply_markup=markup)
        send_menu(message)
        insert_cust_info(cid, user_info[cid]['first_name'],user_info[cid]['last_name'],120, user_info[cid]['email_address'],user_info[cid]['phone_number'], datetime.now(),'user', 0)
    elif message.text == 'no':
        bot.send_message(cid, 'Registration cancelled. Please click on the "sign up" button to start again.')
    
    
    

#  handeling customer receipt and send it to admin step

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 210, content_types=['photo'])
def receive_receipt(message):
    cid = message.chat.id
    file_id = message.photo[-1].file_id
    file_name = f"{cid}_receipt.jpg"
    file_path = bot.get_file(file_id).file_path
    downloaded_file = bot.download_file(file_path)
    receipt_folder = os.path.join(os.getcwd(), 'receipt')
    if not os.path.exists(receipt_folder):
        os.makedirs(receipt_folder)
    save_path = os.path.join(receipt_folder, file_name)
    with open(save_path, 'wb') as f:
        f.write(downloaded_file)
    with open(save_path, 'rb') as f:
        markup = InlineKeyboardMarkup()
        confirm_btn = InlineKeyboardButton('confirm', callback_data='confirm')
        reject_btn = InlineKeyboardButton('reject', callback_data='reject')
        markup.add(confirm_btn, reject_btn)
        user_records.append(cid)
        bot.send_photo(admin_id, f, caption=f"receipt from {cid} \n please choose if you want to confirm or not: ", reply_markup=markup)
        bot.send_message(cid, "your receipt sent to admin , you can get your plan after admin cofirmation")

    
    
#  support message steps (300 to 310)

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 300)
def process_admin_message(message):
    cid = message.chat.id
    sup_message = message.text
    user_sup_message.setdefault(cid, {'message': ''})
    user_sup_message[cid]['message'] = sup_message
    sup_info = f''' Your message sent 
The admin will see your message and solve your problem
If the information below is correct , confirm it :
User: {message.chat.first_name}
Message content : {sup_message} '''

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('yes')
    markup.add('no')
    bot.send_message(cid, sup_info, reply_markup=markup)
    user_steps[cid] = 310

    

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 310)
def yes_process(message):
    cid = message.chat.id
    if message.text == 'yes':
        # User confirmed the information
        markup = hideboard
        bot.send_message(cid, 'information confirmed✅', reply_markup=markup)
        send_menu(message)
        markup2 = InlineKeyboardMarkup()
        support_received = InlineKeyboardButton('received', callback_data='support_received')
        markup2.add(support_received)
        admin_cid = admin_id[0] 
        admin_message = f"New support message from {message.chat.first_name} (ID: {cid}):\n{ user_sup_message[cid]['message']}"
        bot.send_message(admin_cid, admin_message , reply_markup= markup2)
        del user_sup_message[cid]
    
    elif message.text == 'no' :
        bot.send_message(cid, 'sending message cancelled. Please click on the "support" button to start again.')
        
    
    
    


#  user exercise info steps (400 to 460)

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 400)
def age_process(message):
    cid = message.chat.id
    user_exercise_info.setdefault(cid, {'gender': '', 'age': 17 ,'height':175, 'weight':70, 'goal':'', 'exercise_time':''})
    user_exercise_info[cid]['gender'] = message.text
    if message.text=='Male' or message.text=='female':
        markup= ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('5 to 15 years old')
        markup.add('16 to 30 years old')
        markup.add('31 to 40 years old')
        markup.add('41 to 50 years old')
        bot.send_message(cid, 'choose your age:', reply_markup=markup)
        markup = hideboard
        user_steps[cid] = 410

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 410)
def height_process(message):
    cid = message.chat.id
    user_exercise_info[cid]['age'] = message.text
    if message.text=='5 to 15 years old' or message.text=='16 to 30 years old' or message.text=='31 to 40 years old' or message.text=='41 to 50 years old' :
        bot.send_message(cid, 'enter your height:',reply_to_message_id=message.message_id)
        markup = hideboard
        user_steps[cid] = 420

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 420)
def weight_process(message):
    cid = message.chat.id
    
    try:
       user_exercise_info[cid]['height'] = str(int(message.text))
    except ValueError:
        bot.send_message(cid , "invalid ")
        return
    if message.text:
        bot.send_message(cid, 'enter your weight',reply_to_message_id=message.message_id)
        markup = hideboard
        user_steps[cid] = 430

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 430)
def gym_goal_process(message):
    cid = message.chat.id
    
    try:
       user_exercise_info[cid]['weight'] = str(int(message.text))
    except ValueError:
        bot.send_message(cid , "invalid")
        return
    if message.text:
        markup= ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('get in shape')
        markup.add('build strength')
        markup.add('get lean')
        bot.send_message(cid, 'choose your gym goal:', reply_markup=markup)
        markup = hideboard
        user_steps[cid] = 440


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 440)
def exercise_time_process(message):
    cid = message.chat.id
    
    user_exercise_info[cid]['goal'] = message.text
    if message.text:
        markup= ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('once a week')
        markup.add('twice a week')
        markup.add('tree times a week')
        markup.add(' more than tree times in a week')
        bot.send_message(cid, 'how often do you want to exercise:', reply_markup=markup)
        markup = hideboard
        
        user_steps[cid] = 450

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 450)
def exercise_time_process(message):
    cid = message.chat.id
    user_exercise_info[cid]['exercise_time'] = message.text
    
   
    
    

    exercise_info = f''' Dear user
If the information below is correct , please confirm it:

Gender:{user_exercise_info[cid]['gender']}
Age:{user_exercise_info[cid]['age']}
Height:{user_exercise_info[cid]['height']}
Weight:{user_exercise_info[cid]['weight']}
Gym goal:{user_exercise_info[cid]['goal']}
Number of times of exercise:{user_exercise_info[cid]['exercise_time']}
  '''

    markup= ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('yes')
    markup.add ('no')
    bot.send_message(cid, exercise_info,reply_markup=markup)
    user_steps[cid] = 460
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 460)
def yes_process(message):
    cid = message.chat.id
    if message.text == 'yes':
       # conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
       # cursor = conn.cursor()
       # cursor.execute("insert into users_exercise_info (chat_id, gender , age , height, weight, goal , exercise_time ) values (%s , %s , %s , %s , %s , %s , %s)",(cid , user_exercise_info[cid]['gender'], user_exercise_info[cid]['age'],user_exercise_info[cid]['height'], user_exercise_info[cid]['weight'], user_exercise_info[cid]['goal'],user_exercise_info[cid]['exercise_time']))
       # conn.commit()
       markup = hideboard
       bot.send_message(cid, "for getting your plan you must pay 300000 tomans to this card number first\n\n 6104_3386_5167_1234 \n\n please send the receipt after payment ")
       user_steps[cid]=210

    elif message.text == 'no':
         bot.send_message(cid, 'saving information cancelled. Please click on the "exercise plan" button to start again.')





#  hadling the plan photo sent by coach

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 500, content_types=['photo'])
def photo_handler(message):
    cid = message.chat.id
    file_id = message.photo[-1].file_id
    info = bot.get_file(file_id)
    file_content = bot.download_file(info.file_path)
    file_format = info.file_path.split('.')[-1]
    photos_dir = os.path.join(os.getcwd(), 'pictures')
    if not os.path.exists(photos_dir):
        os.makedirs(photos_dir)
    file_path = os.path.join(photos_dir, f'result.{file_format}')
    with open(file_path, 'wb') as f:
        f.write(file_content)
    bot.send_message(cid, 'your picture saved successfully ', reply_to_message_id=message.message_id)
  


#  coach sign up steps (600 to  650)

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 600)
def process_coach_first_name(message):
    cid = message.chat.id
    coach_info.setdefault(cid, {'first_name': '', 'last_name': '' ,'email_address':'', 'phone_number':1,'coach_expertise':''})
    coach_info[cid]['first_name'] = message.text
    user_steps[cid] = 610
    bot.send_message(cid, 'please enter your last name coach:')

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 610)
def process_coach_last_name(message):
    cid = message.chat.id
    last_name = message.text
    coach_info[cid]['last_name'] = last_name
    user_steps[cid] = 620
    bot.send_message(cid, 'please enter your email address')

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 620)
def process_coach_address(message):
    cid = message.chat.id
    email_address = message.text
    coach_info[cid]['email_address'] = email_address
    user_steps[cid] = 630
    bot.send_message(cid, 'please enter your phone number ')



@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 630)
def process_coach_phone_number(message):
    cid = message.chat.id
    phone_number = message.text
    try:
        phone_number= str(int(phone_number))
    except ValueError:
        bot.send_message(cid , "invalid phone number")
        return
    coach_info[cid]['phone_number']=phone_number
    user_steps[cid]=640
    bot.send_message(cid, 'please enter your expertise:')
    

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 640)
def process_coach_expertise(message):
    cid = message.chat.id
    expertise = message.text
    coach_info[cid]['coach_expertise'] = expertise
    first_name = coach_info[cid]['first_name']
    last_name = coach_info[cid]['last_name']
    email_address = coach_info[cid]['email_address']
    phone_number = coach_info[cid]['phone_number']
    full_name = f'{first_name} {last_name}'
    text = f''' You have successfully signed up
If the information below is correct, confirm it :
   Full name : {full_name}
Email : {coach_info[cid]['email_address']}
Phone number : {coach_info[cid]['phone_number']}
Expertise : {coach_info[cid]['coach_expertise']} '''
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('yes')
    markup.add('no')
    bot.send_message(cid, text, reply_markup=markup)
    user_steps[cid] = 650

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 650)
def yes_process(message):
    cid = message.chat.id
    if message.text == 'yes':
       markup = hideboard
       bot.send_message(cid, 'information confirmed✅', reply_markup=markup)
       send_menu(message)
       insert_coach_info(cid, coach_info[cid]['first_name'], coach_info[cid]['last_name'], coach_info[cid]['email_address'], coach_info[cid]['phone_number'], coach_info[cid]['coach_expertise'], datetime.now())
    
    elif message.text == 'no':
         bot.send_message(cid, 'saving information cancelled. Please click on the "sign up" button to start again.')



# handling default message

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    cid= message.chat.id
    default_message = 'undefined'
    if cid in admin_id:
        bot.send_message(cid, 'undefined', reply_to_message_id=message.message_id)
    else:

        bot.send_message(cid , default_message, reply_to_message_id= message.message_id) 
    

bot.infinity_polling() 