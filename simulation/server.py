from dotenv import load_dotenv
from flask import Flask

from controllers.aws_controller import AwsController
from controllers.call_controller import CallController
from controllers.command_controller import CommandController
from controllers.ssh_controller import SSHController
from controllers.user_controller import UserController

app = Flask(__name__)
app.register_blueprint(UserController.user_controller)
app.register_blueprint(AwsController.aws_controller)
app.register_blueprint(CommandController.command_controller)
app.register_blueprint(SSHController.ssh_controller)
app.register_blueprint(CallController.call_controller)
load_dotenv()

if __name__ == '__main__':
    app.run(port=5001)