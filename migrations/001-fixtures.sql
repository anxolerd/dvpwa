INSERT INTO users (
  first_name,
  middle_name,
  last_name,
  username,
  pwd_hash,
  is_admin
)
VALUES
  ('Super', NULL, 'Admin', 'superadmin', md5('superadmin'), TRUE),
  ('John', 'William', 'Doe', 'j.doe', md5('password'), FALSE),
  ('Stephen', NULL, 'King', 's.king', md5('password'), FALSE),
  ('Peter', NULL, 'Parker', 'p.parker', md5('spidey'), FALSE);

INSERT INTO students (name) VALUES
  ('Chuck'), ('James'), ('Thor'), ('Clint'),
  ('Richie'), ('Bill'), ('Ben'), ('Eddie');

INSERT INTO courses (title, description) VALUES
  ('Math', '2+2 = 5'),
  ('Grammar', 'Wi learn haw tu write korektli'),
  ('Physics', 'E=mc^2');

INSERT INTO marks(student_id, course_id, points) VALUES
  (1, 1, 4), (1, 1, 5), (1, 1, 3), (1, 1, 4),
  (1, 2, 2), (1, 2, 3), (1, 3, 5), (1, 3, 5);
