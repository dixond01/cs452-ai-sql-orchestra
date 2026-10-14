INSERT INTO conductor (conductor_id, name, email) VALUES
(1, 'Maria Alvarez', 'malvarez@valleyyouthmusic.org'),
(2, 'David Chen', 'dchen@valleyyouthmusic.org'),
(3, 'Susan Whitaker', 'swhitaker@valleyyouthmusic.org'),
(4, 'James Okafor', 'jokafor@valleyyouthmusic.org');

INSERT INTO ensemble (ensemble_id, name, conductor_id, rehearsal_day, start_time, end_time, room) VALUES
(1, 'Symphony Orchestra', 1, 'Saturday', '09:00', '11:30', 'Concert Hall'),
(2, 'Wind Ensemble', 2, 'Saturday', '10:00', '12:00', 'Band Room'),
(3, 'String Quartet', 3, 'Tuesday', '16:00', '17:00', 'Room 102'),
(4, 'Jazz Band', 2, 'Thursday', '18:00', '19:30', 'Band Room'),
(5, 'Chamber Strings', 1, 'Tuesday', '16:30', '18:00', 'Room 204');

INSERT INTO player (player_id, first_name, last_name, birth_date, school_grade) VALUES
(1, 'Emma', 'Larsen', '2010-03-14', 10),
(2, 'Noah', 'Larsen', '2012-07-02', 8),
(3, 'Olivia', 'Kim', '2009-11-23', 11),
(4, 'Liam', 'Patel', '2011-01-30', 9),
(5, 'Ava', 'Johnson', '2010-09-05', 10),
(6, 'Ethan', 'Nguyen', '2008-12-12', 12),
(7, 'Sophia', 'Martinez', '2011-06-18', 9),
(8, 'Mason', 'Clark', '2012-02-25', 8),
(9, 'Isabella', 'Rossi', '2009-04-09', 11),
(10, 'Lucas', 'Brown', '2010-10-31', 10),
(11, 'Mia', 'Thompson', '2013-05-20', 7),
(12, 'Benjamin', 'Lee', '2008-08-08', 12),
(13, 'Charlotte', 'Davis', '2011-12-01', 9),
(14, 'Henry', 'Wilson', '2012-09-15', 8),
(15, 'Amelia', 'Garcia', '2009-02-17', 11),
(16, 'Jack', 'Olsen', '2013-03-03', 7);

INSERT INTO parent (parent_id, name, phone, email) VALUES
(1, 'Karen Larsen', '801-555-0101', 'karen.larsen@example.com'),
(2, 'Erik Larsen', '801-555-0102', 'erik.larsen@example.com'),
(3, 'Min-jung Kim', '801-555-0103', 'mjkim@example.com'),
(4, 'Raj Patel', '801-555-0104', 'raj.patel@example.com'),
(5, 'Denise Johnson', '801-555-0105', 'denise.j@example.com'),
(6, 'Thu Nguyen', '801-555-0106', 'thu.nguyen@example.com'),
(7, 'Carlos Martinez', '801-555-0107', NULL),
(8, 'Rachel Clark', '801-555-0108', 'rachel.clark@example.com'),
(9, 'Marco Rossi', '801-555-0109', 'marco.rossi@example.com'),
(10, 'Angela Brown', '801-555-0110', 'angela.brown@example.com'),
(11, 'Greg Thompson', '801-555-0111', 'greg.thompson@example.com'),
(12, 'Laura Davis', '801-555-0112', 'laura.davis@example.com'),
(13, 'Paul Wilson', '801-555-0113', 'paul.wilson@example.com'),
(14, 'Elena Garcia', '801-555-0114', 'elena.garcia@example.com'),
(15, 'Tom Olsen', NULL, 'tom.olsen@example.com');

INSERT INTO player_parent (player_id, parent_id) VALUES
(1, 1),
(1, 2),
(2, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10),
(11, 11),
(13, 12),
(14, 12),
(14, 13),
(15, 14),
(16, 15);

INSERT INTO section (section_id, name, instrument, family) VALUES
(1, 'Violin I', 'Violin', 'strings'),
(2, 'Violin II', 'Violin', 'strings'),
(3, 'Viola', 'Viola', 'strings'),
(4, 'Cello', 'Cello', 'strings'),
(5, 'Double Bass', 'Double Bass', 'strings'),
(6, 'Flute', 'Flute', 'woodwind'),
(7, 'Clarinet', 'Clarinet', 'woodwind'),
(8, 'Alto Saxophone', 'Saxophone', 'woodwind'),
(9, 'Trumpet', 'Trumpet', 'brass'),
(10, 'Trombone', 'Trombone', 'brass'),
(11, 'French Horn', 'French Horn', 'brass'),
(12, 'Percussion', 'Percussion', 'percussion'),
(13, 'Oboe', 'Oboe', 'woodwind');

INSERT INTO membership (ensemble_id, player_id, section_id, chair_number) VALUES
-- Symphony Orchestra
(1, 3, 1, 1),
(1, 1, 1, 2),
(1, 9, 1, 3),
(1, 5, 2, 1),
(1, 11, 2, 2),
(1, 4, 3, 1),
(1, 6, 4, 1),
(1, 2, 4, 2),
(1, 12, 5, 1),
(1, 15, 11, 1),
-- Wind Ensemble
(2, 7, 6, 1),
(2, 13, 6, 2),
(2, 8, 7, 1),
(2, 10, 9, 1),
(2, 14, 10, 1),
-- String Quartet
(3, 3, 1, 1),
(3, 5, 2, 1),
(3, 4, 3, 1),
(3, 6, 4, 1),
-- Jazz Band
(4, 10, 9, 1),
(4, 15, 9, 2),
(4, 14, 10, 1),
(4, 8, 8, 1),
(4, 7, 8, 2),
(4, 12, 5, 1),
(4, 1, 12, 1),
-- Chamber Strings
(5, 1, 1, 1),
(5, 9, 1, 2),
(5, 11, 2, 1),
(5, 13, 3, 1),
(5, 2, 4, 1),
(5, 12, 5, 1);
