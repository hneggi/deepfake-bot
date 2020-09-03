import os
import logging
import json
import argparse
from json import JSONDecodeError
from discord.ext import commands
import asyncio
import boto3
from cogs.deployment.config_cog import ConfigCog
from cogs.deployment.message_cog import MessageCog
from cogs.deployment.silly_cog import SillyCog


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MAX_BOTS = 10


class ConfigFileHandler:
    """Handles writing and reading files to and from S3"""
    def __init__(self, storage_location):

        self.storage_location = storage_location

        if storage_location == 'S3':
            cloudcube_url = os.environ['CLOUDCUBE_URL']
            access_key = os.environ['CLOUDCUBE_ACCESS_KEY_ID']
            secret_key = os.environ['CLOUDCUBE_SECRET_ACCESS_KEY']

            self.bucket_name = cloudcube_url.split('.')[0].split('//')[1]
            self.cube_name = cloudcube_url.split('/')[-1]

            self.resource = boto3.resource('s3',
                                           aws_access_key_id=access_key,
                                           aws_secret_access_key=secret_key
                                           )
    
    def get_file(self, file_name):
        """Downloads a file to the ./tmp folder if needed"""
        if self.storage_location == 'local':
            return
        elif self.storage_location == 'S3':
            local_file_name = f'./tmp/{file_name}'
            with open(local_file_name, 'wb') as f:
                f.write(self.resource.Object(self.bucket_name, f'{self.cube_name}/{file_name}').get()['Body'].read())

    def get_json(self, file_name):
        """Reads the contents of a config file and returns it as a dict"""
        if self.storage_location == 'local':
            with open(f'./tmp/{file_name}') as f:
                raw_content = f.read()
        elif self.storage_location == 'S3':
            raw_content = self.resource.Object(self.bucket_name, f'{self.cube_name}/{file_name}').get()['Body'].read()

        try:
            return json.loads(raw_content)
        except JSONDecodeError as e:
            logger.error(e)
            return False

    def update_json(self, file_name, obj):
        """Updates the json file"""
        payload = json.dumps(obj)
        try:
            if self.storage_location == 'local':
                with open(f'./tmp/{file_name}', 'w') as f:
                    f.write(payload)
                return True
            elif self.storage_location == 'S3':
                self.resource.Object(self.bucket_name, f'{self.cube_name}/{file_name}').put(Body=payload)
                return True
        except Exception as e:
            logger.error(e)
            return False


if __name__ == "__main__":

    # Add an option to run the bot without Heroku and S3
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', dest='local', action='store_true', default=False,
                        help='Run your bots locally without using S3 storage')
    args = parser.parse_args()

    # Config handler
    if args.local:
        my_file_handler = ConfigFileHandler('local')
        with open('./tmp/secrets.json') as f:
            secrets = json.loads(f.read())
    else:
        secrets = os.environ
        my_file_handler = ConfigFileHandler('S3')

    # Start with an event loop
    loop = asyncio.get_event_loop()
    idx = 0

    for i in range(MAX_BOTS):
        idx = i + 1
        try:
            # Read in the secret variables
            model_uid = secrets[f'DEEPFAKE_MODEL_UID_{idx}']
            model_key = secrets[f'DEEPFAKE_SECRET_KEY_{idx}']
            token = secrets[f'DEEPFAKE_BOT_TOKEN_{idx}']

            # Create a bot
            app = commands.Bot(command_prefix=f'df{idx}?')
            app.add_cog(ConfigCog(app, idx, model_uid, model_key, my_file_handler))
            app.add_cog(MessageCog(app))
            app.add_cog(SillyCog(app))

            loop.create_task(app.start(token))

        except KeyError as e:
            # No more secret variables found, exit the loop
            break

    logger.info(f'Found {idx - 1} bot configs...')

    try:
        loop.run_forever()
    finally:
        loop.stop()


def run_hosted_bots():
    logger.info('Starting container for hosted deployments...')
