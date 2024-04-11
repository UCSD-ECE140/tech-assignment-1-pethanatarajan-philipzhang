import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

moves = {"w": "UP", "a": "LEFT", "s": "DOWN", "d": "RIGHT"}


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
    Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param flags: these are response flags sent by the broker
    :param rc: stands for reasonCode, which is a code for the connection result
    :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
    Prints mid to stdout to reassure a successful publish ( used as callback for publish )
    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
    :param properties: can be used in MQTTv5, but is optional
    """


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
    Prints a reassurance for successfully subscribing
    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
    :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
    :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


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
        state = json.loads(msg.payload)
        print("Current Position:", state["currentPosition"])

        print("Coins: ", end="")
        for coin in ["coin1", "coin2", "coin3"]:
            coin_position = state[coin]
            if coin_position:
                print(coin_position, end=" ")
        print()

        print("Walls:", state["walls"], "\n")

        # Request move from user
        raw_input = input("Input your move: ")
        while raw_input not in moves:
            print("Invalid move.")
            raw_input = input("Input your move: ")

        # Publish move to broker
        move = moves[raw_input]
        lobby = topic_list[1]
        player = topic_list[2]
        client.publish(f"games/{lobby}/{player}/move", move)

    elif topic_title == "lobby":
        # Check for game over
        message = str(msg.payload, "utf-8")
        if "Game Over" in message:
            # Disconnect to end the program
            client.disconnect()

        print(message)


if __name__ == "__main__":
    load_dotenv(dotenv_path="./credentials.env")

    broker_address = os.environ.get("BROKER_ADDRESS")
    broker_port = int(os.environ.get("BROKER_PORT"))
    username = os.environ.get("USER_NAME")
    password = os.environ.get("PASSWORD")

    client = paho.Client(
        callback_api_version=paho.CallbackAPIVersion.VERSION1,
        client_id="Player1",
        userdata=None,
        protocol=paho.MQTTv5,
    )

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = (
        on_subscribe  # Can comment out to not print when subscribing to new topics
    )
    client.on_message = on_message
    client.on_publish = (
        on_publish  # Can comment out to not print when publishing to topics
    )

    lobby_name = "LonelyGame"
    player_1 = "Player1"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f"games/{lobby_name}/+/game_state")
    client.subscribe(f"games/{lobby_name}/scores")

    client.publish(
        "new_game",
        json.dumps(
            {"lobby_name": lobby_name, "team_name": "ATeam", "player_name": player_1}
        ),
    )

    time.sleep(1)  # Wait a second to resolve game start

    client.publish(f"games/{lobby_name}/start", "START")
    client.loop_forever()
