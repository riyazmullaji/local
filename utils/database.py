import snowflake.connector
from exception import CustomException
from logger import logging
import os

# Initialize logger
logger = logging.getLogger(__name__)

# Function to load queries from `queries.sql`
def load_queries(file_path="utils/queries.sql"):
    queries = {}
    try:
        with open(file_path, "r") as file:
            content = file.read()
            query_parts = content.split("--")
            for part in query_parts:
                lines = part.strip().split("\n")
                if len(lines) > 1:
                    query_name = lines[0].strip()  # First line as key
                    query_sql = "\n".join(lines[1:]).strip()  # Rest as SQL
                    queries[query_name] = query_sql
        logger.info(f"Queries loaded successfully: {list(queries.keys())}")
    except Exception as e:
        logger.error(f"Error loading queries from {file_path}: {e}")
        raise CustomException("Error loading queries", e)
    return queries

# Load queries globally when the module is imported
QUERIES = load_queries()

# Snowflake connection setup
def get_connection():
    try:
        conn = snowflake.connector.connect(
            user='riyazmullaji',
            password='HelloWorld@1902',
            account='oa32825.ap-south-1',
            warehouse='SF_HACKATHON',
            database='PMAY_DB',
            schema='HOUSING'
        )
        logger.info("Connection to Snowflake established successfully.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to Snowflake: {e}")
        raise CustomException("Error connecting to Snowflake", e)

# Function to execute queries
def execute_query(query_name, params=None):
    conn = None
    try:
        if query_name not in QUERIES:
            raise ValueError(f"Query '{query_name}' not found in loaded queries.")

        query = QUERIES[query_name]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()  # For SELECT queries
            logger.info(f"Query executed successfully: {result}")
            return result
        else:
            conn.commit()  # For INSERT/UPDATE/DELETE queries
            logger.info("Query executed successfully (INSERT/UPDATE/DELETE).")
        cursor.close()
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise CustomException("Error executing query", e)
    finally:
        if conn:
            conn.close()
