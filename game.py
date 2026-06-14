def show_eras(eras):
    print("\nCHOOSE YOUR ERA")
    print("-" * 15)
    for era in eras:
        print(f"[{era["id"]}] {era["name"]} {era["years"]} {era["description"]}")

def get_era_ids(eras):
    ids = []
    for era in eras:
        ids.append(str(era["id"]))
    return ids


def select_era(eras):
    show_eras(eras)
    valid_ids = get_era_ids(eras)
    
    while True:
        choice = input("Enter your choice (1-" + str(len(eras)) + "): ").strip()
        if choice in valid_ids:
            for era in eras:
                if choice == str(era["id"]):
                    return era
        else:
            print("Invalid choice. Please try again.")

def extract_choices(story_segment):
    return story_segment["choices"]

def display_choices(choices):
    print("─" * 49)
    print("YOUR CHOICE:")
    print("─" * 49)

    for i, choice in enumerate(choices, start=1):
        print(f"[{i}] {choice}")

    print("─" * 49)

def get_player_choice(choices):
    display_choices(choices)
    
    while True:
        selection = input("\nEnter your choice (1-3): ").strip()
        if selection in ["1", "2", "3"]:
            index = int(selection) - 1
            return choices[index]
        else:
            print("Please enter 1, 2 or 3.")

def get_player_choice_with_quit(choices):
    display_choices(choices)
    
    while True:
        selection = input("\nEnter your choice (1-3) or Q to quit: ").strip().lower()
        
        if selection == "q":
            return None  # signals that the player wants to quit
        elif selection in ["1", "2", "3"]:
            index = int(selection) - 1
            return choices[index]
        else:
            print("Please enter 1, 2, 3 or Q.")

def run_game(client):
    from settings import ERAS
    from llm import (generate_character, display_character, generate_intro,
                     display_story_segment, initialize_history, generate_continuation)
    
    # Step 1: Choose era
    era = select_era(ERAS)
    
    # Step 2: Generate and show the character
    print("\nCreating your character, please wait...")
    character = generate_character(client, era)
    display_character(character)
    input("\nPress ENTER to begin your adventure...")
    
    # Step 3: Generate and show the intro
    print("\nBeginning your story, please wait...")
    intro = generate_intro(client, era, character)
    display_story_segment(intro, "Chapter 1 — The Beginning")
    
    # Step 4: Set up history and choices
    history = initialize_history(intro)
    choices = extract_choices(intro)
    chapter = 2
    
    # Step 5: Game loop
    while True:
        # Handle case where choices couldn't be extracted
        if len(choices) != 3:
            print("\n(The story generated unexpected formatting. Asking the LLM to continue...)")
            choices = ["Continue the story forward.", 
                       "Pause and reflect on what just happened.", 
                       "Look around carefully before deciding."]
        
        # Get player's choice (with option to quit)
        print("\n[Type Q to quit to main menu]")
        chosen = get_player_choice_with_quit(choices)
        
        if chosen is None:  # player typed Q
            print("\nReturning to main menu...")
            break
        
        # Generate continuation
        print("\nContinuing your story, please wait...")
        continuation = generate_continuation(client, era, character, history, chosen)
        display_story_segment(continuation, f"Chapter {chapter}")
        
        choices = extract_choices(continuation)
        chapter += 1