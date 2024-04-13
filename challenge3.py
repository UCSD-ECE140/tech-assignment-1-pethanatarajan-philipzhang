from PlayerClient import PlayerClient


lobby = "Challenge3Game"

# Team names and player names
teams = {"red_team": ["red1", "red2"], "blue_team": ["blue1", "blue2"]}

clients = []

# Init player clients
for team_name, players in teams.items():
    for player_name in players:
        client = PlayerClient(lobby, team_name, player_name)
        clients.append(client)

# Join clients to game
for i, client in enumerate(clients):
    # The last client is the leader and they will start the game
    leader = i == len(clients) - 1
    client.join_game(leader)


while all([client.in_game for client in clients]):
    # Wait until all clients are done playing
    pass
