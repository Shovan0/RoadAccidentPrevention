-- =====================================================================
-- Road Accident Prevention -- Database Schema
-- Run this script in MySQL to set up the database.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `road-accident-prevention`;
USE `road-accident-prevention`;

-- ── Owners ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS owners (
    owner_id  INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    contact   VARCHAR(20),
    email     VARCHAR(100),
    address   TEXT
);

-- ── Drivers ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS drivers (
    driver_id      INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    license_number VARCHAR(20) UNIQUE,
    contact        VARCHAR(20),
    email          VARCHAR(100),
    address        TEXT,
    date_of_birth  DATE
);

-- ── Users ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id    INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    role       ENUM('admin','user') DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Cars ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cars (
    car_number   VARCHAR(20) PRIMARY KEY,
    owner_id     INT,
    driver_id    INT,
    make         VARCHAR(50),
    model        VARCHAR(50),
    year         INT,
    color        VARCHAR(30),
    vehicle_type ENUM('car','truck','bus') DEFAULT 'car',
    FOREIGN KEY (owner_id)  REFERENCES owners(owner_id)  ON DELETE SET NULL,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE SET NULL
);

-- =====================================================================
-- Sample  Data
-- =====================================================================

INSERT IGNORE INTO owners (owner_id, name, contact, email, address) VALUES
(1,  'Rajesh Kumar',      '+91-9876543210', 'rajesh.kumar@email.com',   '12 MG Road, Mumbai, MH'),
(2,  'Priya Sharma',      '+91-8765432109', 'priya.sharma@email.com',   '45 Park Street, New Delhi, DL'),
(3,  'Suresh Patel',      '+91-7654321098', 'suresh.patel@email.com',   '78 Residency Rd, Bengaluru, KA'),
(4,  'Anita Desai',       '+91-6543210987', 'anita.desai@email.com',    '23 Anna Salai, Chennai, TN'),
(5,  'Vikram Singh',      '+91-5432109876', 'vikram.singh@email.com',   '56 Lake Town, Kolkata, WB'),
(6,  'Meera Nair',        '+91-4321098765', 'meera.nair@email.com',     '89 Nehru Nagar, Ahmedabad, GJ'),
(7,  'Arjun Reddy',       '+91-3210987654', 'arjun.reddy@email.com',    '34 Civil Lines, Lucknow, UP'),
(8,  'Kavitha Rao',       '+91-2109876543', 'kavitha.rao@email.com',    '67 Sector 15, Gurugram, HR'),
(9,  'Deepak Joshi',      '+91-1098765432', 'deepak.joshi@email.com',   '90 Vaishali Nagar, Jaipur, RJ'),
(10, 'Sunita Verma',      '+91-9988776655', 'sunita.verma@email.com',   '11 Arera Colony, Bhopal, MP');

INSERT IGNORE INTO drivers (driver_id, name, license_number, contact, email, address, date_of_birth) VALUES
(1,  'Ramesh Yadav',      'MH0120001234', '+91-9871234567', 'ramesh.y@email.com',   '5 Workers Colony, Mumbai, MH',       '1985-03-15'),
(2,  'Sunita Jain',       'DL0220005678', '+91-8762345678', 'sunita.j@email.com',   '22 Lajpat Nagar, Delhi, DL',         '1990-07-22'),
(3,  'Mahesh Gowda',      'KA0320009012', '+91-7653456789', 'mahesh.g@email.com',   '44 Jayanagar, Bengaluru, KA',        '1988-11-08'),
(4,  'Lakshmi Pillai',    'TN0420003456', '+91-6544567890', 'lakshmi.p@email.com',  '66 T Nagar, Chennai, TN',            '1992-05-30'),
(5,  'Biswajit Das',      'WB0520007890', '+91-5435678901', 'biswajit.d@email.com', '88 Salt Lake, Kolkata, WB',          '1987-09-12'),
(6,  'Hardik Shah',       'GJ0620001234', '+91-4326789012', 'hardik.s@email.com',   '10 Satellite, Ahmedabad, GJ',        '1993-01-25'),
(7,  'Pradeep Mishra',    'UP0720005678', '+91-3217890123', 'pradeep.m@email.com',  '32 Gomti Nagar, Lucknow, UP',        '1986-06-18'),
(8,  'Geeta Rawat',       'HR0820009012', '+91-2108901234', 'geeta.r@email.com',    '54 DLF Phase 2, Gurugram, HR',       '1991-12-03'),
(9,  'Santosh Kumar',     'RJ0920003456', '+91-1099012345', 'santosh.k@email.com',  '76 C-Scheme, Jaipur, RJ',            '1989-04-27'),
(10, 'Asha Tiwari',       'MP1020007890', '+91-9980123456', 'asha.t@email.com',     '98 Malviya Nagar, Bhopal, MP',       '1994-08-14'),
(11, 'Ravi Chandran',     'TN0120011111', '+91-8871234567', 'ravi.c@email.com',     '31 Adyar, Chennai, TN',              '1983-02-09'),
(12, 'Pooja Mehta',       'MH0220022222', '+91-7762345678', 'pooja.m@email.com',    '53 Andheri West, Mumbai, MH',        '1996-10-19');

INSERT IGNORE INTO cars (car_number, owner_id, driver_id, make, model, year, color, vehicle_type) VALUES
('MH 01 AB 1234', 1,  1,  'Maruti',  'Swift',       2020, 'Red',    'car'),
('DL 02 CD 5678', 2,  2,  'Hyundai', 'Creta',       2021, 'White',  'car'),
('KA 03 EF 9012', 3,  3,  'Tata',    'Nexon',       2022, 'Blue',   'car'),
('TN 04 GH 3456', 4,  4,  'Honda',   'City',        2019, 'Silver', 'car'),
('WB 05 IJ 7890', 5,  5,  'Toyota',  'Innova',      2021, 'White',  'car'),
('GJ 06 KL 1234', 6,  6,  'Mahindra','Scorpio',     2020, 'Black',  'car'),
('UP 07 MN 5678', 7,  7,  'Ford',    'Ecosport',    2018, 'Grey',   'car'),
('HR 08 OP 9012', 8,  8,  'Kia',     'Seltos',      2022, 'Orange', 'car'),
('RJ 09 QR 3456', 9,  9,  'Renault', 'Kwid',        2021, 'Yellow', 'car'),
('MP 10 ST 7890', 10, 10, 'Suzuki',  'Baleno',      2020, 'Brown',  'car'),
('MH 02 UV 1111', 1,  11, 'Ashok Leyland', 'Dost',  2019, 'White',  'truck'),
('DL 03 WX 2222', 2,  12, 'TATA',    'Ultra',       2020, 'Blue',   'truck'),
('KA 04 YZ 3333', 3,  3,  'Volvo',   'B9R',         2021, 'Red',    'bus'),
('TN 05 AA 4444', 4,  4,  'Eicher',  'Skyline Pro', 2022, 'Green',  'bus'),
('WB 06 BB 5555', 5,  5,  'Bajaj',   'Maxima',      2020, 'Yellow', 'car'),
('GJ 07 CC 6666', 6,  6,  'Maruti',  'Dzire',       2021, 'Silver', 'car'),
('UP 08 DD 7777', 7,  7,  'Hyundai', 'Venue',       2022, 'Blue',   'car'),
('HR 09 EE 8888', 8,  8,  'Honda',   'Amaze',       2019, 'White',  'car'),
('RJ 10 FF 9999', 9,  9,  'Toyota',  'Glanza',      2021, 'Red',    'car'),
('MP 01 GG 1010', 10, 10, 'Tata',    'Tigor',       2020, 'Grey',   'car');
