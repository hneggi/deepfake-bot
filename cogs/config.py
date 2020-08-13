import os
from dotenv import load_dotenv


load_dotenv()

# Environment Variable Secrets
database_url = os.environ['DEEPFAKE_DATABASE_STRING']
bot_token = os.environ['DEEPFAKE_DISCORD_TOKEN']

print(database_url)

# AWS Resource Names
aws_s3_bucket_prefix = 'deepfake-discord-bot'
lambda_markov_name = 'deepfake-bot-markovify'
lambda_wordcloud_name = 'deepfake-bot-wordcloud'
lambda_activity_name = 'deepfake-bot-activity'

# Need a unique delimiter to keep messages in flat text.
unique_delimiter = '11a4b96a-ae8a-45f9-a4db-487cda63f5bd'

report_issue_url = 'https://github.com/rustygentile/deepfake-bot/issues/new'
deepfake_owner_id = 551864836917821490
version = 'new requirements test'
