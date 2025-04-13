import random

suits = ["Diamonds", "Hearts", "Spades", "Clubs"]
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]

deck = [(rank, suit) for suit in suits for rank in ranks]
