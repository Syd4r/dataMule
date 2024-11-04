# dataMule
To set up the repository, first clone the repo.

Then run the command: pip install -r requirements.txt

Look in the file helper_functions.py and change the admin account creation at the bottom to your details. Then run python helper_functions.py

If you want to check out the hawkin data page, make a .env file with:

HD_REFRESH_TOKEN="REPLACE WITH THE API TOKEN"

REGION=Americas

ACCESS_TOKEN=

TOKEN_EXPIRATION=

CLOUD_URL=

Then try running app.py, if port 5000 is taken, switch your port to something else.
