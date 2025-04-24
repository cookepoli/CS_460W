import psycopg2

class Authenticator:
    def __init__(self):
        pass

    def login(self, username, password):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT member_id, firstname, lastname, (password = crypt(%s, password)) FROM member WHERE active = true", (password,))
                    members = cur.fetchall()


            for i in range(len(members)):
                name = members[i][1][0] + members[i][2][0:4]
                if self.checkUsername(username, name) and members[i][3] == True:
                    return members[i][0], members[i][1], members[i][2]

            return False, False, False

        except psycopg2.Error as e:
           return False, False, False


    def checkUsername(self, username, name):
        if name  == username:
            return True
        else:
            return False