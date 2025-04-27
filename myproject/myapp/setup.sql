
CREATE USER aceduser WITH PASSWORD 'acedpassword';

CREATE EXTENSION pgcrypto;

CREATE TABLE IF NOT EXISTS member (
    member_id   SERIAL          NOT NULL,
    firstname   VARCHAR(32)     NOT NULL,
    lastname    VARCHAR(32)     NOT NULL,
    email       VARCHAR(64)     NOT NULL,
    phonenum    VARCHAR(12)     NOT NULL,
    guestpass   INT             NOT NULL DEFAULT 4,
    optIN       BOOLEAN         NOT NULL,
    active      BOOLEAN         NOT NULL DEFAULT TRUE,
    password    VARCHAR(64)     NOT NULL,

    PRIMARY KEY(member_id)
);

CREATE TABLE IF NOT EXISTS charges (
    charge_id   SERIAL              NOT NULL,
    member_id   INT                 NOT NULL,
    amount      DOUBLE PRECISION    NOT NULL,
    date        DATE                NOT NULL DEFAULT CURRENT_DATE,
    description VARCHAR(128)        NOT NULL,
    type        VARCHAR(6)          NOT NULL,
    isPaid      BOOLEAN             NOT NULL DEFAULT FALSE,

    PRIMARY KEY(charge_id),
    FOREIGN KEY(member_id) REFERENCES member(member_ID)
                                   ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservation (
    reservation_id  SERIAL          NOT NULL,
    court_num       INT             NOT NULL,
    res_day         INT             NOT NULL,
    start_time      TIME            NOT NULL,
    end_time        TIME            NOT NULL,
    member_ID       INT             NOT NULL,
    type            VARCHAR(7)      NOT NULL,

    PRIMARY KEY(reservation_id),
    FOREIGN KEY(member_id) REFERENCES member(member_id)
                                    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendees (
    reservation_ID  INT             NOT NULL,
    firstname       VARCHAR(32)     NOT NULL,
    lastname        VARCHAR(32)     NOT NULL,
    member_id       INT,

    FOREIGN KEY(reservation_id) REFERENCES reservation(reservation_id)
                                    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS billing_constants (
    guestfee    INT             NOT NULL,
    annualfee   INT             NOT NULL
);

GRANT ALL PRIVILEGES ON DATABASE aced TO aceduser;
GRANT ALL PRIVILEGES ON TABLE member TO aceduser;
GRANT ALL PRIVILEGES ON TABLE charges TO aceduser;
GRANT ALL PRIVILEGES ON TABLE reservation TO aceduser;
GRANT ALL PRIVILEGES ON TABLE attendees TO aceduser;
GRANT ALL PRIVILEGES ON TABLE billing_constants to aceduser;
GRANT ALL PRIVILEGES ON SEQUENCE member_member_id_seq to aceduser;
GRANT ALL PRIVILEGES ON SEQUENCE reservation_reservation_id_seq to aceduser;
GRANT ALL PRIVILEGES ON SEQUENCE charges_charge_id_seq to aceduser;


INSERT INTO member (firstname, lastname, email, phonenum, optin, active, password) VALUES (
    'President',
    'Staff',
    'president@aced.com',
    '111-111-1111',
    FALSE,
    TRUE,
    crypt('ilovetennis',gen_salt('md5'))
    );

INSERT INTO member (firstname, lastname, email, phonenum, optin, active, password) VALUES (
    'Billing',
    'Staff',
    'billing@aced.com',
    '111-111-1112',
    FALSE,
    TRUE,
    crypt('ilovemoney', gen_salt('md5'))
    );

INSERT INTO billing_constants VALUES (
    5,
    400
    );