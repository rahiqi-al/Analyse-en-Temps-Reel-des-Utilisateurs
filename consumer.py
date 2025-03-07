from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, concat, lit, current_timestamp, count, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
import logging
from pymongo import MongoClient
from config.config import config  
from cassandra.cluster import Cluster, NoHostAvailable
import uuid
import json


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename="log/app.log",filemode='a')
logger = logging.getLogger(__name__)

def store_mongodb(batch_df, batch_id):
    client = None
    try:
        client = MongoClient(config.connection_string)
        db = client["randomUserDB"]
        collection = db["users"]
        
        results = batch_df.selectExpr("explode(results) as result").toJSON().collect()
        logger.info(f"Batch {batch_id}: Collected {len(results)} JSON rows")
        data = [json.loads(r) for r in results]
        
        if data:
            collection.insert_many(data)
            logger.info(f"Inserted {len(data)} records into MongoDB for batch {batch_id}")
        else:
            logger.info(f"No data to insert into MongoDB for batch {batch_id}")
    
    except Exception as e:
        logger.exception(f"MongoDB error in batch {batch_id}: {e}")
    finally:
        if client:
            client.close()

def store_cassandra(batch_df, batch_id):
    cluster = None
    try:    
        logger.info(f'Storing batch {batch_id} in Cassandra')
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect()

        session.execute("CREATE KEYSPACE IF NOT EXISTS user_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")
        session.set_keyspace("user_keyspace")
        
        session.execute(""" CREATE TABLE IF NOT EXISTS user_keyspace.users (
            id uuid PRIMARY KEY, gender text, street_number int, street_name text, city text, state text, 
            country text, postcode text, latitude float, longitude float, email text, age int, 
            phone text, nat text, full_name text, ingestion_time timestamp )""")
        
        df = batch_df.selectExpr("explode(results) as result").select(
            col("result.gender").alias("gender"),
            col("result.name.title").alias("title"),
            col("result.name.first").alias("first"),
            col("result.name.last").alias("last"),
            col("result.location.street.number").alias("street_number"),
            col("result.location.street.name").alias("street_name"),
            col("result.location.city").alias("city"),
            col("result.location.state").alias("state"),
            col("result.location.country").alias("country"),
            col("result.location.postcode").cast("string").alias("postcode"),
            col("result.location.coordinates.latitude").cast("float").alias("latitude"),
            col("result.location.coordinates.longitude").cast("float").alias("longitude"),
            col("result.email").alias("email"),
            col("result.dob.age").alias("age"),
            col("result.phone").alias("phone"),
            col("result.nat").alias("nat"))

        df = df.select('*', 
                       concat(col('title'), lit(" "), col("first"), lit(" "), col("last")).alias('full_name'),
                       current_timestamp().alias("ingestion_time")).drop("title", "first", "last")  
        
        logger.info('Starting to insert data into Cassandra')
        rows = df.collect()
        for row in rows:
            session.execute(
                "INSERT INTO user_keyspace.users (id, gender, street_number, street_name, city, state, country, postcode, latitude, longitude, email, age, phone, nat, full_name, ingestion_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (uuid.uuid4(), row["gender"], row["street_number"], row["street_name"], row["city"], row["state"], row["country"], row["postcode"], row["latitude"], row["longitude"], row["email"], row["age"], row["phone"], row["nat"], row["full_name"], row["ingestion_time"])
            )
        logger.info(f"Finished inserting {len(rows)} rows into Cassandra for batch {batch_id}")

        df_grouped = df.groupBy("country").agg(count("*").alias("user_count"), avg("age").alias("average_age"))
        logger.info(f"Cassandra aggregation complete for batch {batch_id}")
    
    except NoHostAvailable as e:
        logger.exception(f"Cassandra connection failed for batch {batch_id}: {e}")
    except Exception as e:
        logger.exception(f"Cassandra processing error for batch {batch_id}: {e}")
    finally:   
        if cluster: 
            cluster.shutdown()

def consumer():
    spark = None
    try:
        logger.info('Starting the consumer')
        spark = SparkSession.builder.appName("streamprocessing").config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1").config("spark.hadoop.fs.defaultFS", "file:///").getOrCreate()
        logger.info('Session created successfully')

        schema = StructType([
            StructField("results", ArrayType(StructType([
                StructField("gender", StringType(), True),
                StructField("name", StructType([
                    StructField("title", StringType(), True),
                    StructField("first", StringType(), True),
                    StructField("last", StringType(), True)
                ]), True),
                StructField("location", StructType([
                    StructField("street", StructType([
                        StructField("number", IntegerType(), True),
                        StructField("name", StringType(), True)
                    ]), True),
                    StructField("city", StringType(), True),
                    StructField("state", StringType(), True),
                    StructField("country", StringType(), True),
                    StructField("postcode", IntegerType(), True),
                    StructField("coordinates", StructType([
                        StructField("latitude", StringType(), True),
                        StructField("longitude", StringType(), True)
                    ]), True),
                    StructField("timezone", StructType([
                        StructField("offset", StringType(), True),
                        StructField("description", StringType(), True)
                    ]), True)
                ]), True),
                StructField("email", StringType(), True),
                StructField("dob", StructType([
                    StructField("date", StringType(), True),
                    StructField("age", IntegerType(), True)
                ]), True),
                StructField("registered", StructType([
                    StructField("date", StringType(), True),
                    StructField("age", IntegerType(), True)
                ]), True),
                StructField("phone", StringType(), True),
                StructField("cell", StringType(), True),
                StructField("nat", StringType(), True)
            ])), True),
            StructField("info", StructType([
                StructField("seed", StringType(), True),
                StructField("results", IntegerType(), True),
                StructField("page", IntegerType(), True),
                StructField("version", StringType(), True)
            ]), True)])  

        df = spark.readStream.format('kafka').option("kafka.bootstrap.servers", config.server).option("subscribe", config.topic_name).option("startingOffsets", "earliest").option("group.id", "spark-streaming-test").load()


        df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.results")
        logger.info('Starting the function to store raw data in MongoDB')
        query = df.writeStream.foreachBatch(lambda batch_df, batch_id: [store_mongodb(batch_df, batch_id), store_cassandra(batch_df, batch_id)]).outputMode('append').start()
        logger.info('Streaming query started, waiting for Kafka data...')

        query.awaitTermination()
    
    except Exception as e:
        logger.exception(f'Consumer error: {e}')
    finally:
        if spark:
            spark.stop()


