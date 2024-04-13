import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
from automatedAgent import State, bestMove
import time

moves = {"w": "UP", "a": "LEFT", "s": "DOWN", "d": "RIGHT"}


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
    Prints a mqtt message to stdout ( used as callback for subscribe )
    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param msg: the message with topic and payload
    """

    topic_list = msg.topic.split("/")
    topic_title = topic_list[-1]

    if topic_title == "game_state":
        # Parse game state and display to user
        raw_state = json.loads(msg.payload)

        # Populate State model
        state = State(
            teammateNames=raw_state["teammateNames"],
            teammatePositions=raw_state["teammatePositions"],
            enemyPositions=raw_state["enemyPositions"],
            currentPosition=raw_state["currentPosition"],
            coin1=raw_state["coin1"],
            coin2=raw_state["coin2"],
            coin3=raw_state["coin3"],
            walls=raw_state["walls"],
        )

        # Get best move
        best_move = bestMove(state)

        # Publish move to broker
        move_direction = moves[best_move]
        lobby = topic_list[1]
        player = topic_list[2]
        print(
            f"{str(client._client_id, encoding='utf-8')} wants to move {move_direction}."
        )
        client.publish(f"games/{lobby}/{player}/move", move_direction)

    elif topic_title == "lobby":
        # Check for game over
        message = str(msg.payload, "utf-8")
        if "Game Over" in message:
            # Disconnect to end the program
            client.loop_stop()
            client.disconnect()


load_dotenv(dotenv_path="./credentials.env")
broker_address = os.environ.get("BROKER_ADDRESS")
broker_port = int(os.environ.get("BROKER_PORT"))
username = os.environ.get("USER_NAME")
password = os.environ.get("PASSWORD")


class PlayerClient:
    """
    Player Client

    Represents a single player of the game.

    """

    def __init__(self, lobby_name, team_name, player_name):
        self.in_game = False
        self.lobby_name = lobby_name
        self.team_name = team_name
        self.player_name = player_name

        self.client = paho.Client(
            callback_api_version=paho.CallbackAPIVersion.VERSION1,
            client_id=player_name,
            userdata=None,
            protocol=paho.MQTTv5,
        )

        # enable TLS for secure connection
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        self.client.username_pw_set(username, password)
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        self.client.connect(broker_address, broker_port)

        # setting callbacks, use separate functions like above for better visibility
        self.client.on_message = on_message
        self.client.on_disconnect = self.on_disconnect_handler()

        # subscribe to relevant topics
        self.client.subscribe(f"games/{lobby_name}/lobby")
        self.client.subscribe(f"games/{lobby_name}/{player_name}/game_state")
        self.client.subscribe(f"games/{lobby_name}/scores")

    def on_disconnect_handler(self):
        """
        Return a handler for on_disconnect
        """

        def on_disconnect(client, userdata, flags, rc):
            self.in_game = False

        return on_disconnect

    def join_game(self, leader=False):
        """Join the game lobby.
           If leader is True, the client will start the game for everyone.

        Args:
            leader (bool, optional): leader of the game? Defaults to False.
        """

        # register client to game
        print(f"{self.player_name} on {self.team_name} joining...")
        self.client.publish(
            "new_game",
            json.dumps(
                {
                    "lobby_name": self.lobby_name,
                    "team_name": self.team_name,
                    "player_name": self.player_name,
                }
            ),
        )

        if leader:
            time.sleep(1)  # Wait a second to resolve game start
            print("Starting game...")
            self.client.publish(f"games/{self.lobby_name}/start", "START")

        self.in_game = True
        self.client.loop_start()
