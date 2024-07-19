import mysql.connector
from config import *


def drop_n_create_database():
    conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    cursor.execute("create database sportbot")
    cursor.close()
    conn.close()
def create_cust_table():
    conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    SQL_Query = """  create table customer(
                                                        cust_id bigint primary key NOT NULL,
                                                        cust_name varchar(50) NOT NULL,
                                                        cust_lastname varchar(50) DEFAULT NULL,
                                                        cust_email varchar(50) DEFAULT NULL,
                                                        cust_phonenumber varchar(11) DEFAULT NULL,
                                                        registery_date datetime DEFAULT CURRENT_TIMESTAMP,
                                                        privilage enum('user','admin') DEFAULT NULL,
                                                        receipt_confirmed tinyint(1) DEFAULT '0'
                                                         ); """
    cursor.execute(SQL_Query)
    cursor.close()
    conn.close()



def create_coach_table():
    conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    SQL_Query = """  create table coach (
                                                       coach_id bigint primary key NOT NULL,
                                                       coach_name varchar(50) DEFAULT NULL,
                                                       coach_lastname varchar(50) DEFAULT NULL,
                                                       coach_email varchar(50) DEFAULT NULL,
                                                       coach_phonenumber varchar(11) DEFAULT NULL,
                                                       coach_expertise varchar(60) DEFAULT NULL,
                                                       registery_date datetime DEFAULT CURRENT_TIMESTAMP
                                                       );"""
    cursor.execute(SQL_Query)
    cursor.close()
    conn.close()

def create_plan_table():
    conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    SQL_Query = """  create table plan (
                                                       plan_id int primary key NOT NULL AUTO_INCREMENT,
                                                       cust_id bigint DEFAULT NULL,
                                                       coach_id bigint DEFAULT NULL,
                                                       plan_type varchar(20) DEFAULT NULL,
                                                       price decimal(10,2) DEFAULT NULL,
                                                       plan_date datetime DEFAULT CURRENT_TIMESTAMP,
                                                       CONSTRAINT fk_coach_id FOREIGN KEY (coach_id) REFERENCES coach (coach_id),
                                                       CONSTRAINT fk_cust_id FOREIGN KEY (cust_id) REFERENCES customer (cust_id) 
                                                       );"""
    cursor.execute(SQL_Query)
    cursor.close()
    conn.close()



def create_users_exercise_info_table():
    conn= mysql.connector.connect(user=db_username , password= db_password, host = 'localhost', database= db_name)
    cursor = conn.cursor()
    SQL_Query = """  create table users_exercise_info (
                                                          info_id bigint primary key NOT NULL,
                                                          cust_id bigint DEFAULT NULL,
                                                          gender varchar(10) DEFAULT NULL,
                                                          age varchar(80) DEFAULT NULL,
                                                          height int DEFAULT NULL,
                                                          weight int DEFAULT NULL,
                                                          goal varchar(100) DEFAULT NULL,
                                                          exercise_time varchar(100) DEFAULT NULL,
                                                          CONSTRAINT fkk_cust_id FOREIGN KEY (cust_id) REFERENCES customer (cust_id)
                                                        );"""
    cursor.execute(SQL_Query)
    cursor.close()
    conn.close()


if __name__=="__main__":
    drop_n_create_database()
    create_cust_table()
    create_coach_table()
    create_plan_table()