from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient , NewTopic
import json
import time
import logging
import requests
from config.config import config

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename="log/app.log",filemode='a')
logger=logging.getLogger(__name__)

def report(err,msg):
    if err is not None:
        logger.error(f'message failed from the producer{err}')
    else:
        logger.info(f'message deliverd to : topic = {msg.topic()} & partition = {msg.partition()}')



def fetch_api():
    for attempts in range(3):

        try:
            response = requests.get(config.url)
            if response.status_code != 200:
                raise ValueError(f"error fetching data ,status code :{response.status_code}")
            
            logger.info('data got fetched successfully')

            return response.json()
            
        except Exception as e :
            logger.info(f'api is not available : attempts {attempts+1}')
            if attempts < 2 :
                logger.info(f'retraying after {60} s')
                time.sleep(60)
            
            else :
                logger.exception('all retries  faileed (probleme with the api)')
                raise


            


def producer():
    try :
        admin=AdminClient(config.producer_config)
        if config.topic_name not in admin.list_topics().topics: # return the claster metadata
            topic=NewTopic(config.topic_name, num_partitions=1, replication_factor=1)
            admin.create_topics([topic])
            logger.info(f'topic got created under the name : {config.topic_name}')
        
        else :
            logger.info(f'topic already exists: {config.topic_name}')

        producer = Producer(config.producer_config)

        while True :
            result = fetch_api()
            producer.produce(config.topic_name,value=json.dumps(result),callback=report)
            producer.flush()

            time.sleep(10)

        
    except Exception as e :
        logger.exception('producer error ')

producer()
