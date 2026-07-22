-- ============================================================
-- FORENSIC MEDICO-LEGAL DATABASE
-- 02_dml_seed_data.sql — Data Manipulation Language (DML)
-- Initial Baseline & 8 Diverse Forensic Test Cases
-- ============================================================

-- ------------------------------------------------------------
-- 1. ROLES
-- ------------------------------------------------------------
INSERT INTO role (role_id, role_name) VALUES
 (1, 'Administrator'),
 (2, 'Senior JMO'),
 (3, 'JMO'),
 (4, 'Lab Technician'),
 (5, 'Clerk');

-- ------------------------------------------------------------
-- 2. STAFF
-- ------------------------------------------------------------
INSERT INTO staff (staff_id, full_name, designation, slmc_regno, qualification, station) VALUES
 (1, 'Dr. W.M.S. Perera',   'Senior JMO',   'SLMC-11023', 'MBBS, MD (Forensic Medicine)', 'Colombo North Teaching Hospital'),
 (2, 'Dr. R.A.D. Fernando', 'JMO',          'SLMC-15678', 'MBBS, Dip. Leg. Med.',         'Colombo North Teaching Hospital'),
 (3, 'Dr. K.G.N. Silva',    'JMO',          'SLMC-16789', 'MBBS',                         'National Hospital Kandy'),
 (4, 'Dr. T.P. Jayasuriya', 'PG Trainee',   'SLMC-19023', 'MBBS (PGIM Trainee)',          'Colombo North Teaching Hospital'),
 (5, 'Mr. A.B. Wickramasinghe', 'Tech Officer', NULL,     'Dip. Medical Lab Technology',  'Colombo North Teaching Hospital'),
 (6, 'Mrs. C.D. Ranatunga', 'Clerk',        NULL,          'Diploma in Office Management', 'Colombo North Teaching Hospital'),
 (7, 'Mr. S.J. Bandara',    'Tech Officer', NULL,          'Dip. Medical Lab Technology',  'National Hospital Kandy');

-- ------------------------------------------------------------
-- 3. APP USERS (Default Password Hash = "password123")
-- ------------------------------------------------------------
INSERT INTO app_user (user_id, username, password_hash, role_id, staff_id, is_active) VALUES
 (1, 'admin',      '$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e', 1, NULL, TRUE),
 (2, 'dr.perera',  '$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e', 2, 1,    TRUE),
 (3, 'dr.fernando','$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e', 3, 2,    TRUE),
 (4, 'dr.silva',   '$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e', 3, 3,    TRUE),
 (5, 'tech.wick',  '$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e', 4, 5,    TRUE),
 (6, 'clerk.rana', '$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e', 5, 6,    TRUE);

-- ------------------------------------------------------------
-- 4. PATIENTS
-- ------------------------------------------------------------
INSERT INTO patient (patient_id, full_name, nic_passportno, dob, age, gender, address, occupation) VALUES
 (1, 'Nimal Perera',           '198512345678',  '1985-03-12', 41, 'M', '45 Galle Road, Colombo 03',        'Driver'),
 (2, 'Kamala Wijesinghe',      '199234567891',  '1992-07-01', 33, 'F', '12 Kandy Road, Kadawatha',          'Teacher'),
 (3, 'Sunil Rathnayake',       '197845612378',  '1978-11-20', 47, 'M', '78 Peradeniya Road, Kandy',         'Farmer'),
 (4, 'Unknown Male #A-2026-14', NULL,           NULL,          NULL, 'Unknown', 'N/A (unidentified remains found, Mahaweli riverbank)', NULL),
 (5, 'Anusha Fernando',        '200156789012',  '2001-05-09', 25, 'F', '9 Station Road, Gampaha',           'Undergraduate'),
 (6, 'Piyadasa Gunasekara',    '196512378945',  '1965-01-30', 61, 'M', '23 Temple Lane, Matale',            'Retired'),
 (7, 'Sarath Wickramasinghe',  '197923456789',  '1979-04-15', 47, 'M', '12 Main Street, Negombo',           'Business Owner'),
 (8, 'Dilini Jayawardena',     '200287654321',  '2002-09-18', 23, 'F', '88 Lake Road, Kurunegala',          'Bank Clerk');

-- ------------------------------------------------------------
-- 5. POLICE STATIONS & INVESTIGATING OFFICERS
-- ------------------------------------------------------------
INSERT INTO police_station (police_station_id, station_name, division) VALUES
 (1, 'Colombo North Police Station', 'Colombo'),
 (2, 'Kandy Police Station',         'Kandy'),
 (3, 'Gampaha Police Station',       'Gampaha'),
 (4, 'Matale Police Station',        'Matale');

INSERT INTO investigating_officer (officer_id, name, rank, officer_regno, police_station_id) VALUES
 (1, 'W.A. Jayasekara',   'Sub Inspector',    'SI/4521', 1),
 (2, 'K.M. Perera',       'Police Constable', 'PC/9812', 1),
 (3, 'R.D. Bandara',      'Inspector',        'IP/2210', 2),
 (4, 'S.L. Fonseka',      'Sub Inspector',    'SI/5643', 3),
 (5, 'N.K. Rajapaksa',    'Police Constable', 'PC/7734', 4),
 (6, 'M.P. Dissanayake',  'Sub Inspector',    'SI/8821', 1),
 (7, 'K.L. Jayawardena',  'Inspector',        'IP/3342', 3);

-- ------------------------------------------------------------
-- 6. COURTS & MAGISTRATES
-- ------------------------------------------------------------
INSERT INTO court (court_id, court_name, district) VALUES
 (1, 'Magistrate Court Colombo', 'Colombo'),
 (2, 'Magistrate Court Kandy',   'Kandy'),
 (3, 'Magistrate Court Gampaha', 'Gampaha'),
 (4, 'Magistrate Court Matale',  'Matale');

INSERT INTO magistrate (magistrate_id, name, court_id) VALUES
 (1, 'Hon. A.B.C. Wijeratne', 1),
 (2, 'Hon. D.M. Senanayake',  2),
 (3, 'Hon. P.R. Amarasinghe', 3),
 (4, 'Hon. T.K. Wickrama',    4);

-- ------------------------------------------------------------
-- 7. CASE MASTER LOG (8 Diverse Cases)
-- ------------------------------------------------------------
INSERT INTO case_master
 (case_id, case_number, inquest_no, case_type, police_refno, court_refno, dept_refno,
  incident_date, received_date, trial_date, status,
  patient_id, police_station_id, issuing_officer_id, producing_officer_id, court_id, magistrate_id) VALUES
 -- Case 1: Assault (Grievous Hurt)
 (1, 'MLC/2026/0142', NULL,        'Assault',
     'CB/1234/26', 'MC/COL/551/26', 'FMD/551/26',
     '2026-06-02 21:15', '2026-06-03 09:00', '2026-08-14',
     'Report Pending', 1, 1, 1, 2, 1, 1),

 -- Case 2: Homicide (Sharp Force Injury)
 (2, 'MLC/2026/0143', 'B/98/26',   'Homicide',
     'CB/1240/26', 'MC/COL/552/26', 'FMD/552/26',
     '2026-06-05 02:40', '2026-06-05 07:30', '2026-09-02',
     'Awaiting Lab', NULL, 1, 2, NULL, 1, 1),

 -- Case 3: Sexual Assault
 (3, 'MLC/2026/0144', NULL,        'Sexual Assault',
     'GP/0456/26', 'MC/GAM/210/26', 'FMD/210/26',
     '2026-06-10 18:00', '2026-06-11 10:15', NULL,
     'Under Examination', 5, 3, 4, NULL, 3, NULL),

 -- Case 4: Skeletal Remains
 (4, 'MLC/2026/0145', 'B/101/26',  'Skeletal Remains',
     'MT/0789/26', 'MC/MAT/077/26', 'FMD/077/26',
     '2026-05-20 00:00', '2026-06-01 11:00', NULL,
     'Awaiting Lab', 4, 4, 5, NULL, 4, 4),

 -- Case 5: Natural Death (Ischaemic Heart Disease)
 (5, 'MLC/2026/0146', 'B/102/26',  'Natural/Accidental Death',
     'KD/0321/26', 'MC/KAN/144/26', 'FMD/144/26',
     '2026-06-18 06:00', '2026-06-18 08:45', '2026-07-30',
     'Despatched', 6, 2, 3, NULL, 2, 2),

 -- Case 6: Assault (Motor Vehicle Accident / Severe Trauma)
 (6, 'MLC/2026/0147', NULL,        'Assault',
     'CB/1301/26', 'MC/COL/601/26', 'FMD/601/26',
     '2026-06-20 12:30', '2026-06-20 14:00', '2026-08-28',
     'Report Pending', 7, 1, 6, 2, 1, 1),

 -- Case 7: Sexual Assault (Forensic DNA Confirmed)
 (7, 'MLC/2026/0148', NULL,        'Sexual Assault',
     'GP/0512/26', 'MC/GAM/288/26', 'FMD/288/26',
     '2026-06-21 01:00', '2026-06-21 09:30', '2026-09-10',
     'Report Pending', 8, 3, 7, NULL, 3, 3),

 -- Case 8: Accidental Death (Drowning Accident)
 (8, 'MLC/2026/0149', 'B/115/26',  'Natural/Accidental Death',
     'KD/0402/26', 'MC/KAN/190/26', 'FMD/190/26',
     '2026-06-22 08:00', '2026-06-22 11:00', '2026-08-05',
     'Awaiting Lab', 3, 2, 3, NULL, 2, 2);

-- ------------------------------------------------------------
-- 8. CASE ASSIGNMENTS
-- ------------------------------------------------------------
INSERT INTO case_assignment (case_id, staff_id, role_in_case) VALUES
 (1, 2, 'Examining JMO'),
 (2, 1, 'Lead JMO (Postmortem)'),
 (2, 4, 'Assisting PG Trainee'),
 (3, 3, 'Examining JMO'),
 (4, 1, 'Supervising Senior JMO'),
 (4, 3, 'Examining JMO'),
 (5, 1, 'Lead JMO (Postmortem)'),
 (6, 2, 'Examining JMO'),
 (7, 3, 'Examining JMO'),
 (8, 1, 'Lead JMO (Postmortem)');

-- ------------------------------------------------------------
-- 9. INQUEST VERDICTS
-- ------------------------------------------------------------
INSERT INTO inquest_verdict (verdict_id, case_id, magistrate_id, verdict_text, verdict_date) VALUES
 (1, 2, 1, 'Death due to homicidal violence; case referred for further police investigation under Section 355 CPC.', '2026-06-20'),
 (2, 5, 2, 'Death due to natural causes (ischaemic heart disease); no further judicial action required.', '2026-06-25'),
 (3, 8, 2, 'Death due to asphyxia secondary to drowning (accidental drowning in Victoria Reservoir).', '2026-06-28');

-- ------------------------------------------------------------
-- 10. CASE EVENTS & SUBTYPES (8 Events)
-- ------------------------------------------------------------
INSERT INTO case_event (event_id, case_id, event_type, event_date, staff_id) VALUES
 (1, 1, 'Clinical Examination', '2026-06-03 10:30', 2),
 (2, 2, 'Postmortem',           '2026-06-05 09:00', 1),
 (3, 3, 'Clinical Examination', '2026-06-11 11:00', 3),
 (4, 4, 'Skeletal Examination', '2026-06-02 14:00', 1),
 (5, 5, 'Postmortem',           '2026-06-18 10:00', 1),
 (6, 6, 'Clinical Examination', '2026-06-20 15:00', 2),
 (7, 7, 'Clinical Examination', '2026-06-21 10:30', 3),
 (8, 8, 'Postmortem',           '2026-06-22 11:30', 1);

-- Clinical Examinations
INSERT INTO clinical_examination
 (event_id, history_given, place_of_exam, hospital_no, ward, bed_no,
  admission_date, discharge_date, consent_obtained, reason_for_referral,
  alcohol_smell_present, under_influence_alcohol, drugs_consumed, under_influence_drugs,
  investigations_ordered, referrals_made, other_opinions) VALUES
 (1, 'Alleges assaulted by three unknown persons with wooden poles near bus stand at approx. 9.00pm.',
     'FMD Clinic, Colombo North Teaching Hospital', 'H/12345', 'Surgical Ward 4', '14B',
     '2026-06-02', '2026-06-04', TRUE, 'Police referral for grievous hurt assessment',
     TRUE, 'Yes', 'Not tested', 'Not tested',
     'X-ray left forearm, CT brain', 'Orthopaedic referral', 'Injuries consistent with history given.'),

 (3, 'Alleges sexual assault by acquaintance at a private residence on the night of 10.06.2026.',
     'FMD Clinic, Gampaha District Hospital', 'H/55231', NULL, NULL,
     NULL, NULL, TRUE, 'Police referral for medico-legal examination following alleged sexual assault',
     FALSE, 'No', 'Not tested', 'Not tested',
     'STI screening, forensic swabs', 'Counselling referral', 'Findings consistent with alleged history.'),

 (6, 'Alleges hit by a speeding motorcycle while crossing road at pedestrian crossing.',
     'FMD Clinic, Colombo North Teaching Hospital', 'H/88412', 'Accident Service Ward 2', '08A',
     '2026-06-20', '2026-06-25', TRUE, 'Police referral for medico-legal report on road traffic accident injuries',
     FALSE, 'No', 'Not tested', 'Not tested',
     'CT Brain, X-ray pelvis and right leg', 'Neurosurgery & Orthopaedics', 'Grievous hurt sustained.'),

 (7, 'Alleges non-consensual sexual contact following social gathering.',
     'FMD Clinic, Gampaha District Hospital', 'H/56001', NULL, NULL,
     '2026-06-21', '2026-06-21', TRUE, 'Urgent forensic evaluation following sexual assault complaint',
     FALSE, 'No', 'No', 'No',
     'High vaginal swab, toxicological screen', 'Psychiatry & Counselling', 'Physical signs of recent trauma present.');

-- Sexual Assault Findings
INSERT INTO sexual_assault_finding
 (event_id, history_of_assault_given, vaginal_hymen_signs_present,
  anal_penetration_signs_present, inter_labial_penetration_signs_present, remarks) VALUES
 (3, 'Single episode of non-consensual vaginal penetration alleged, approx. 36 hours prior to examination.',
     TRUE, FALSE, TRUE, 'Recent hymenal tear noted at 6 o''clock position; forensic swabs taken and forwarded to Government Analyst.'),
 (7, 'Alleged forced intercourse approx. 8 hours prior to examination.',
     TRUE, FALSE, TRUE, 'Fresh mucosal lacerations at posterior commissure; swabs taken for DNA profiling.');

-- Postmortems
INSERT INTO postmortem
 (event_id, date_time_of_death, requested_by_name, requested_by_designation, district,
  place_of_examination, scene_description, external_exam_description,
  estimated_age, sex, height_cm, eyes_and_pupils, hair_description, teeth_condition,
  tongue_condition, primary_flaccidity, rigor_mortis, hypostasis, putrefaction,
  hands_nails_condition, cause_of_death, time_since_death, register_serial_no, conclusion) VALUES
 (2, '2026-06-05 01:00', 'W.A. Jayasekara', 'Sub Inspector, Colombo North Police', 'Colombo',
     'Colombo North Teaching Hospital Mortuary',
     'Body found in a drain along Kelani Valley Road, partially clothed.',
     'Multiple incised wounds to neck and chest; defence wounds on both forearms.',
     '30-35 years', 'M', 168.50, 'Both pupils fixed and dilated, corneas hazy',
     'Black, short, straight', 'Natural dentition, no dentures',
     'Dry, protruding slightly', 'Present, resolving', 'Fully established',
     'Fixed, purple-red, back of trunk and limbs', 'Early putrefactive changes on abdomen',
     'Defence wounds on both palms and forearms',
     'Haemorrhagic shock due to multiple incised wounds to neck and chest', '18-24 hours',
     '551/26', 'Death due to homicidal violence caused by a sharp-edged weapon.'),

 (5, '2026-06-18 04:30', 'R.D. Bandara', 'Inspector, Kandy Police', 'Kandy',
     'National Hospital Kandy Mortuary',
     'Found collapsed at home by family members; no signs of external violence reported.',
     'No external injuries. Old surgical scar right hypochondrium.',
     '60-65 years', 'M', 165.00, 'Both pupils mid-dilated, corneas clear',
     'Grey, thinning', 'Partial dentures upper jaw',
     'Pale, moist', 'Absent', 'Passing off',
     'Fixed, purple, dependent parts', 'Nil',
     'No injuries noted',
     'Ischaemic heart disease with acute myocardial infarction', '6-9 hours',
     '144/26', 'Death due to natural causes — acute myocardial infarction.'),

 (8, '2026-06-22 06:15', 'R.D. Bandara', 'Inspector, Kandy Police', 'Kandy',
     'National Hospital Kandy Mortuary',
     'Body recovered from Victoria Reservoir near Teldeniya by navy divers.',
     'Fine white froth at nostrils and mouth. Washerwoman hands and feet.',
     '45-50 years', 'M', 171.00, 'Pupils fixed, corneas clear',
     'Black mixed with grey', 'Natural dentition',
     'Indented by teeth', 'Absent', 'Established in lower limbs',
     'Pinkish-purple on anterior chest and face', 'Nil',
     'Silt under fingernails',
     'Asphyxia secondary to drowning', '4-6 hours',
     '190/26', 'Death due to accidental drowning; no marks of ante-mortem violence detected.');

-- Postmortem Organ Findings
INSERT INTO postmortem_organ_finding (event_id, organ_name, findings) VALUES
 (2, 'Heart', '280g, chambers empty, coronary arteries patent, no gross pathology.'),
 (2, 'Lungs', 'Right 420g / Left 390g, congested, cut surface reveals frothy fluid.'),
 (2, 'Liver', '1450g, pale, cut surface unremarkable.'),
 (5, 'Heart', '410g, left ventricular wall hypertrophied, LAD shows 80% stenosis with recent thrombus.'),
 (5, 'Lungs', 'Right 480g / Left 460g, pulmonary oedema noted bilaterally.'),
 (5, 'Kidneys', 'Right 140g / Left 145g, early nephrosclerotic changes.'),
 (8, 'Lungs', 'Right 620g / Left 580g, voluminous, ballooned, overlapping heart, cut surface exudes abundant froth.'),
 (8, 'Stomach', 'Contains 250ml watery fluid with fine silt particles.');

-- Body Identifiers
INSERT INTO body_identifier (event_id, name, address, relationship_to_deceased) VALUES
 (2, 'S.M. Kumara', '14 Kelani Valley Road, Colombo 14', 'Brother'),
 (5, 'P.G. Somawathi', '23 Temple Lane, Matale', 'Spouse'),
 (8, 'S. Rathnayake', '78 Peradeniya Road, Kandy', 'Son');

-- Skeletal Examination
INSERT INTO skeletal_examination
 (event_id, history, specimen_no, place_found, seal_status, wrapping_description,
  human_remains_present, animal_remains_present, state_of_putrefaction, skeletonized, mummified,
  min_no_individuals, mni_reasons, gender_conclusion, age_conclusion, stature_estimate,
  stature_method, time_since_death, cause_of_death_opinion, special_techniques_recommended,
  supervised_by_staff_id) VALUES
 (4, 'Skeletal remains recovered by police during routine river-bank search, submitted for identification.',
     'SK/2026/014', 'Mahaweli riverbank, near Katugastota bridge, Matale District',
     'Intact', 'Remains wrapped in a blue polythene sack, tied with nylon rope',
     TRUE, FALSE, 'Fully skeletonized, no soft tissue remaining', TRUE, FALSE,
     1, 'Single set of long bones and skull recovered, no duplicate elements found',
     'Probable male (pelvic and skull morphology)', '25-35 years (based on epiphyseal fusion and pubic symphysis)',
     '170 cm (approx.)', 'Trotter & Gleser regression formula (femur length)',
     'Estimated 6-12 months based on degree of weathering',
     'Cause of death cannot be determined from skeletal remains alone; no evidence of peri-mortem trauma detected.',
     'DNA profiling recommended for identification; forwarded to Government Analyst.',
     1);

INSERT INTO skeletal_item (event_id, item_category, description, serial_number, quantity) VALUES
 (4, 'Human Remain', 'Complete skull with mandible', 'SK/2026/014-01', 1),
 (4, 'Human Remain', 'Long bones - both femurs, tibiae, fibulae, humeri, radii, ulnae', 'SK/2026/014-02', 12),
 (4, 'Human Remain', 'Rib cage fragments and vertebrae', 'SK/2026/014-03', 1),
 (4, 'Other Content', 'Remnants of blue polythene sack', 'SK/2026/014-W1', 1),
 (4, 'Other Content', 'Nylon rope fragment', 'SK/2026/014-W2', 1);

-- ------------------------------------------------------------
-- 11. GRIEVOUS HURT LOOKUP & INJURIES
-- ------------------------------------------------------------
INSERT INTO grievous_hurt_type (clause_code, description) VALUES
 ('a', 'Emasculation'),
 ('b', 'Permanent privation of sight of either eye'),
 ('c', 'Permanent privation of hearing of either ear'),
 ('d', 'Privation of any member or joint'),
 ('e', 'Destruction or permanent impairment of the powers of any member or joint'),
 ('f', 'Permanent disfiguration of the head or face'),
 ('g', 'Fracture or dislocation of a bone'),
 ('h', 'Any hurt which endangers life or causes severe bodily pain for 20 days'),
 ('i', 'Any hurt causing permanent disability');

INSERT INTO injury
 (event_id, nature, size_shape, site, causative_weapon, body_cavity, category_of_hurt,
  endangers_life, timing_relative_to_death, grievous_hurt_clause_code, explanatory_remarks) VALUES
 (1, 'Contusion', '5cm x 3cm, oval, bluish', 'Left forearm, dorsal aspect', 'Blunt weapon (wooden pole)', 'External', 'Non-grievous', FALSE, 'Not Applicable', NULL, NULL),
 (1, 'Fracture', 'Simple transverse fracture', 'Left radius, mid-shaft', 'Blunt weapon (wooden pole)', 'Internal', 'Grievous', FALSE, 'Not Applicable', 'g', 'Confirmed on X-ray; fracture of a bone as per clause (g).'),
 (1, 'Laceration', '3cm x 0.5cm x 0.5cm', 'Scalp, left parietal region', 'Blunt weapon', 'External', 'Non-grievous', FALSE, 'Not Applicable', NULL, NULL),

 (2, 'Incised wound', '8cm x 2cm x 4cm deep', 'Neck, anterior aspect, transecting right carotid artery', 'Sharp-edged weapon (knife)', 'External', 'Fatal in ordinary course of nature', TRUE, 'Ante-mortem', NULL, 'Fatal injury; cause of death.'),
 (2, 'Incised wound', '6cm x 1.5cm x 3cm deep', 'Chest, left side, penetrating pleural cavity', 'Sharp-edged weapon (knife)', 'Internal', 'Fatal in ordinary course of nature', TRUE, 'Ante-mortem', NULL, 'Contributory fatal injury.'),
 (2, 'Incised wound (defence)', '4cm x 1cm x 1cm deep', 'Left palm', 'Sharp-edged weapon (knife)', 'External', 'Grievous', FALSE, 'Ante-mortem', 'h', 'Classic defence wound.'),

 (6, 'Comminuted Fracture', 'Displaced fracture right tibia/fibula', 'Right leg mid-shaft', 'Impact with vehicle bumper', 'Internal', 'Grievous', TRUE, 'Not Applicable', 'g', 'Comminuted fracture requiring surgical fixation.'),
 (6, 'Subdural haematoma', '30ml volume', 'Right parietal lobe', 'Head impact with pavement', 'Internal', 'Grievous', TRUE, 'Not Applicable', 'h', 'Endangers life due to intracranial pressure.');

-- ------------------------------------------------------------
-- 12. SPECIMENS & LABORATORY CHAIN
-- ------------------------------------------------------------
INSERT INTO specimen (event_id, specimen_type, specimen_label, collection_date, seal_no, chain_of_custody_status, production_number) VALUES
 (1, 'Blood sample (alcohol analysis)', 'A', '2026-06-03 10:45', 'SEAL-3301', 'Sent to Government Analyst', 'PN/2026/551-1'),
 (2, 'Blood sample', 'A', '2026-06-05 09:30', 'SEAL-3302', 'Sent to Government Analyst', 'PN/2026/552-1'),
 (2, 'Viscera (stomach, liver, kidney)', 'B', '2026-06-05 09:45', 'SEAL-3303', 'Sent to Government Analyst', 'PN/2026/552-2'),
 (2, 'Weapon swab', 'C', '2026-06-05 10:00', 'SEAL-3304', 'Sent to Government Analyst', 'PN/2026/552-3'),
 (3, 'Forensic vaginal & anal swabs', 'A', '2026-06-11 11:30', 'SEAL-3305', 'Sent to Government Analyst', 'PN/2026/210-1'),
 (4, 'Femur sample (for DNA)', 'A', '2026-06-02 15:00', 'SEAL-3306', 'Sent to Medical Research Institute (MRI)', 'PN/2026/077-1'),
 (5, 'Coronary artery + myocardium sample', 'A', '2026-06-18 10:30', 'SEAL-3307', 'Sent to Histopathology', 'PN/2026/144-1'),
 (7, 'Vaginal swab & blood sample (DNA)', 'A', '2026-06-21 11:00', 'SEAL-3308', 'Sent to Government Analyst', 'PN/2026/288-1'),
 (8, 'Drowning fluid & lung tissue', 'A', '2026-06-22 12:00', 'SEAL-3309', 'Sent to Histopathology', 'PN/2026/190-1');

INSERT INTO lab_request
 (lab_request_id, specimen_id, lab_name, requested_by_staff_id, test_requested, poisons_suspected,
  macroscopic_appearances, special_procedure_request, date_sent, urgency, request_purpose,
  date_accepted, accepted_by_name, receiving_refno) VALUES
 (1, 1, 'Government Analyst', 2, 'Blood alcohol concentration', NULL, NULL, NULL,
     '2026-06-03 11:00', 'Routine', 'Judicial', '2026-06-03 15:20', 'Mr. D.S. Karunaratne', 'GA/2026/2211'),

 (2, 2, 'Government Analyst', 1, 'Toxicological screening - full panel', 'Organophosphates, common poisons', NULL, NULL,
     '2026-06-05 12:00', 'Urgent', 'Judicial', '2026-06-05 16:40', 'Mr. D.S. Karunaratne', 'GA/2026/2212'),

 (3, 3, 'Histopathology', 1, 'Histopathological examination of viscera', NULL,
     'Liver pale, kidneys congested', 'Special stains if indicated', '2026-06-05 12:15', 'Routine', 'Judicial',
     '2026-06-06 09:00', 'Ms. W.A. Ranasinghe', 'HP/2026/0876'),

 (4, 4, 'Government Analyst', 1, 'DNA / blood grouping comparison of weapon swab', NULL, NULL, NULL,
     '2026-06-05 12:30', 'Urgent', 'Judicial', '2026-06-05 17:00', 'Mr. D.S. Karunaratne', 'GA/2026/2213'),

 (5, 5, 'Government Analyst', 3, 'Forensic swab analysis (seminal fluid / DNA)', NULL, NULL, NULL,
     '2026-06-11 12:00', 'Urgent', 'Judicial', '2026-06-11 17:30', 'Mr. D.S. Karunaratne', 'GA/2026/2214'),

 (6, 6, 'Medical Research Institute (MRI)', 1, 'DNA profiling for identification', NULL, NULL,
     'Full nuclear + mitochondrial DNA profile requested', '2026-06-02 16:00', 'Routine', 'Judicial',
     '2026-06-04 10:00', 'Dr. N.J. Abeywardena', 'MRI/2026/0033'),

 (7, 7, 'Histopathology', 1, 'Cardiac histopathology', NULL, 'Myocardium pale, focal areas of pallor',
     NULL, '2026-06-18 11:00', 'Routine', 'Judicial', '2026-06-18 14:30', 'Ms. W.A. Ranasinghe', 'HP/2026/0891'),

 (8, 8, 'Government Analyst', 3, 'DNA profiling & STR matching', NULL, NULL, NULL,
     '2026-06-21 12:00', 'Urgent', 'Judicial', '2026-06-21 16:00', 'Mr. D.S. Karunaratne', 'GA/2026/2280'),

 (9, 9, 'Histopathology', 1, 'Diatom test & lung histology for drowning', NULL, 'Oedematous lungs with subpleural haemorrhages',
     'Diatom extraction from lung & kidney', '2026-06-22 13:00', 'Routine', 'Judicial', '2026-06-22 15:30', 'Ms. W.A. Ranasinghe', 'HP/2026/0920');

INSERT INTO lab_request_organ_tissue (lab_request_id, organ_name, no_of_tissue) VALUES
 (3, 'Liver', 2),
 (3, 'Kidney', 2),
 (3, 'Stomach contents', 1),
 (7, 'Heart (myocardium)', 3),
 (7, 'Coronary artery segment', 1),
 (9, 'Right lung peripheral tissue', 2),
 (9, 'Left lung peripheral tissue', 2);

INSERT INTO lab_result
 (lab_result_id, lab_request_id, laboratory_no, result_date, received_by, lab_notes, findings, reported_by, checked_by, sent_on_date) VALUES
 (1, 1, 'GA-LAB/9021', '2026-06-10 10:00', 'Mr. D.S. Karunaratne',
     'Sample received in good condition, sealed.',
     'Blood alcohol concentration: 142 mg/100ml, consistent with recent alcohol consumption.',
     'Mr. D.S. Karunaratne', 'Dr. Government Analyst (Toxicology)', '2026-06-11 09:00'),

 (2, 2, 'GA-LAB/9022', '2026-06-15 10:00', 'Mr. D.S. Karunaratne',
     'Viscera preserved in saturated saline, no leakage.',
     'No common poisons detected. Ethanol: negative.',
     'Mr. D.S. Karunaratne', 'Dr. Government Analyst (Toxicology)', '2026-06-16 09:00'),

 (3, 4, 'GA-LAB/9023', '2026-06-16 10:00', 'Mr. D.S. Karunaratne',
     'Weapon swab intact on receipt.',
     'DNA profile obtained from weapon swab matches reference sample from suspect (99.99% probability).',
     'Mr. D.S. Karunaratne', 'Dr. Government Analyst (Serology)', '2026-06-17 09:00'),

 (4, 5, 'GA-LAB/9024', '2026-06-18 10:00', 'Mr. D.S. Karunaratne',
     'Swabs received frozen, chain of custody intact.',
     'Seminal fluid detected on vaginal swab; DNA profiling in progress, interim report issued.',
     'Mr. D.S. Karunaratne', 'Dr. Government Analyst (Serology)', '2026-06-19 09:00'),

 (5, 8, 'GA-LAB/9035', '2026-06-25 11:00', 'Mr. D.S. Karunaratne',
     'Swabs sealed in tamper-evident container.',
     'Single male DNA profile isolated from vaginal swab matches suspect reference (15 STR loci matched).',
     'Mr. D.S. Karunaratne', 'Dr. Government Analyst (Serology)', '2026-06-26 10:00');

-- ------------------------------------------------------------
-- 13. REPORTS, AUDIT LOGS, NOTIFICATIONS
-- ------------------------------------------------------------
INSERT INTO report
 (report_id, serial_no, case_id, event_id, report_type, prepared_by_staff_id,
  date_issued, date_despatched, status, file_path) VALUES
 (1, 'MLR/551/26', 1, 1, 'MLR', 2, '2026-06-04 12:00', NULL, 'Signed', '/reports/mlr_551_26.pdf'),
 (2, 'PMR/552/26', 2, 2, 'PMR', 1, '2026-06-06 09:00', NULL, 'Draft', NULL),
 (3, 'MLR/210/26', 3, 3, 'MLR', 3, '2026-06-12 14:00', NULL, 'Draft', NULL),
 (4, 'SK/077/26',  4, 4, 'Court Report', 1, '2026-06-05 11:00', NULL, 'Draft', NULL),
 (5, 'PMR/144/26', 5, 5, 'PMR', 1, '2026-06-19 10:00', '2026-06-20 09:00', 'Despatched', '/reports/pmr_144_26.pdf'),
 (6, 'MLR/601/26', 6, 6, 'MLR', 2, '2026-06-22 16:00', NULL, 'Signed', '/reports/mlr_601_26.pdf'),
 (7, 'MLR/288/26', 7, 7, 'MLR', 3, '2026-06-26 14:00', NULL, 'Signed', '/reports/mlr_288_26.pdf'),
 (8, 'PMR/190/26', 8, 8, 'PMR', 1, '2026-06-23 10:00', NULL, 'Draft', NULL);

INSERT INTO audit_log (user_id, table_name, record_id, action_type, old_values, new_values, ip_address) VALUES
 (2, 'case_master', 1, 'INSERT', NULL, '{"case_number":"MLC/2026/0142","status":"Under Examination"}', '192.168.1.10'),
 (1, 'postmortem',  2, 'INSERT', NULL, '{"cause_of_death":"Haemorrhagic shock..."}', '192.168.1.11'),
 (1, 'case_master', 2, 'UPDATE', '{"status":"Under Examination"}', '{"status":"Awaiting Lab"}', '192.168.1.11'),
 (6, 'report',      1, 'UPDATE', '{"status":"Draft"}', '{"status":"Signed"}', '192.168.1.15'),
 (3, 'case_master', 7, 'INSERT', NULL, '{"case_number":"MLC/2026/0148","status":"Under Examination"}', '192.168.1.14');

INSERT INTO notification (user_id, title, message_text, is_read) VALUES
 (2, 'Lab result received', 'Government Analyst report for case MLC/2026/0142 (specimen A) has been received.', TRUE),
 (1, 'New case assigned', 'You have been assigned as lead JMO for case MLC/2026/0143 (Homicide).', FALSE),
 (1, 'Lab request pending', 'Histopathology report for case MLC/2026/0143 is still pending (7 days elapsed).', FALSE),
 (3, 'Report due', 'MLR for case MLC/2026/0144 is pending finalisation before the trial date.', FALSE),
 (3, 'DNA match result', 'GA DNA profile matching confirmed for sexual assault case MLC/2026/0148.', FALSE);

-- ------------------------------------------------------------
-- 14. RESET AUTO-INCREMENT SEQUENCES
-- ------------------------------------------------------------
SELECT setval('role_role_id_seq', (SELECT MAX(role_id) FROM role));
SELECT setval('staff_staff_id_seq', (SELECT MAX(staff_id) FROM staff));
SELECT setval('app_user_user_id_seq', (SELECT MAX(user_id) FROM app_user));
SELECT setval('patient_patient_id_seq', (SELECT MAX(patient_id) FROM patient));
SELECT setval('police_station_police_station_id_seq', (SELECT MAX(police_station_id) FROM police_station));
SELECT setval('investigating_officer_officer_id_seq', (SELECT MAX(officer_id) FROM investigating_officer));
SELECT setval('court_court_id_seq', (SELECT MAX(court_id) FROM court));
SELECT setval('magistrate_magistrate_id_seq', (SELECT MAX(magistrate_id) FROM magistrate));
SELECT setval('case_master_case_id_seq', (SELECT MAX(case_id) FROM case_master));
SELECT setval('inquest_verdict_verdict_id_seq', (SELECT MAX(verdict_id) FROM inquest_verdict));
SELECT setval('case_event_event_id_seq', (SELECT MAX(event_id) FROM case_event));
SELECT setval('lab_request_lab_request_id_seq', (SELECT MAX(lab_request_id) FROM lab_request));
SELECT setval('lab_result_lab_result_id_seq', (SELECT MAX(lab_result_id) FROM lab_result));
SELECT setval('report_report_id_seq', (SELECT MAX(report_id) FROM report));
