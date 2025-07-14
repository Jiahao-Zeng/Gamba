import random

suits = ["Diamonds", "Hearts", "Spades", "Clubs"]
suit_symbols = {"Diamonds": "♦", "Hearts": "♥", "Spades": "♠", "Clubs": "♣"}
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]

class Shoe(list):
    def __init__(self, num_decks: int = 4):
        self.num_decks = num_decks
        super().__init__()
        self._reshuffle()

    def _reshuffle(self) -> None:
        self[:] = [
            (rank, suit)
            for _ in range(self.num_decks)
            for suit in suits
            for rank in ranks
        ]
        random.shuffle(self)

    # In case shoe runs out while hand is in play
    def pop(self, index: int = -1):
        if not self:
            self._reshuffle()
        return super().pop(index)

def card_value(rank: int | str) -> int:
    if rank == "A":
        return 11
    if rank in ("J", "Q", "K"):
        return 10
    return int(rank)

def card_display(rank, suit):
    """Convert card to display format with suit symbol"""
    return f"{rank}{suit_symbols[suit]}"

def hand_value(hand: list[tuple[int | str, str]]) -> int:
    total = 0
    aces = 0

    # Ace tracker
    for rank, _ in hand:
        total += card_value(rank)
        if rank == "A":
            aces += 1

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

class Hand:
    def __init__(self, bet=0):
        self.cards = []
        self.bet = bet
        self.original_bet = bet  
        self.stood = False
        self.doubled = False

    def total(self):
        total = sum(card_value(rank) for rank, _ in self.cards)
        aces = sum(1 for rank, _ in self.cards if rank == "A")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
    def is_pair(self):
        return len(self.cards) == 2 and self.cards[0][0] == self.cards[1][0]
    
    def can_split(self):
        return self.is_pair()
    
    def split(self):
        if not self.can_split():
            raise ValueError("Can't split")
        card = self.cards.pop()
        new_hand = Hand(bet=self.bet)
        new_hand.original_bet = self.original_bet  
        new_hand.cards.append(card)
        return new_hand
    
    def can_double(self, player) -> bool:
        return (len(self.cards) == 2 and not self.doubled and player.balance >= self.bet) 
    
    def __str__(self):
        cards = ", ".join(card_display(r, s) for r, s in self.cards)
        total = self.total()
        
        # Check if hand has aces and could show alternate value
        aces = sum(1 for rank, _ in self.cards if rank == "A")
        if aces > 0:
            # Calculate the value with aces as 1
            soft_total = sum(card_value(rank) for rank, _ in self.cards) - (aces * 10)
            if soft_total <= 21 and soft_total != total:
                return f"{cards} ({soft_total}/{total}) - Bet: ${self.original_bet}"
        
        return f"{cards} ({total}) - Bet: ${self.original_bet}"
    
    def display_hand(self):
        """Display hand without bet information (for dealer)"""
        cards = ", ".join(card_display(r, s) for r, s in self.cards)
        total = self.total()
        
        # Check if hand has aces and could show alternate value
        aces = sum(1 for rank, _ in self.cards if rank == "A")
        if aces > 0:
            # Calculate the value with aces as 1
            soft_total = sum(card_value(rank) for rank, _ in self.cards) - (aces * 10)
            if soft_total <= 21 and soft_total != total:
                return f"{cards} ({soft_total}/{total})"
        
        return f"{cards} ({total})"
    
class Player:
    def __init__(self, balance=0):
        self.balance = balance
        self.hands = []

    def place_bet(self, amount, hand):
        if amount > self.balance:
            raise ValueError("Not enough money to place")
        self.balance -= amount
        hand.bet += amount

class Dealer(Player):
    def play(self, shoe):
        hand = self.hands[0]

        # Show initial dealer hand before playing
        print(f"Dealer shows: {hand.display_hand()}")
        
        stand_on_soft17 = True
        while True:
            total = hand.total()
            soft = any(rank == "A" for rank, _ in hand.cards) and total <= 21
            if total < 17:
                hand.cards.append(shoe.pop())
                print(f"Dealer shows: {hand.display_hand()}")
            elif total == 17 and soft and not stand_on_soft17:
                hand.cards.append(shoe.pop())
                print(f"Dealer shows: {hand.display_hand()}")
            else:
                hand.stood = True
                break
        
        print("_" * 50)

def deal_initial(player, dealer, shoe, bet_size):
    player.hands = [Hand(bet=bet_size)]
    dealer.hands = [Hand()]
    player.place_bet(bet_size, player.hands[0])

    for _ in range(2):
        player.hands[0].cards.append(shoe.pop())
        dealer.hands[0].cards.append(shoe.pop())

def play_player_hands(player, shoe):
    hand_index = 0
    while hand_index < len(player.hands):
        hand = player.hands[hand_index]
        
        while not hand.stood and hand.total() < 21:
            print(f"\nHand {hand_index + 1}: {hand}")
            
            # Build options list
            options = []
            option_map = {}
            
            # Always available options
            options.append("Hit")
            option_map["1"] = "hit"
            option_map["hit"] = "hit"
            option_map["h"] = "hit"
            
            options.append("Stand")
            option_map["2"] = "stand"
            option_map["stand"] = "stand"
            option_map["s"] = "stand"
            
            # Conditional options
            if hand.can_double(player):
                options.append("Double")
                option_map["3"] = "double"
                option_map["double"] = "double"
                option_map["d"] = "double"
            
            if hand.can_split():
                options.append("Split")
                option_map["4"] = "split"
                option_map["split"] = "split"
                option_map["sp"] = "split"
            
            # Display options
            print("Options:")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            
            action = input("Choice: ").strip().lower()
            
            # Handle the action
            if action in option_map:
                action = option_map[action]
            
            if action == "hit":
                hand.cards.append(shoe.pop())
            elif action == "stand":
                hand.stood = True
            elif action == "split" and hand.can_split():
                new_hand = hand.split()
                hand.cards.append(shoe.pop())
                new_hand.cards.append(shoe.pop())
                player.place_bet(hand.bet, new_hand)
                player.hands.append(new_hand)
                # Don't increment hand_index - stay on current hand
            elif action == "double" and hand.can_double(player):
                player.place_bet(hand.bet, hand)
                hand.doubled = True
                hand.cards.append(shoe.pop())
                hand.stood = True
            else:
                print("Invalid choice")
        
        # Move to next hand
        hand_index += 1

def result(player, dealer):
    dealer_total = dealer.hands[0].total()
    print(f"\nDealer shows: {dealer.hands[0].display_hand()}")

    for i, hand in enumerate(player.hands, 1):
        total = hand.total()
        outcome = ""
        if total > 21:
            outcome = "bust"
        elif dealer_total > 21 or total > dealer_total:
            outcome = "win"
            player.balance += hand.bet
        elif total == dealer_total:
            outcome = "push"
            player.balance += hand.bet
        else:
            outcome = "lose"
        print(f"Hand {i}: {hand}; {outcome}")

if __name__ == "__main__":
    print("Welcome to Blackjack!")
    
    # Initialize game
    shoe = Shoe(4)  # 4 deck shoe
    player = Player(1000)  # Start with $1000
    dealer = Dealer()
    
    while True:
        print(f"\nYour balance: ${player.balance}")
        
        if player.balance <= 0:
            print("You're out of money! Game over.")
            break
            
        # Get bet
        while True:
            try:
                bet = int(input("Enter your bet (or 0 to quit): "))
                if bet == 0:
                    print("Thanks for playing!")
                    exit()
                if bet > player.balance:
                    print("Not enough money!")
                    continue
                if bet < 1:
                    print("Bet must be at least $1!")
                    continue
                break
            except ValueError:
                print("Please enter a valid number!")
        
        # Deal initial cards
        deal_initial(player, dealer, shoe, bet)
        
        print("_" * 50)  # Visual separator after bet
        
        # Show dealer's up card
        dealer_up_card = dealer.hands[0].cards[0]
        print(f"\nDealer shows: {card_display(dealer_up_card[0], dealer_up_card[1])} ({card_value(dealer_up_card[0])})")
        print(f"Your hand: {player.hands[0]}")
        
        print("_" * 50)  # Visual separator after showing hands
        
        # Offer insurance if dealer shows ace
        insurance_bet = 0
        if dealer_up_card[0] == "A":
            print("\nInsurance is available!")
            while True:
                try:
                    insurance_input = input("Would you like insurance? (y/n): ").strip().lower()
                    if insurance_input in ["y", "yes"]:
                        insurance_amount = int(input(f"Enter insurance amount (max ${bet//2}): "))
                        if insurance_amount <= 0:
                            print("Insurance amount must be positive!")
                            continue
                        if insurance_amount > bet // 2:
                            print(f"Insurance cannot exceed half your bet (${bet//2})!")
                            continue
                        if insurance_amount > player.balance:
                            print("Not enough money for insurance!")
                            continue
                        insurance_bet = insurance_amount
                        player.balance -= insurance_amount
                        print(f"Insurance bet: ${insurance_amount}")
                        break
                    elif insurance_input in ["n", "no"]:
                        break
                    else:
                        print("Please enter y/n")
                except ValueError:
                    print("Please enter a valid number!")
        
        # Check for blackjack
        if player.hands[0].total() == 21:
            print("Blackjack!")
            if dealer.hands[0].total() == 21:
                print("Dealer also has blackjack. Push!")
                player.balance += bet
                if insurance_bet > 0:
                    print(f"Insurance pays 2:1! You win ${insurance_bet * 2}")
                    player.balance += insurance_bet * 2
            else:
                print("You win!")
                player.balance += bet * 2.5  # Blackjack pays 3:2
                if insurance_bet > 0:
                    print(f"Insurance loses. You lose ${insurance_bet}")
            continue
        
        # Play player hands
        play_player_hands(player, shoe)
        
        # Play dealer hand
        if any(hand.total() <= 21 for hand in player.hands):
            dealer.play(shoe)
        
        # Handle insurance if dealer doesn't have blackjack
        if insurance_bet > 0 and dealer.hands[0].total() != 21:
            print(f"Insurance loses. You lose ${insurance_bet}")
        
        # Determine results
        result(player, dealer)
        
        print("_" * 50)  # Visual separator between games
        
        # Clear hands for next round
        player.hands = []
        dealer.hands = []

# TODO: 
# Check up on edge cases
# Debug any issues