-- ============================================================
--  SAMPLE DATA  (run AFTER schema.sql)
-- ============================================================

-- Staff
INSERT INTO staff (full_name, role, specialization, contact, email) VALUES
('Dr. Roshan Perera',   'Hospital Management',    'Forensic Pathology',  '0771234567', 'roshan@forensic.lk'),
('Dr. Nimal Silva',     'Hospital Management',       'Judicial Medicine',   '0772345678', 'nimal@forensic.lk'),
('Ms. Kamala Fernando', 'Hospital Management', 'Toxicology',          '0773456789', 'kamala@forensic.lk'),
('Mr. Suresh Jayawardena','Hospital Management',   NULL,                  '0774567890', 'suresh@forensic.lk'),
('Inspector Ranjith',   'Police Management',    'Criminal Investigation','0775678901','ranjith@police.lk'),
('Ms. Priya Admin',     'Hospital Management',     NULL,                  '0776789012', 'priya@forensic.lk');

-- Users  (passwords are all "Password123" — hashed with bcrypt)
-- You will regenerate these via the app's init command, but these are placeholder hashes
INSERT INTO app_user (username, password_hash, role, staff_id) VALUES
('admin',   '$2b$12$placeholder_admin_hash_here',   'Hospital Management',     6),
('doctor1', '$2b$12$placeholder_doctor_hash_here',  'Hospital Management',    1),
('jmo1',    '$2b$12$placeholder_jmo_hash_here',     'Hospital Management',       2),
('lab1',    '$2b$12$placeholder_lab_hash_here',     'Hospital Management', 3),
('clerk1',  '$2b$12$placeholder_clerk_hash_here',   'Hospital Management',     4),
('police1', '$2b$12$placeholder_police_hash_here',  'Police Management',    5);

-- Patients
INSERT INTO patient (full_name, nic, dob, gender, address, contact, hospital_no) VALUES
('Kamal Bandara',     '198501234567', '1985-03-12', 'Male',   '12 Main St, Colombo',    '0711111111', 'H001'),
('Seetha Rathnayake', '199203456789', '1992-07-24', 'Female', '45 Lake Rd, Kandy',      '0712222222', 'H002'),
('Pradeep Wijesinghe','198712345678', '1987-11-05', 'Male',   '78 Hill Ave, Galle',     '0713333333', 'H003'),
('Nimali Dissanayake','200001234560', '2000-01-15', 'Female', '23 Beach Rd, Matara',    '0714444444', 'H004'),
('Rohan Gunawardena', '197509876543', '1975-09-30', 'Male',   '56 Temple Rd, Colombo',  '0715555555', 'H005');

-- Cases
INSERT INTO forensic_case (patient_id, case_number, case_type, incident_date, admission_date, police_ref, court_ref, police_station, status, description, created_by) VALUES
(1, 'FC-2024-001', 'Postmortem',    '2024-01-10', '2024-01-11', 'PR-001/2024', 'CR-001/2024', 'Colombo Fort',   'Closed',      'Death under suspicious circumstances', 1),
(2, 'FC-2024-002', 'Assault',       '2024-01-15', '2024-01-15', 'PR-002/2024', NULL,          'Kandy Central',  'In Progress', 'Physical assault with blunt object',   1),
(3, 'FC-2024-003', 'Accident',      '2024-02-01', '2024-02-02', 'PR-003/2024', 'CR-002/2024', 'Galle Road',     'Open',        'Road traffic accident',                1),
(4, 'FC-2024-004', 'Sexual Assault','2024-02-10', '2024-02-10', 'PR-004/2024', 'CR-003/2024', 'Matara',         'In Progress', 'Sexual assault case',                  1),
(5, 'FC-2024-005', 'Toxicology',    '2024-03-05', '2024-03-06', 'PR-005/2024', NULL,          'Colombo North',  'Open',        'Suspected poisoning',                  1);

-- Case-Doctor assignments
INSERT INTO case_doctor (case_id, staff_id) VALUES
(1, 1),(1, 2),(2, 1),(3, 2),(4, 1),(5, 2);

-- Postmortem records
INSERT INTO postmortem (case_id, doctor_id, exam_date, findings, cause_of_death, manner_of_death, body_condition) VALUES
(1, 1, '2024-01-12', 'Multiple blunt force injuries to the skull. Internal hemorrhage noted.', 'Traumatic brain injury', 'Homicide', 'Fresh'),
(5, 2, '2024-03-07', 'Elevated blood toxin levels. Organ damage consistent with poisoning.', 'Acute poisoning', 'Undetermined', 'Fresh');

-- Evidence
INSERT INTO evidence (case_id, evidence_type, description, storage_location, collected_by, collected_date, status) VALUES
(1, 'Weapon',     'Wooden bat found at scene',       'Locker A-1', 'Inspector Ranjith', '2024-01-10', 'In Storage'),
(1, 'Clothing',   'Victim clothing with blood stains','Locker A-2', 'Inspector Ranjith', '2024-01-10', 'Sent to Lab'),
(2, 'Photograph', 'Injury photographs',               'Digital Storage', 'Dr. Roshan', '2024-01-15', 'In Storage'),
(4, 'Swab',       'DNA swab samples',                'Lab Cold Storage','Dr. Roshan',  '2024-02-10', 'Sent to Lab'),
(5, 'Blood Sample','Blood sample for toxicology',    'Lab Cold Storage','Dr. Nimal',   '2024-03-06', 'Sent to Lab');

-- Lab Tests
INSERT INTO lab_test (case_id, evidence_id, test_type, requested_by, tested_by, test_date, result, status) VALUES
(1, 2, 'DNA Analysis',      1, 'Ms. Kamala', '2024-01-18', 'DNA matched suspect profile', 'Completed'),
(4, 4, 'DNA Profiling',     1, 'Ms. Kamala', '2024-02-15', 'Pending analysis',            'Pending'),
(5, 5, 'Toxicology Screen', 2, 'Ms. Kamala', '2024-03-10', 'Organophosphate detected',    'Completed');

-- Court Reports
INSERT INTO court_report (case_id, doctor_id, report_type, content, submission_date, court_name, status) VALUES
(1, 1, 'Post-Mortem Report', 'Death caused by traumatic brain injury. Manner: Homicide.', '2024-01-20', 'Colombo Magistrate Court', 'Submitted'),
(5, 2, 'Toxicology Report',  'Organophosphate compound detected in blood and urine samples.', '2024-03-15', 'Colombo High Court', 'Accepted');