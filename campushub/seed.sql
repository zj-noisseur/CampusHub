-- 1. Insert Institutions
INSERT INTO institution (university_name, state) 
VALUES ('Multimedia University Melaka', 'Melaka');

INSERT INTO institution (university_name, state) 
VALUES ('Multimedia University Cyberjaya', 'Selangor');

-- 2. Insert Clubs
-- Melaka Sports & Martial Arts
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Aerobic Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Archery Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Badminton Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Basketball Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Chess Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Fencing Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Flex & Fitness Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Football Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Rugby Club', '@mmuhornbills', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Netball Club', '@mmumelakanetball', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'OUTRECS', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Road Runners Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Squash Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Swimming Club', '@mmu_swimming_club', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Table Tennis Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Tennis Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Volleyball Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Water Sports Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Softball Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'E-Games Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Aikido Club', '@mmu.aikido', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Judo Club', '@mmu_judo_club', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Karate Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Silat Cekak Pusaka Hanafi Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Taekwondo Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Wing Chun Club', '@wingchundoclubmmu', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Wushu Club', NULL, NULL);

-- Melaka Non-sports
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Accounting Club', '@mmuac.malacca', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Arabic Culture Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Animals And Pets Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Buddhist Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Business Society', '@mmu_businesssociety', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Chinese Language Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Chinese Orchestra Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Choir Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Editorial Squad', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Engineering Society', '@mmu_engineeringsociety', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Golden Key Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Indian Cultural Society', '@icsmmumalacca', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Institusi Usrah', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'International Student Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'IT Society', '@itsocietymmumelaka', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Korean Cultural Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Malaysian Red Crescent Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'MMU Christian Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'MMU IEM', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'MMU IET', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'MMusic Society', '@mmusic_society_melaka_campus', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Multimedia Arts & Theater Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Multimedia Initiative Language of English', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Multimedia University Law Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Robotics Club', '@mmuroboticsclub', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Sekretariat Rakan Muda', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'St. John Ambulance', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, "Voice's Debating Society", NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Student College Committee', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (1, 'Student Representative Council', '@srcmmu_melaka', NULL);

-- Cyberjaya Sports & Societies
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Rugby Club', '@mmuhornbillsreds', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Basketball Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Netball Club', '@mmunetbees', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Badminton Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Volleyball Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'OARS', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Swimming Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Chess Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Soccer Club', '@mmufccyber', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Archery Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Water Sports Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'MMU E-Sport Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Silat Cekak Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Aikido Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Buddhist Society Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Chinese Language Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Christian Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Communicators For Life (CFL)', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Creative Multimedia Club (CMC)', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Cyberjaya Accounting Club (CAC)', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'D.I.C.E', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Deejay Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Editorial Squad Cyberjaya', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Engineering Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Faculty of Management Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Cinematics Arts Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Indian Cultural Society', '@icsmmucyber', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'International Student Society (ISS)', '@iss_mmucyber', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'IT Society', '@itsocietymmu', NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Japanese Cultural Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Korean Language Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'MMU Game Developers Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Rentak Dance Club', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Sekretariat Rakan Muda (SRM)', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Sekretariat Sekolah@MMU', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Sekretariat Rukun Negara', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Theatre at Multimedia University (TAMU)', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'University Peer Group (UPG)', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Usrah Institution', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Voices Debating Society', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Enactus MMU', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Student College Committee', NULL, NULL);
INSERT INTO club (institution_id, name, ig_handle, valid_till) VALUES (2, 'Student Representative Council', '@srcmmu_cyber', NULL);