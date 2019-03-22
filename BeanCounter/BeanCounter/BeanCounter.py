##Bean Counter Project
##
##Author: Gavin Mullis
##Date Last Modified: March 21st, 2019
##
##This Bot keeps track of the bean counting channel statistics through the use of
##the Discord API and Google Sheets API
##Only 500 writes to the Sheets may be performed in 100 seconds
##Ecah Message recieved by the bot performs approximately 50 writes. 
##So if 6 messages are recieved within 1 minute a crash will occur 

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

print("Opening Google Sheet...")
##Opening Google Sheet containing records
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('BeanCounterBot-33ae94c26a20.json', scope)
gc = gspread.authorize(credentials)             ##Validate Credentials
wks = gc.open('BeanCounter').sheet1             ##Open Sheet

print("Sheet Opened...\nExtracting Data...")
##Extract Important Variables from Sheet and Create Empty Lists

##General Statistics and Totals
expectedNumber = int(wks.acell('A4').value)     
successfulCounts = int(wks.acell('A6').value)   
unsuccessfulCounts = int(wks.acell('A8').value) 
numOfStreaks = int(wks.acell('A10').value)     
previousAuthor = str(wks.acell('A12').value)   
highestCount = int(wks.acell('A14').value)
topFiveStreaks = []
lastStreak = int(wks.acell('A22').value)
topFiveCounters = []
topFiveLosers = []
lastFiveStreaks = []
avgStreak = float(wks.acell('A42').value)
numOfUsers = int(wks.acell('B2').value)

##User Specific Statistics and Totals
users = []
userCounts = []
userFails = []

##Fill List Variables with Sheet Data
for i in range(5):
    topFiveStreaks.append(int(wks.cell((i+16), 1).value))  ##A16-A20
    topFiveCounters.append(str(wks.cell((i+24), 1).value)) ##A24-A28
    topFiveLosers.append(str(wks.cell((i+30), 1).value))   ##A30-A34
    lastFiveStreaks.append(int(wks.cell((i+36), 1).value)) ##A36-A40
for j in range(numOfUsers):
    users.append(str(wks.cell((j+4), 2).value))            ##B4-B?
    userCounts.append(int(wks.cell((j+4), 3).value))       ##C4-C?
    userFails.append(int(wks.cell((j+4), 4).value))        ##D4-D?

print("Data Extracted, Connecting to Discord Client...")

##Opening token.txt and preparing variables to connect to Discord Client
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

token = read_token()
client = discord.Client()

print("Delay for API...")
time.sleep(1)
print("uwu")
time.sleep(1)
print("owo")
time.sleep(1)
print("uvu")
time.sleep(1)
print("Delay Over")

############################################################################################################

##Client Events Below

##On Message Event
@client.event
async def on_message(message):
    
    global expectedNumber, successfulCounts, unsuccessfulCounts, numOfStreaks, previousAuthor, highestCount
    global topFiveStreaks, lastStreak, topFiveCounters, topFiveLosers, lastFiveStreaks, avgStreak, numOfUsers
    global users, userCounts, userFails
    id = client.get_guild(441695788951666692)   ##Server ID
    channels = {"beancountingchannel"}          ##Channel ID
    invalid_users = ["Bean Counter#5648"]       ##Bot ID


    ##Message is in the correct channel and not sent by the bot
    if str(message.channel) in channels and str(message.author) not in invalid_users:

        ##Message is a Command
        if message.content[0] == "!":

            if(message.content.find("!hiscore") != -1):
                await message.channel.send(f"""The Current Hiscore is {highestCount}.""")
            elif(message.content.find("!totals") != -1):
                await message.channel.send(f"""There have been, {successfulCounts}, successful counts.\nAnd there have been, {unsuccessfulCounts} unsuccessful counts.""")
            elif(message.content.find("!user") != -1):
                if str(message.author) in users:
                    userIndex = users.index(str(message.author))
                    await message.channel.send(f"""User {message.author} has {userCounts[userIndex]} successful counts and {userFails[userIndex]} unsuccessful counts.""")
                else:
                    await message.channel.send(f"""{message.author} has not yet participated in the counting of beans.""")
            else:
                await message.channel.send("Type !help for a list of commands")

        ##Message is a Count
        elif has_numbers(message.content):
        
            ##Check if User is in List of Users
            userIndex = 0

            ##User is in the list
            if str(message.author) in users:
                userIndex = users.index(str(message.author))

            ##This is a new User. They should be added to the List
            else:
                ##Update Variables
                users.append(str(message.author))
                userCounts.append(0)
                userFails.append(0)
                userIndex = users.index(str(message.author))
                numOfUsers += 1
                ##Update Sheet
                wks.update_acell('B2', str(numOfUsers))
                wks.update_cell((4 + userIndex), 2, users[userIndex])
                wks.update_cell((4 + userIndex), 3, userCounts[userIndex])
                wks.update_cell((4 + userIndex), 4, userFails[userIndex])
                time.sleep(1)   ##Delay to keep API Happy


            ##Successful Count
            if ((string_to_number(message.content) == expectedNumber) and (message.author != previousAuthor)) or ((string_to_number(message.content) == expectedNumber) and (expectedNumber == 1)):

                ##New HighScore
                if(expectedNumber > highestCount):
                    highestCount = expectedNumber
                    wks.update_acell('A14', str(highestCount))

                ##Update Variables
                expectedNumber += 1
                successfulCounts += 1
                userCounts[userIndex] += 1
                previousAuthor = message.author

                ##Update Sheet
                wks.update_acell('A4', str(expectedNumber))
                wks.update_acell('A6', str(successfulCounts))
                wks.update_acell('A12', str(previousAuthor))
                wks.update_cell((4 + userIndex), 3, userCounts[userIndex])
                time.sleep(1)   ##Delay to keep API Happy


            ##Unsuccessful Count
            else:

                ##Streak Break Messages
                if(message.author == previousAuthor and string_to_number(message.content) == expectedNumber):
                    await message.channel.send(f"""Oof, you broke the streak by counting twice in a row.""")
                elif(message.author != previousAuthor or expectedNumber == 1):
                    await message.channel.send(f"""Awww, you broke the streak with, {string_to_number(message.content)}, when we were expecting, {expectedNumber}.""")
                else:
                    await message.channel.send(f"""Wow you suck. Not only did you count twice in a row, but it wasn't even the right number.""")

                ##Update Variables
                lastStreak = expectedNumber - 1
                expectedNumber = 1
                unsuccessfulCounts += 1
                numOfStreaks += 1
                userFails[userIndex] += 1
                previousAuthor = message.author

                ##Last Five Streaks
                lastFiveStreaks.reverse()
                lastFiveStreaks.append(lastStreak)
                lastFiveStreaks.reverse()
                lastFiveStreaks.pop()

                ##Average Streak
                avgStreak = (((numOfStreaks - 1)*avgStreak) + lastStreak) / numOfStreaks

                ##Update Sheet
                wks.update_acell('A22', str(lastStreak))
                wks.update_acell('A4', str(expectedNumber))
                wks.update_acell('A8', str(unsuccessfulCounts))
                wks.update_acell('A10', str(numOfStreaks))
                wks.update_acell('A12', str(previousAuthor))
                wks.update_acell('A42', str(avgStreak))
                wks.update_cell((4 + userIndex), 4, userFails[userIndex])
                for i in range(5):
                    wks.update_cell((36+i), 1, lastFiveStreaks[i])
                time.sleep(1)   ##Delay to keep API Happy

            ###########################################################################

            ##Evaluate Rankings

            ###########################################################################

            ##Top 5 Streaks
            topFiveStreaks.append(expectedNumber-1)
            topFiveStreaks.sort()
            topFiveStreaks.reverse()
            topFiveStreaks.pop()    ##Remove the smallest streak

            for i in range(5):
                wks.update_cell((16+i), 1, topFiveStreaks[i])

            ###########################################################################

            ##Top 5 Counters
            tempList = userCounts.copy()
            tempList.sort()
            tempList.reverse()

            ##More than 5 Users
            if(numOfUsers >= 5):
                for i in range(5):
                    topFiveCounters[i] = users[userCounts.index(tempList[i])]
                    wks.update_cell((24 + i), 1, topFiveCounters[i])

            ##More than 0 users but less than 5 users
            else:
                for i in range(numOfUsers):
                    topFiveCounters[i] = users[userCounts.index(tempList[i])]
                    wks.update_cell((24 + i), 1, topFiveCounters[i])

            ###########################################################################

            ##Top 5 Losers
            tempList = userFails.copy()
            tempList.sort()
            tempList.reverse()

            ##More than 5 Users
            if(numOfUsers >= 5):
                for i in range(5):
                    topFiveLosers[i] = users[userFails.index(tempList[i])]
                    wks.update_cell((30 + i), 1, topFiveLosers[i])

            ##More than 0 users but less than 5 users
            else:
                for i in range(numOfUsers):
                    topFiveLosers[i] = users[userFails.index(tempList[i])]
                    wks.update_cell((30 + i), 1, topFiveLosers[i])
            
            ###########################################################################

        ##Message is only text
        else:
            pass    ##Do Nothing

    ##Message is either in the incorrect channel or sent by the bot
    else:
        pass


############################################################################################################
print("Connected to Discord\nAwaiting Messages...")
##Run Client with Token
client.run(token)



