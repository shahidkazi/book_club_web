<div align="center">
  <img src="screens/banner.png" /><br/>
  Simple Python/Firebase based website for book lovers to have their own website for book sharing and reviews
</div>

# Description

Simple and ready Python based website which you can use for your own bookclub, to share, rate and comments on book listings and reviews. 

The site is mobile friendly and has features like adding book with rating and review, liking and commenting on other people's books, Searching and filtering to get the books you want.

Also contains an admin login which gives access to manage all user's books and also for managing genes for the books.

Feel free to customize and use but do not forget to keep credit for me :-)

# Index
- [Technology Stack](#technology-stack)
- [How To Use](#how-to-use)
- [Screenshots](#screenshots)

# Technology Stack

1. Python Flask (for backend code)
2. Google Firestore (JSON based No-SQL database for storage)
3. Google Cloud for hosting (Free Tier is good enough)
4. Google Firebase (Application and free friendly domain)

# How To Use

**Will add a better guide soon, but if you are tech savvy / programmer - the steps below should not be difficult to decipher

1. Create a [Google Firebase](https://console.firebase.google.com) Account
2. Create a project for the bookclub for hosting your site and database
3. Once the account is created, go to 'Hosting' and add a new web app. Choose a name wisely since this will become part of the url (e.g. bookclub.web.app)
4. Go to Firestore database and create a new database, use 'default' database, since this is part of the Free Tier (refer to [Firebase QuickStart](https://firebase.google.com/docs/firestore/quickstart))
5. Note the credentials for the database to be updated to the website code
6. In the console, on the top left 'Project Overview' go to Usage and Billing and change from Free Tier to Pay as You Go Blaze plan by adding a payment method (dont worry it wont be too expensive unless you have a very heavy usage - I pay less than $0.50 per month for 17+ users) on a live imeplementation.
7. The project will also be available in [Google Cloud Console](https://console.cloud.google.com)
8. Clone and download the code to your local machine
9. If you want to modify code/update site locally then you need
   - Python
   - IDE (Visual Studio Code / PyCharm / etc)
10. Update the Firestore Key to the code and the email address for the admin (this accounr is the one for sending reset password and welcome emails). You will need to enable 2FA and get an app password for gmail to work via python (refer to [this thread](https://support.google.com/accounts/thread/270448277/generate-a-16-digit-app-password-for-a-python-application?hl=en))
11. Open the code and run app.py - this will open a local server and host the site for you to test
12. You may want to change the branding (banner, name, etc)
13. Once ready, install the firebase cli and google cloud cli
14. Use this guide to identify the commands to first build and deploy to Google Cloud as a service and then deploy to Firebase so that the site is served via the domain created in Firebase hosting [Flask apps on Firebase](https://medium.com/firebase-developers/hosting-flask-servers-on-firebase-from-scratch-c97cfb204579)

# Screenshots


Feel free to reach out to me if you need any help.
