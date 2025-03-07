import streamlit as st
import logging
import pandas as pd
from cassandra.cluster import Cluster
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename="log/app.log", filemode='a')
logger = logging.getLogger(__name__)

def get_recent_users(session):
    query = "SELECT * FROM users LIMIT 10;"
    rows = session.execute(query)
    return pd.DataFrame(rows, columns=rows.column_names)

def app():
    try:
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect('user_keyspace')
    except Exception as e:
        st.error(f"Error connecting to Cassandra: {e}")
        logger.error(f"Cassandra Connection Error: {e}")
        return

    st.title("Dashboard Utilisateurs - Cassandra")
    st.subheader("Derniers utilisateurs enregistrés")

    # Display recent users
    recent_users = get_recent_users(session)
    st.dataframe(recent_users)

    # Auto-refresh every 10 seconds
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    app()
