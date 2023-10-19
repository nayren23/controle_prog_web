-- Créaton de la DB et de l'utilisateur :

Create schema agence;
-- Table locataire
CREATE TABLE agence.locataire (
	id serial NOT NULL,
    mail varchar NOT NULL,
	mdp varchar NULL,
    nom varchar NOT NULL,
    prenom varchar NOT NULL
	
);

ALTER TABLE agence.locataire ADD CONSTRAINT locataire_pk PRIMARY KEY (id);

-- Table token
CREATE TABLE agence.token (
	id serial NOT NULL,
    nom varchar NOT NULL
	
);

ALTER TABLE agence.token ADD CONSTRAINT token_pk PRIMARY KEY (id);

-- Table appartement
CREATE TABLE agence.appartement (
	id serial NOT NULL,
    adresse varchar NOT NULL

);

ALTER TABLE agence.appartement ADD CONSTRAINT appartement_pk PRIMARY KEY (id);

-- Table quittance
CREATE TABLE agence.quittance (
	id serial NOT NULL,
    date varchar NOT NULL,
    id_appartement int NOT NULL,
	id_locataire int NOT NULL,
	CONSTRAINT agence_appartement_fk_2 FOREIGN KEY (id_appartement) REFERENCES agence.appartement(id),
	CONSTRAINT agence_locataire_fk_2 FOREIGN KEY (id_locataire) REFERENCES agence.locataire(id)
);

-- Table Jointures locataire / appartement
CREATE TABLE agence.appartement_locataire (
	id_appartement int NOT NULL,
	id_locataire int NOT NULL,
    date_arrive varchar,
    date_depart varchar,
	CONSTRAINT agence_appartement_fk FOREIGN KEY (id_appartement) REFERENCES agence.appartement(id),
	CONSTRAINT agence_locataire_fk FOREIGN KEY (id_locataire) REFERENCES agence.locataire(id)
);


-- Populate table books
INSERT INTO agence.appartement (id,adresse) VALUES
	 (1,'20 avenue de la rose '),
	 (2,'30 rue de la bourde ' ),
	 (3,'45 boulevard du joker');
 

INSERT INTO agence.locataire (nom, prenom, mail, mdp) VALUES ('greg', 'greg', 'greg@gmail.com', '$2a$04$h5QBtXdDUIRscaQ9j8Ek4.kxLqiZgvsNxX8bR3VA1JKO7MNtkIX9O') RETURNING id;