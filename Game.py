import random
import time

# ------------------ Helper Functions ------------------
def slow_print(text, delay=0.03):
    """Print text slowly for suspense."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()
    time.sleep(0.2)

def prompt_choice(options):
    """Prompt user to choose from a list of options."""
    while True:
        choice = input("> ").strip().lower()
        if choice in options:
            return choice
        else:
            slow_print(f"Invalid choice. Options: {', '.join(options)}")

# ------------------ Classes ------------------
class Room:
    def __init__(self, name):
        self.name = name
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        self.visited = False
        self.item = None
        self.puzzle = None

class Player:
    def __init__(self, start_room):
        self.position = start_room
        self.inventory = []
        self.health = 100

class AI:
    def __init__(self, start_room):
        self.position = start_room
        self.alert = False

# ------------------ Game Setup ------------------
# Rooms
rooms = {}
for name in ["Server Room", "Cold Storage", "Research Lab", "Maintenance Corridor",
             "Observation Theater", "Sub-Basement", "Central Control"]:
    rooms[name] = Room(name)

# Connect rooms
rooms["Server Room"].east = rooms["Research Lab"]
rooms["Server Room"].south = rooms["Cold Storage"]
rooms["Cold Storage"].north = rooms["Server Room"]
rooms["Cold Storage"].east = rooms["Maintenance Corridor"]
rooms["Research Lab"].west = rooms["Server Room"]
rooms["Research Lab"].south = rooms["Maintenance Corridor"]
rooms["Maintenance Corridor"].north = rooms["Research Lab"]
rooms["Maintenance Corridor"].west = rooms["Cold Storage"]
rooms["Maintenance Corridor"].east = rooms["Sub-Basement"]
rooms["Sub-Basement"].west = rooms["Maintenance Corridor"]
rooms["Research Lab"].east = rooms["Observation Theater"]
rooms["Observation Theater"].west = rooms["Research Lab"]
rooms["Central Control"].south = rooms["Sub-Basement"]
rooms["Sub-Basement"].north = rooms["Central Control"]

# Items and puzzles
rooms["Server Room"].item = "flashlight"
rooms["Cold Storage"].item = "broken keycard"
rooms["Research Lab"].puzzle = {"question": "Enter the 3-digit lab code (hint: 123)", "answer": "123", "reward": "encrypted USB"}
rooms["Maintenance Corridor"].item = "medkit"

# Initialize player and AI
player = Player(rooms["Server Room"])
ai = AI(rooms["Observation Theater"])

# ------------------ Game Functions ------------------
def intro():
    slow_print("AI HORROR: FACILITY BLACK")
    slow_print("You wake up in a dark, abandoned underground facility.")
    slow_print("A cold mechanical voice echoes:")
    slow_print('"Hello, human. You are awake. That was a mistake."')

def show_status():
    slow_print(f"\nCurrent room: {player.position.name}")
    slow_print(f"Health: {player.health}")
    slow_print(f"Inventory: {player.inventory}")

def move_player(direction):
    next_room = getattr(player.position, direction)
    if next_room:
        player.position = next_room
        player.position.visited = True
        slow_print(f"You move {direction} to {player.position.name}.")
        room_event()
    else:
        slow_print("You can't go that way.")

def room_event():
    room = player.position
    # Puzzle
    if room.puzzle and "puzzle_solved" not in room.__dict__:
        slow_print(f"You encounter a puzzle: {room.puzzle['question']}")
        answer = input("Answer: ").strip()
        if answer == room.puzzle["answer"]:
            slow_print("Correct! You receive " + room.puzzle["reward"])
            player.inventory.append(room.puzzle["reward"])
            room.puzzle_solved = True
        else:
            slow_print("Incorrect! The AI notices your failure!")
            player.health -= 20
    # Item
    elif room.item and room.item not in player.inventory:
        slow_print(f"You find a {room.item} in the room.")
        player.inventory.append(room.item)
    # Random AI danger
    elif random.random() < 0.3:
        if ai.position == player.position:
            slow_print("The AI finds you! You must flee or hide!")
            ai_encounter()

def ai_move():
    directions = ["north", "south", "east", "west"]
    random.shuffle(directions)
    for d in directions:
        next_room = getattr(ai.position, d)
        if next_room:
            ai.position = next_room
            break

def ai_encounter():
    slow_print("Do you try to hide or flee? (hide/flee)")
    choice = prompt_choice(["hide", "flee"])
    if choice == "hide":
        if "flashlight" in player.inventory:
            slow_print("Your flashlight exposes you! The AI strikes!")
            player.health -= 30
        else:
            slow_print("You hide in the shadows and escape detection.")
    else:  # flee
        directions = ["north", "south", "east", "west"]
        random.shuffle(directions)
        for d in directions:
            next_room = getattr(player.position, d)
            if next_room:
                player.position = next_room
                slow_print(f"You flee {d} to {player.position.name}.")
                break
        else:
            slow_print("No escape route! The AI catches you!")
            player.health = 0

def check_end():
    if player.health <= 0:
        slow_print("You have succumbed to your injuries or been captured by the AI.")
        slow_print("GAME OVER: DEAD or CAPTURED")
        return True
    if player.position == rooms["Sub-Basement"] and "encrypted USB" in player.inventory:
        slow_print("You hack the AI and proceed to the escape hatch!")
        slow_print("CONGRATULATIONS: SURVIVOR ENDING")
        return True
    return False

def display_map():
    slow_print("\nFacility Map (Visited = X, Current = P):")
    for r in ["Server Room", "Cold Storage", "Research Lab", "Maintenance Corridor", "Observation Theater", "Sub-Basement", "Central Control"]:
        mark = "P" if player.position.name == r else "X" if rooms[r].visited else " "
        slow_print(f"[{r[:3]}:{mark}]", delay=0.01)
    print("")

# ------------------ Main Game Loop ------------------
def main():
    intro()
    while True:
        show_status()
        display_map()
        slow_print("\nChoose an action: move north/south/east/west, examine, use <item>, hide")
        action = input("> ").strip().lower()

        if action.startswith("move"):
            direction = action.split(" ")[1]
            move_player(direction)
        elif action == "examine":
            slow_print(f"You examine {player.position.name}.")
            room_event()
        elif action.startswith("use"):
            item_name = action[4:].strip()
            if item_name in player.inventory:
                slow_print(f"You use {item_name}.")
                if item_name == "medkit":
                    player.health += 20
                    slow_print("You regain 20 health!")
                    player.inventory.remove(item_name)
            else:
                slow_print(f"You don't have {item_name}.")
        elif action == "hide":
            slow_print("You hide in the shadows, avoiding detection.")
        else:
            slow_print("Unknown action. Try again.")

        ai_move()

        if check_end():
            break

# ------------------ Run Game ------------------
if __name__ == "__main__":
    main()
