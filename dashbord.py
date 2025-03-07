from consumer import consumer
from producer import producer
import streamlit as st
import logging
import pandas as pd 
from cassandra.cluster import Cluster
import time

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename="log/app.log",filemode='a')
logger=logging.getLogger(__name__)


def app():
    # Start producer and consumer
    producer()
    time.sleep(5)
    consumer()
    time.sleep(5)

    # Connect to Cassandra
    try:
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect('user_keyspace')  # Set keyspace directly
    except Exception as e:
        st.error(f"Error connecting to Cassandra: {e}")
        logger.error(f"Cassandra Connection Error: {e}")
        return

    # Function to get recent users
    def get_recent_users():
        query = "SELECT * FROM users LIMIT 10;"
        rows = session.execute(query)
        return pd.DataFrame(rows, columns=rows.column_names)

    st.title("Dashboard Utilisateurs - Cassandra")

    st.subheader("Derniers utilisateurs enregistrés")
    recent_users = get_recent_users()
    st.dataframe(recent_users)

    # Auto-refresh using Streamlit empty container
    placeholder = st.empty()
    while True:
        time.sleep(10)
        placeholder.empty()  # Clear previous content
        recent_users = get_recent_users()
        placeholder.dataframe(recent_users)
        st.experimental_rerun()  # Refresh Streamlit page

if __name__ == "__main__":
    app()

