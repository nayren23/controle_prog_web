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
import os


app = Flask(__name__)

######################### Token ######################### 
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=get_one_user(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            if not current_user["active"]:
                abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated

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
    

@app.route('/')
def hello():
    return "Hello"


@app.route('/locataire/get/<userID>', methods=['GET','POST'])
def get_one_user(userID):
    """ Return book bookId in JSON format """
    query = "select * from agence.locataire where id=%(userID)s order by id asc" % {'userID':userID}
    conn = connect_pg.connect()
    rows = connect_pg.get_query(conn, query)
    returnStatement = {}
    if len(rows) > 0:
        returnStatement = get_user_statement(rows[0])
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


def get_users_statement(row) :
    """ users array statement """
    return {
        'id':row[0],
        'name   ':row[1],
        'firstname':row[2],
        'email' : row[3]
    }

#TP3
@app.route('/locataire/add', methods=['POST'])
def add_user():
    """ Add a new locataire to the database """
    try:
        # Récupérez les données JSON envoyées avec la requête POST
        locataire_data = request.get_json()
        
        # On verifie que les champs obligatoires sont présents dans les données JSON
        champs_obligatoires = ['nom', 'prenom', 'mail', 'mdp']
        for champ in champs_obligatoires:
            if champ not in locataire_data:
                return jsonify({"error": f"Le champ '{champ}' est obligatoire"}), 400
            
        # On récupére les données de la requête JSON
        nom = locataire_data['nom']
        prenom = locataire_data['prenom']
        mail = locataire_data['mail']
        mdp = locataire_data["mdp"]       
        # Hachage du mot de passe
        mdp_hashed = bcrypt.generate_password_hash(mdp).decode('utf-8')

        # Créez une nouvelle connexion à la base de données
        conn = connect_pg.connect()
        
        # On exécute la requête SQL pour ajouter l'utilisateur à la base de données
        query = [
            f"INSERT INTO agence.locataire (nom, prenom, mail, mdp) VALUES ('{nom}', '{prenom}', '{mail}', '{mdp_hashed}') RETURNING id" #f pour intriduire des variables dans une string
        ]
        
        locataire_id = connect_pg.execute_commands(conn, query)
        
        # On ferme la connexion à la base de données
        connect_pg.disconnect(conn)

        # Réponse JSON indiquant que l'utilisateur a été ajouté avec succès
        return jsonify({"message": "L'utilisateur a était ajouté avec succès", "locataire_id": locataire_id}), 201

    except Exception as e:
        # En cas d'erreur, renvoyez une réponse JSON avec le message d'erreur
        return jsonify({"error": str(e)}), 500


#Verification mot de passe

@app.route('/identify', methods=['POST'])
def identify_user():
    """ Verification mdp avec celui de la BDD """
    try:
        data = request.json

        # Vérifiez d'abord si les clés 'locataire_mail' et 'mdp_saisie' sont présentes dans les données JSON
        if 'locataire_mail' not in data or 'mdp_saisie' not in data:
            return jsonify({"error": "Les clés 'locataire_mail' et 'mdp_saisie' sont obligatoires"}), 400

        # Récupérez les valeurs des clés 'locataire_mail' et 'mdp_saisie'
        locataire_mail = data['locataire_mail']
        mdp_saisie = data['mdp_saisie']

        # Créez une nouvelle connexion à la base de données
        conn = connect_pg.connect()

        # Vérifiez d'abord si l'utilisateur existe
        locataire_mdp_query = f"SELECT * FROM agence.locataire WHERE mail = '{locataire_mail}'"
        locataire_exists = connect_pg.get_query(conn, locataire_mdp_query)

        if not locataire_exists:
            # L'utilisateur avec l'ID spécifié n'existe pas
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        #recupération mdp de la BDD

        mdp_bdd = locataire_exists[0]["mdp"]

        # Vérification du mot de passe
        if bcrypt.checkpw(mdp_saisie.encode('utf-8'), mdp_bdd):
            try:
                # token should expire after 24 hrs
                user["token"] = jwt.encode(
                    {"user_id": user["id"],
                    "exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(minutes=15)},
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                return jsonify({"message": f"Le mot de passe de {locataire_mail} est correct"}), 200

            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500       
        return jsonify({"message": f"Le mot de passe de {locataire_mail} est incorrect"}), 401

    except Exception as e:
        # En cas d'erreur, renvoyez une réponse JSON avec le message d'erreur
        return jsonify({"error": str(e)}), 500
 

if __name__ == "__main__":
  # read server parameters
  params = config('config.ini', 'server')
  context = (params['cert'], params['key']) #certificate and key files
  # Launch Flask server
  app.run(debug=params['debug'], host=params['host'], port=params['port'], ssl_context=context)