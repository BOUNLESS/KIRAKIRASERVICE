CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    rol VARCHAR(30) NOT NULL
);