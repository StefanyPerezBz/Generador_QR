-- Tabla para el administrador (solo 1 registro)
create table admin (
  id uuid primary key default gen_random_uuid(),
  username text unique not null,
  password text not null
);

-- Inserta el admin por defecto (cambia por tu usuario real)
insert into admin (username, password)
values ('admin', crypt('admin123', gen_salt('bf')));

-- Tabla para los documentos multimedia
create table media_documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  media_url text not null,
  qr_url text,
  media_type text check (media_type in ('image', 'video', 'audio')),
  created_at timestamp default now()
);
