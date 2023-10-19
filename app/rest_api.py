#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import json
import psycopg2
import requests
from contextlib import closing
from config import config
import connect_pg
import bcrypt


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/books/get', methods=['GET','POST'])
def get_books():
    """ Return all books in JSON format """
    query = "select * from books order by id asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    for row in rows:
        returnStatement.append(get_book_statement(row))
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@app.route('/books/get/<bookId>', methods=['GET','POST'])
def get_one_book(bookId):
    """ Return book bookId in JSON format """
    query = "select * from books where id=%(bookId)s order by id asc" % {'bookId':bookId}
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if len(rows) > 0:
        returnStatement = get_book_statement(rows[0])
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@app.route('/books/search/<title>', methods=['GET','POST'])
def search_books(title):
    """ Return list of books which title matche with %<title>% """
    # /!\ we escape % with another % => %title% => %%title%%
    query = "select * from books where title like '%%%(title)s%%' order by title asc" % {'title':title}
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    for row in rows:
        returnStatement.append(get_book_statement(row))
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)
    
    
def get_book_statement(row) :
    """ Book array statement """
    return {
        'id':row[0],
        'title':row[1],
        'author':row[2],
        'editor':row[3],
        'editPub':row[4],
        'summary':row[5],
        'cover':row[6]
    }
    

@app.route('/users/get', methods=['GET','POST'])
def get_users():
    """ Return all users in JSON format """
    query = "select * from users order by id asc"
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = []
    for row in rows:
        returnStatement.append(get_users_statement(row))
    
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@app.route('/users/get/<userId>', methods=['GET','POST'])
def get_one_user(userId):
    """ Return user userId in JSON format """
    query = "select * from users where id=%(userId)s order by id asc" % {'userId':userId}
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if len(rows) > 0:
        returnStatement = get_users_statement(rows[0])
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@app.route('/')
def hello():
    return "test"



def get_users_statement(row) :
    """ users array statement """
    return {
        'id':row[0],
        'name   ':row[1],
        'firstname':row[2],
        'email' : row[3]
    }

@app.route('/books/add', methods=['POST'])
def add_book():
    """ Add a book / return book bookId in JSON format """

    returnStatement = []

    jsonObject = request.json

    # we escape all values
    for key, value in jsonObject["datas"].items():
        jsonObject["datas"][key] = value.replace("'", "''")

    # For each column, we add an SQL column and value => table1,table2,table3... / 'value1','value2','value3'...
    insertColumns = ",".join(list(jsonObject["datas"].keys()))

    insertValues = "'" + "','".join(list(jsonObject["datas"].values())) + "'"

    # we build the insert query
    query = "insert into books (%(columns)s) values (%(values)s) returning id" % {'columns':insertColumns, 'values':insertValues}

    conn = connect_pg.connect()

    # the query returning the book id
    row = connect_pg.execute_commands(conn, (query,))
    
    connect_pg.disconnect(conn)
    # finally, we return the book
    return get_one_book(row)
    
@app.route('/books/search', methods=['GET'])
def advanced_search_books():
    """ Return list of books which matches with criterias """
    # criterias :
    # - title
    # - author
    # - editor
    conditions = " True "
    args = request.args
    order = ""  # Initialisez order avec une chaîne vide
    
    # we build the query with criterias
    for key in args:
        value = args.get(key).lower()
        # For each criteria, we add an SQL condition
        switch={
            # we put all criterias in lowercase
            'title': " and lower(title) like '%%%(title)s%%'" % {'title':args.get(key).lower()},
            'author': " and lower(author) like '%%%(author)s%%'" % {'author':args.get(key).lower()},
            'editor': " and lower(editor) like '%%%(editor)s%%'" % {'editor':args.get(key).lower()},
            'text': " and lower(summary) like '%%%(text)s%%'" % {'text':args.get(key).lower()},
            'dateFrom': " and date_publication >= '%%%(dateFrom)s%%'" % {'dateFrom':args.get(key).lower()},
            'dateTo': " and date_publication <= '%%%(dateTo)s%%'" % {'dateTo':args.get(key).lower()},
            'sort':'', # skipped
            }
        conditions = conditions + switch.get(key, "Invalid criteria")
        # Add sorts criterias to sql query : order by XYZ asc
        if key == "sort":

            sortValue = value
            lenSortKey = int(len(sortValue))

            if lenSortKey > 3 and sortValue[lenSortKey - 3:] == "asc":

                orderColumn = sortValue[0:lenSortKey - 3]
                order = orderColumn + " ASC"

            elif lenSortKey > 4 and sortValue[lenSortKey - 4:] == "desc":

                orderColumn = sortValue[0:lenSortKey - 4]
                order = orderColumn + " DESC"

    query = "select * from books where %(conditions)s" % {'conditions':conditions}  

    if order != "":
        query = query + " order by " + order 

    conn = connect_pg.connect()
    returnStatement = []

    try:
        rows = connect_pg.get_query(conn, query)
        
        for row in rows:
            returnStatement.append(get_book_statement(row))
    
    except Exception as e:
        # Gérer l'erreur, par exemple, en journalisant l'erreur
        print(f"Erreur lors de l'exécution de la requête SQL : {str(e)}")
    
    finally:
        connect_pg.disconnect(conn)

    return jsonify({
        "type":"books",
        "elements":len(returnStatement),
        "datas":returnStatement
        })


#TP3
@app.route('/users/add', methods=['POST'])
def add_user():
    """ Add a new user to the database """
    try:
        # Récupérez les données JSON envoyées avec la requête POST
        user_data = request.get_json()
        
        # On verifie que les champs obligatoires sont présents dans les données JSON
        champs_obligatoires = ['name', 'firstname', 'email', 'mdp']
        for champ in champs_obligatoires:
            if champ not in user_data:
                return jsonify({"error": f"Le champ '{champ}' est obligatoire"}), 400
            
        # On récupére les données de la requête JSON
        name = user_data['name']
        firstname = user_data['firstname']
        email = user_data['email']
        mdp = user_data["mdp"]       
        # Hachage du mot de passe
        mdp_hashed = bcrypt.hashpw(mdp.encode('utf-8'), bcrypt.gensalt())

        # Créez une nouvelle connexion à la base de données
        conn = connect_pg.connect()
        
        # On exécute la requête SQL pour ajouter l'utilisateur à la base de données
      #  query = f""INSERT INTO users (name, firstname, email) VALUES ('{name}', '{firstname}', '{email}') RETURNING id"
        query = [
            f"INSERT INTO users (name, firstname, email, mdp) VALUES ('{name}', '{firstname}', '{email}', '{mdp_hashed}') RETURNING id" #f pour intriduire des variables dans une string
        ]
        
        user_id = connect_pg.execute_commands(conn, query)
        
        # On ferme la connexion à la base de données
        connect_pg.disconnect(conn)

        # Réponse JSON indiquant que l'utilisateur a été ajouté avec succès
        return jsonify({"message": "L'utilisateur a était ajouté avec succès", "user_id": user_id}), 201

    except Exception as e:
        # En cas d'erreur, renvoyez une réponse JSON avec le message d'erreur
        return jsonify({"error": str(e)}), 500


@app.route('/users/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """ Delete a user from the database by ID """
    try:
        # Créez une nouvelle connexion à la base de données
        conn = connect_pg.connect()

        # Vérifiez d'abord si l'utilisateur existe
        user_exists_query = f"SELECT * FROM users WHERE id = {user_id}"
        user_exists = connect_pg.get_query(conn, user_exists_query)

        if not user_exists:
            # L'utilisateur avec l'ID spécifié n'existe pas
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Exécutez la requête SQL pour supprimer l'utilisateur de la base de données
        #delete_user_query = f"DELETE FROM users WHERE id = {user_id}"
        delete_user_query = [
            f"DELETE FROM users WHERE id = ('{user_id}')" #f pour intriduire des variables dans une string
        ]
        connect_pg.execute_commands(conn, delete_user_query)

        # Fermez la connexion à la base de données
        connect_pg.disconnect(conn)

        # Réponse JSON indiquant que l'utilisateur a été supprimé avec succès
        return jsonify({"message": f"Utilisateur avec l'ID {user_id} supprimé avec succès"}), 200

    except Exception as e:
        # En cas d'erreur, renvoyez une réponse JSON avec le message d'erreur
        return jsonify({"error": str(e)}), 500


#Verification mot de passe

@app.route('/user/identify', methods=['POST'])
def identify_user():
    """ Verification mdp avec celui de la BDD """
    try:
        data = request.json

        # Vérifiez d'abord si les clés 'user_identifiant' et 'mdp_saisie' sont présentes dans les données JSON
        if 'user_identifiant' not in data or 'mdp_saisie' not in data:
            return jsonify({"error": "Les clés 'user_identifiant' et 'mdp_saisie' sont obligatoires"}), 400

        # Récupérez les valeurs des clés 'user_identifiant' et 'mdp_saisie'
        user_identifiant = data['user_identifiant']
        mdp_saisie = data['mdp_saisie']

        # Créez une nouvelle connexion à la base de données
        conn = connect_pg.connect()

        # Vérifiez d'abord si l'utilisateur existe
        user_mdp_query = f"SELECT * FROM users WHERE identifiant = {user_identifiant}"
        user_exists = connect_pg.get_query(conn, user_exists_query)

        if not user_exists:
            # L'utilisateur avec l'ID spécifié n'existe pas
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        #recupération mdp de la BDD
        mdp_bdd = user_exists[0]["mdp"]
        # Verification du bon mot de passe

        # Hachage du mot de passe
      #  hashed_password = bcrypt.hashpw(mdp_saisie.encode('utf-8'), bcrypt.gensalt())

        # Vérification du mot de passe
        if bcrypt.checkpw(mdp_saisie.encode('utf-8'), mdp_bdd):
            return jsonify({"message": f"Le mot de passe de {user_identifiant} est correct"}), 200
        else:
            return jsonify({"message": f"Le mot de passe de {user_identifiant} est incorrect"}), 401


    except Exception as e:
        # En cas d'erreur, renvoyez une réponse JSON avec le message d'erreur
        return jsonify({"error": str(e)}), 500
 


if __name__ == "__main__":
    # read server parameters
    params = config('config.ini', 'server')
    context = (params['cert'], params['key']) #certificate and key files
    print("Affichage INFO",params['cert'], params['key'])
    # Launch Flask server0
    app.run(debug=params['debug'], host=params['host'], port=params['port'], ssl_context=context)