# rocketico

This project tries to simulate a real world ICO through the emission of an ERC-20 token called Rocket Token.

First of all start your local blockchain (i.e. Ganache )

To set Up the project first compile and run the tests for the smart contracts installing truffle and runnig "truffle test" 
inside /truffle directory

Run "pip install -r requirements.txt" to install all the dependencies for the django project.

After makemigrations and migrate create a superuser.
Run the server and log as the superuser just created.

Select control page, fill in the form with the required data and press start sale button ( admin private key is the private key 
of the admin account i.e. ganache account 0 )

You shuold see two contract creation on your local blockchain transactions.

The project is ready, just register a new user send test ether to it ( superusers can do it in sendEther page) and try to buy
an amount of Rocket Token using the form in the dashboard page. You should see your balance in ether and rocket updated and a change
in the percentage of tokens sold in the home page.


Luca Pedrazini


