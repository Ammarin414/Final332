AWS 3-Tier Project: To-Do List

This is a simple To-Do List application built on a classic 3-Tier architecture using AWS services:

Frontend (Web Tier): S3 (Static Website Hosting)

Backend (App Tier): EC2 (running a Python Flask API)

Database (Data Tier): RDS (MySQL)

Project Structure

/
|-- app.py             # (Backend) Flask API server
|-- requirements.txt   # (Backend) Python dependencies
|-- index.html         # (Frontend) Main HTML file
|-- style.css          # (Frontend) CSS styles
|-- app.js             # (Frontend) JavaScript logic
`-- README.md          # This file


How to Deploy

Database (RDS):

Launch an RDS MySQL instance (Free Tier).

Note the Endpoint, username, and password.

Connect to it (e.g., via EC2) and run CREATE DATABASE tododb;

Backend (EC2):

Launch an Amazon Linux 2023 t2.micro EC2 instance.

In the Security Group, allow SSH (Port 22) and Custom TCP (Port 5000) from Anywhere (0.0.0.0/0).

SSH into the instance, install Git, Python3, and Pip.

git clone [YOUR_REPO_URL] and cd [YOUR_REPO_NAME]

pip3 install -r requirements.txt

Edit app.py and fill in the db_config with your RDS credentials.

Run the server: python3 app.py (or nohup python3 app.py & to run in background).

Frontend (S3):

Create a public S3 bucket.

Enable Static website hosting.

Add a Bucket Policy to allow public s3:GetObject.

Edit app.js and set the apiUrl variable to your EC2's Public DNS (e.g., http://ec2-xx-xx-xx.compute-1.amazonaws.com:5000).

Upload index.html, style.css, and the edited app.js to the bucket.

Test:

Open the S3 Bucket website endpoint URL in your browser.
