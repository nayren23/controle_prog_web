# Utilisez une image Python de base
FROM python:3.10

WORKDIR /usr/app

# Copiez le reste de votre application
COPY * ./
COPY ./requirements.txt  usr/app/requirements.txt

# Installez toutes les dépendances Python qui sont listé dans le fichier "requirements.txt"
RUN pip install -r ./requirements.txt 
RUN pip install bcrypt

EXPOSE 5050
EXPOSE 8080

# Commande d'exécution de votre application Flask
CMD ["python3", "rest_api.py"]