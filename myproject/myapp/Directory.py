import psycopg2
from psycopg2 import sql

class Directory():
    def __init__(self):
        pass

    def getAll(self, memberid: int):
            #Member View
        if memberid != 1 and memberid !=2:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT firstname, lastname, email, phonenum FROM member WHERE optin = true AND active = true ORDER BY member_id")
                    return cur.fetchall()
            #Admin View
        else:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM member ORDER BY member_id")
                    return cur.fetchall()

    def searchAttr(self, memberid: str, attribute: str, value: str):
            #member View
        try:
            if memberid != 1 and memberid !=2:
                with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql.SQL("SELECT firstname, lastname, email, phonenum FROM member WHERE optin = TRUE AND active = true AND {attr} = %s ORDER BY member_id").format(attr=sql.Identifier(attribute)),
                                    (value,))
                        return cur.fetchall()
                #Admin View
            else:
                with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql.SQL("SELECT * FROM member WHERE {attr} = %s ORDER BY member_id").format(attr=sql.Identifier(attribute)),
                                    (value,))
                        return cur.fetchall()
        except psycopg2.Error as e:
            return -1
        except TypeError as e:
            return -1

    def nameLookup(self, firstname: str, lastname: str):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT member_id FROM member WHERE firstname = %s AND lastname = %s",(firstname, lastname))
                    return cur.fetchone()[0]
        except:
            return False

    def getEmails(self):
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT email FROM member WHERE active = True")
                return cur.fetchall()
