from dotenv import load_dotenv
import os 
import yaml 
load_dotenv()



class Config :
    with open('config/config.yml','r') as file:
        config_data = yaml.load(file , Loader=yaml.FullLoader)

        url=config_data['INGESTION']['URL']
        producer_config=config_data['PRODUCER']['CONFIG']
        topic_name =config_data['PRODUCER']['TOPIC_NAME']



        server=os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        connection_string=os.getenv('CONNECTION_STRING')











config = Config()    

#print(config.topic_name)

