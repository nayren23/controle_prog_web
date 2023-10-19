-- connect to postgres : psql -h database-etudiants -d rchouchane

-- Création de la DB et de l'utilisateur :
-- # sudo -i -u postgres
-- # createuser -d -P books_manager
-- # createdb -O books_manager books_manager
-- # exit
-- 
-- Ensuite, utiliser DBeaver pour créer tables (ou psql en ligne de commandes)

--DROP TABLE IF EXISTS public.books CASCADE;
--DROP TABLE IF EXISTS public.users CASCADE;

-- Table Books
CREATE TABLE public.books (
    id serial NOT NULL,
    title varchar NOT NULL,
    author varchar NULL,
    editor varchar NULL,
    date_publication date NULL,
    summary text NULL,
    cover jsonb NULL
);

ALTER TABLE public.books ADD CONSTRAINT books_pk PRIMARY KEY (id);

-- Table Users
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY NOT NULL,
    name varchar NOT NULL,
    firstname varchar NULL,
    email varchar NULL,
    identifiant varchar NULL,
    mdp varchar NULL
);

-- Table Jointures Books / Users
CREATE TABLE public.books_users (
    id_book int NOT NULL,
    id_user int NOT NULL,
    CONSTRAINT books_users_fk FOREIGN KEY (id_book) REFERENCES public.books(id),
    CONSTRAINT books_users_fk_1 FOREIGN KEY (id_user) REFERENCES public.users(id)
);


-- Populate table books
INSERT INTO public.books ( title,author,editor,date_publication,summary,cover) VALUES
     ('Les Misérables','Victor Hugo','Hachette',NULL,'Test 2',NULL),
     ('le horla','Maupassant','Gallimard','1889-12-01','Test',NULL),
     ('Là où les zeubs les ecrevisses','Delia Owens','Seuil','2021-08-01','Long texte','{"uri": "/img/cover_owens.jpg", "type": "jpeg", "caption": "Légende de l''image", "description": "Une image de couverture"}');


--Users

INSERT INTO users (  name, firstname, email)
VALUES ( 'Dupont', 'Jean', 'jean.dupont@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Martin', 'Marie', 'marie.martin@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Lefebvre', 'Pierre', 'pierre.lefebvre@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Dubois', 'Sophie', 'sophie.dubois@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Leroy', 'Paul', 'paul.leroy@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Tremblay', 'Isabelle', 'isabelle.tremblay@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Gagnon', 'Michel', 'michel.gagnon@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Roy', 'Catherine', 'catherine.roy@example.com');

INSERT INTO users (  name, firstname, email)
VALUES ('Morin', 'Luc', 'luc.morin@example.com');