import os
import logging
import math
from discord.ext import commands
from cogs.db_connection import ConnectionManager
from cogs.core_commands import CoreCommands
from cogs.filter_commands import FilterCommands
from cogs.plot_commands import PlotCommands
from cogs.model_commands import ModelCommands
from cogs.deploy_commands import DeployCommands
from cogs.deployment.deployment_runner import run_hosted_bots
import cogs.config
import argparse

logger = logging.getLogger(__name__)


class DeepFakeBot(commands.Bot):
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandOnCooldown):
            await ctx.send(f'Whoa, {ctx.author.name} slow down there! '
                           f'Try using `{ctx.invoked_with}` again in {math.ceil(exception.retry_after)}s')


def run_app():
    app = DeepFakeBot(command_prefix='d!')
    app.add_cog(ConnectionManager(app))
    app.add_cog(CoreCommands(app))
    app.add_cog(FilterCommands(app))
    app.add_cog(PlotCommands(app))
    app.add_cog(ModelCommands(app))
    app.add_cog(DeployCommands(app))

    @app.event
    async def on_message(message):
        await app.process_commands(message)

    token = cogs.config.bot_token
    try:
        app.run(token)
    except RuntimeError as e:
        logger.error('DeepfakeBot: Failed start attempt. I may have already been running.')
        logger.error(e)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser()
    parser.add_argument('--hosted', action='store_true', default=False, dest='hosted')
    if parser.parse_args().hosted:
        run_hosted_bots()
    else:
        run_app()
