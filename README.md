# 📌 Plateforme de Streaming en Temps Réel pour la Gestion et l'Analyse des Utilisateurs

Ce projet met en place un pipeline de données en temps réel pour ingérer, traiter et visualiser les données des utilisateurs. En utilisant l'API Random User, le système récupère des profils d'utilisateurs et les traite en quasi-temps réel grâce à Apache Kafka, PySpark Structured Streaming, MongoDB et Cassandra. Les résultats finaux sont affichés sur un tableau de bord Streamlit pour le suivi et l'analyse.

## 🚀 Fonctionnalités

- **Streaming basé sur Kafka** : Collecte et distribue efficacement les données utilisateur.
- **Traitement avec PySpark** : Transforme et agrège les données dynamiquement.
- **Stockage MongoDB & Cassandra** : Stockage flexible des documents et requêtes analytiques rapides.
- **Tableau de bord Streamlit** : Visualisation en direct des données brutes et agrégées.
- **Résilience et scalabilité** : Gestion des échecs d'ingestion avec des mécanismes de reprise.

## ⚙️ Architecture du Projet

```
+-----------------------+
|   Random User API     |
|                       |
+----------+----------- +
           |
(1) Script d'Ingestion (Python) 
           v
+-----------------------+
|   Producteur Kafka    |
+----------+----------- +
           |
           v
+----------------------+
|  Cluster Kafka       |
| (Brokers, Zookeeper) |
+----------+-----------+
           |
           v
+-----------------------+
| PySpark Streaming     |
| (Traitement Structuré)|
+----------+----------- +
   |        |        |
   |        |        | (4) Écriture des agrégats
   |        |        | dans Cassandra
   |        |        |
   v        v        v
+--------+ +-------------+ +-----------------+
|MongoDB | |  Cassandra  | |   Monitoring    |
+--------+ +-------------+ +-----------------+
          |
          v
  (5) Tableau de bord Streamlit
```

## 📊 Flux de Données

1. **Ingestion des données** : Le script Python récupère les utilisateurs depuis l'API Random User.
2. **Kafka Producer** : Envoie les données utilisateur à un topic Kafka.
3. **PySpark Streaming** : Lit les données de Kafka, les transforme et les stocke dans MongoDB & Cassandra.
4. **MongoDB** : Stocke les données brutes des utilisateurs.
5. **Cassandra** : Stocke les statistiques agrégées des utilisateurs.
6. **Tableau de bord Streamlit** : Affiche les mises à jour en temps réel.

## 🎯 Composants Clés

- **Producteur Kafka (Python & Requests)** : Récupère les données utilisateur et les envoie à Kafka.
- **Cluster Kafka** : Gestionnaire de messages pour le streaming en temps réel.
- **PySpark Streaming** : Traitement et enrichissement des données.
- **MongoDB** : Stockage des données brutes.
- **Cassandra** : Stockage des insights et des statistiques agrégées.
- **Streamlit Dashboard** : Interface de visualisation des données.

## 📈 Monitoring & Résilience

- **Surveillance de Kafka** : Vérification de la publication et consommation des messages.
- **Interface PySpark Streaming** : Suivi des tâches Spark et gestion des erreurs.
- **Mécanisme de Reprise** : Gestion des pannes réseau et erreurs API.

## 📬 Contactez-moi

- **Auteur** : Ali Rahiqi 
- **Email** : [ali123rahiqi@gmail.com](mailto:ali123rahiqi@gmail.com)

