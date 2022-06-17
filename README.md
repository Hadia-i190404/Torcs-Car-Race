# Torcs-Car-Race
Torcs car simulation thorugh AI
I was provided with the Torcs Car simulator and was asked to make the car complete the race via predicting what move to make.
In the intitial stage, I added controls to the game and played the game myself. I did this to collect data ("gamedata.csv"), which was processed later and used for prediction.
I used Decision Tree Regressor as my module. Th reason for choosing this module was it's continuous data reading and high accuracy considering the data I collected.
Once the data was collected, I processed the data, split it into test and trained data, used the decsion tree regressor's in built prediction function. 
Some light coding and my car was able to predict from the given data and complete its race.
