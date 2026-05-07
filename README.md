This is a Donation Assistance application that aims to provide an additional solution for Non-Profits, with a focus on the needs of smaller Non-Profits.
This project serves the purpose of inspiring me to create real-world solutions that build in complexity, security and features provided as we continue to
grow as developers. 

As of May 5th, 2026, we have created a primitive but real-world program which utilizes SerpApi to gather the image and product names from Amazon. The goal
is to implement official Amazon API to take advantage of the robust features available and provide a fluid user experience. 

To run this program you would need to clone the repository to your local system and then perform the following:
- create a virtual environment
- pip install the requirements.txt dependencies inside of the root directory that is home to the virtual environment. 
- Create a superuser for admin login and database input (In terminal)
- Create a database (In terminal)
- Register with SerpAPI to get an API key: https://serpapi.com/
- Store the API key in a .env file as SERPAPI_KEY
- I believe you will need to collect the static files. 
- Create an Amazon wishlist and fill it with items
- Run the server (In terminal)
- Open browser with localhost and port identified in terminal.
- Navigate to /admin and login using the credential created with createsuperuser
- Select add item
- When creating items in the admin interface, you need to paste the product url into the appropriate field.
- Set your thresholds. (lvl_1, lvl_2, ... I will probably redefine these variables or section them off with a more appropriate description to avoid confusion.)
- Set remaining variables (the lighter color variables do not need input; these are automated... I will work on removing these visually from the admin form)
- Save the Item object. This populates the image, price and product name.
- Repeat for multiple items
- You should now have a populated donation list that you can add and remove from and the option to proceed to Amazon. 

