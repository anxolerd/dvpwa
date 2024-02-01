INSERT INTO users (
  first_name,
  middle_name,
  last_name,
  username,
  pwd_hash,
  is_admin
)
VALUES
  ('Super', NULL, 'Admin', 'superadmin', crypt('superadmin', gen_salt('bf', 8)), TRUE),
  ('John', 'William', 'Doe', 'j.doe', crypt('password', gen_salt('bf', 8)), FALSE),
  ('Stephen', NULL, 'King', 's.king', crypt('password', gen_salt('bf', 8)), FALSE),
  ('Peter', NULL, 'Parker', 'p.parker', crypt('spidey', gen_salt('bf', 8)), FALSE);

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
