from llm import load_client
from game import run_game

def show_how_to_play():
    print("""
        HOW TO PLAY
        -----------
        - You will choose a historical era to set your adventure in.
        - An AI will create your character and begin the story.
        - At each step, you will be given choices. Pick one!
        - The story never ends... unless you quit.

        Press ENTER to go back to the menu...
    """)

def get_main_menu_choice():
    while True:
        try:
            print("[1] Start New Game")
            print("[2] How to Play")
            print("[3] Quit")

            player_choice = int(input("Enter your choice (1-3): "))

            if 1 <= player_choice <= 3:
                return player_choice
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except:
            print("only numbers")

def show_welcome():
    print("NEVER ENDING STORY ")
    print("An AI-Powered Interactive Adventure")
    print("What would you like to do?")
    

def run_menu():
    client = load_client()
    show_welcome()
    while True:
        number = get_main_menu_choice()
        if number == 1:
            run_game(client)
        elif number == 2:
            show_how_to_play()
        elif number == 3:
            print("\nGoodbye! May your stories never end.\n")
            break
    

if __name__ == "__main__":
    run_menu()








