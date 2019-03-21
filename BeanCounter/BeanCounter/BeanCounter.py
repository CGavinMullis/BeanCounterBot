##Bean Counter Project
##
##Author: Gavin Mullis
##Date Last Modified: March 21st, 2019
##
##This Bot keeps track of the bean counting channel statistics through the use of
##the Discord API and Google Sheets API


############################################################################################################

##Header Files
import discord
import time
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials


############################################################################################################

##Functions for use in Events

##Determines if the inputChar is a digit or not
##Turns out there is a built in function called isdigit() that does the same thing
def is_digit(inputChar):    
    if inputChar >= '0' and inputChar <='9':
        return True
    else:
        return False

##Determeines if the inputString contains any digits or not
def has_numbers(inputString):
    return any(is_digit(char) for char in inputString)

#Converts a given input string into an integer of the earliest string of consecutive numbers
def string_to_number(inputString):

    outputNum = ""          ##Initialized as Empty string
    numsFound = False       ##Flag to denote when first complete number has been found
    lastCharIsNum = False   ##Flag to denote when last char is a num
    i = 0   

    ##While there are characters to search or a number has not been found
    while i < len(inputString) and not numsFound:

        ##Digits have previously been found and the current character is not a digit
        if(not is_digit(inputString[i]) and lastCharIsNum): 
            numsFound = True

        ##Current Character is a digit
        elif(is_digit(inputString[i])):
            outputNum = outputNum + inputString[i]
            lastCharIsNum = True

        ##Current Character is not a digit but no digits have been found yet
        else:
            pass

        ##Move onto next character
        i += 1

    return int(outputNum)


##End of Functions


############################################################################################################

##Initialization of Bot

##Opening Google Sheet containing records
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('BeanCounterBot-33ae94c26a20.json', scope)
gc = gspread.authorize(credentials)             ##Validate Credentials
wks = gc.open('BeanCounter').sheet1             ##Open Sheet

##Extract Important Variables from Sheet
expectedNumber = int(wks.acell('A4').value)     
successfulCounts = int(wks.acell('A6').value)   
unsuccessfulCounts = int(wks.acell('A8').value) 
numOfStreaks = int(wks.acell('A10').value)     
previousAuthor = str(wks.acell('A12').value)    
highestCount = int(wks.acell('A14').value)

##Opening token.txt and preparing variables to connect to Discord Client
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

token = read_token()
client = discord.Client()


############################################################################################################

##Client Events Below

##On Message Event
@client.event
async def on_message(message):
    
    global expectedNumber, successfulCounts, unsuccessfulCounts, numOfStreaks, previousAuthor, highestCount
    id = client.get_guild(441695788951666692)   ##Server ID
    channels = {"beancountingchannel"}          ##Channel ID
    invalid_users = ["Bean Counter#5648"]       ##Bot ID

    ##Message is in the correct channel and not sent by the bot
    if str(message.channel) in channels and str(message.author) not in invalid_users:

        ##Message is a Command
        if message.content[0] == "!":

            if(message.content.find("!hiscore") != -1):
                await message.channel.send(f"""The Current Hiscore is {highestCount}.""")
            elif(message.content.find("!totals")!= -1):
                await message.channel.send(f"""There have been, {successfulCounts}, successful counts.\nAnd there have been, {unsuccessfulCounts} unsuccessful counts.""")
            else:
                await message.channel.send("Type !help for a list of commands")

        ##Message is a Count
        elif has_numbers(message.content):

            ##Successful Count
            if (string_to_number(message.content) == expectedNumber and message.author != previousAuthor) or (string_to_number(message.content) == expectedNumber and expectedNumber == 1):

                ##New HighScore
                if(expectedNumber > highestCount):
                    highestCount = expectedNumber
                    wks.update_acell('A14', str(highestCount))

                ##Update Variables and Sheet
                expectedNumber += 1
                successfulCounts += 1
                previousAuthor = message.author
                wks.update_acell('A4', str(expectedNumber))
                wks.update_acell('A6', str(successfulCounts))
                wks.update_acell('A12', str(previousAuthor))

            ##Unsuccessful Count
            else:

                ##Streak Break Messages
                if(message.author == previousAuthor and string_to_number(message.content) == expectedNumber):
                    await message.channel.send(f"""Oof, you broke the streak by counting twice in a row.""")
                elif(message.author != previousAuthor or expectedNumber == 1):
                    await message.channel.send(f"""Awww, you broke the streak with, {string_to_number(message.content)}, when we were expecting, {expectedNumber}.""")
                else:
                    await message.channel.send(f"""Wow you suck. Not only did you count twice in a row, but it wasn't even the right number.""")

                ##Reset Expected Number and Update the Sheet
                expectedNumber = 1
                unsuccessfulCounts += 1
                numOfStreaks += 1
                previousAuthor = message.author
                wks.update_acell('A4', str(expectedNumber))
                wks.update_acell('A8', str(unsuccessfulCounts))
                wks.update_acell('A10', str(numOfStreaks))
                wks.update_acell('A12', str(previousAuthor))

        ##Message is only text
        else:
            pass    ##Do Nothing
    ##Message is either in the incorrect channel or sent by the bot
    else:
        pass


############################################################################################################

##Run Client with Token
client.run(token)



