import smtplib
import requests
from email.message import EmailMessage
from email.utils import formatdate
from pprint import pprint
import os
import discord
from discord.ext import commands
import discord.ext
from dotenv import load_dotenv
from typing import List, Dict
import random


load_dotenv()

SMTP_SERVER = os.environ.get("SMTP_SERVER")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
TOKEN = os.getenv("DISCORD_TOKEN")
IMGFLIP_USERNAME = os.environ.get("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.environ.get("IMGFLIP_PASSWORD")
CAPTION_IMAGE_URL = "https://api.imgflip.com/caption_image"
GET_MEMES_URL = "https://api.imgflip.com/get_memes"


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)



class Hangman:
    people_playing_list = {}

    async def play_hangman(self, ctx, hangman_player) -> None:
        await ctx.send("**Hangman**")
        await ctx.send("Player: " + hangman_player.name)
        hangman_player.guess_message = await ctx.send("Guess: ")
        hangman_player.lives_message = await ctx.send("Lives: 7")
        hangman_player.word_message = await ctx.send(
            "Word: " + str(" ".join(hangman_player.dashed_word))
        )
        hangman_player.ending_message = await ctx.send("Good luck!")

    async def guess_letter(self, ctx, hangman_player, letter) -> str:
        if letter in hangman_player.guesses:
            hangman_player.ending_phrase = "You already guessed that."

        else:
            if letter in hangman_player.word:
                await self.reveal_some_letters(hangman_player, letter)
                hangman_player.guesses.append(letter)

                if await self.is_every_letter_in_word(hangman_player):
                    hangman_player.ending_phrase = "You won!"
                    Hangman.people_playing_list.pop(ctx.author.id)
                    return

                hangman_player.ending_phrase = "Correct guess."
            else:
                hangman_player.lives -= 1
                hangman_player.guesses.append(letter)

                if hangman_player.lives == 0:
                    Hangman.people_playing_list.pop(ctx.author.id)
                    hangman_player.ending_phrase = (
                        "You lost! The word was: " + hangman_player.word
                    )
                    return

                hangman_player.ending_phrase = "Wrong guess."

    async def refresh_messages(self, hangman_player):
        joined_guesses = str(", ".join(hangman_player.guesses))
        joined_dashed_word = str(" ".join(hangman_player.dashed_word))
        await hangman_player.guess_message.edit(
            content=("Guess: " + joined_guesses)
        )
        await hangman_player.lives_message.edit(
            content=("Lives: " + str(hangman_player.lives))
        )
        await hangman_player.word_message.edit(
            content=("Word: " + joined_dashed_word)
        )
        await hangman_player.ending_message.edit(
            content=(hangman_player.ending_phrase)
        )

    async def return_specific_hangman_player(self, id) -> object:
        return Hangman.people_playing_list.get(id)

    async def is_he_playing(self, id) -> bool:
        if id in Hangman.people_playing_list:
            return True
        else:
            return False

    async def is_every_letter_in_word(self, hangman_player) -> bool:
        """"
        Checking if player guessed all right letters

        Returning True if the condition is met
        """
        copy_of_dashed_word = hangman_player.dashed_word.copy()

        for letter in hangman_player.word:
            try:
                copy_of_dashed_word.remove(letter)
            except (ValueError):
                pass

        if not len(copy_of_dashed_word):
            return True
        else:
            return False

    async def reveal_some_letters(self, hangman_player, letter) -> None:
        """Replaces dashes with right guessed letter"""

        list_indexes_of_letter = [
            i for i, ltr in enumerate(hangman_player.word) if ltr == letter
        ]

        for j in list_indexes_of_letter:
            hangman_player.dashed_word[j] = letter


class HangmanPlayer:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.guesses: List[chr] = []
        self.lives = 7
        self.word = self.random_line_from_words()[:-1].upper()
        self.dashed_word = self.dashes_instead_letters(self.word)

        self.guess_message = None
        self.lives_message = None
        self.word_message = None
        self.ending_message = None
        self.ending_phrase = None

    def random_line_from_words(self) -> str:
        return random.choice(list(open("words.txt")))

    def dashes_instead_letters(self, word) -> List[chr]:
        """
        Returning list of dashes.

        Returns a list of dashes with the same length as the parameter.
        """
        list_of_dashes: List[str] = []
        for _ in word:
            list_of_dashes.append("-")

        return list_of_dashes


# --------- LEVEL 3 ----------
hangman = Hangman()


@bot.command(name="play_hangman")
async def play_hangman(ctx: commands.Context) -> None:

    if not await hangman.is_he_playing(ctx.author.id):

        hangman_player = HangmanPlayer(ctx.author.id, ctx.author.name)
        Hangman.people_playing_list[ctx.author.id] = hangman_player

        await hangman.play_hangman(ctx, hangman_player)

    else:
        await ctx.send("You are already playing!")


@bot.command(name="guess")
async def guess(ctx: commands.Context, letter: str) -> None:

    if await hangman.is_he_playing(ctx.author.id):

        hangman_player = (
            await hangman.return_specific_hangman_player(ctx.author.id))

        await hangman.guess_letter(ctx, hangman_player, letter.upper())
        await hangman.refresh_messages(hangman_player)

    else:
        await ctx.send("you have to create a new game first - !play_hangman")

    await ctx.message.delete()


bot.run(TOKEN)
