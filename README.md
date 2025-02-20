Minecraft Server with Ngrok

This repository contains the setup instructions for running a Minecraft server (version 1.21.4) using Ngrok for easy multiplayer access.

1. Prerequisites

A computer with macOS or Linux

Java 21 or above installed

Ngrok account (free or paid)

Python 3 installed

2. Download and Set Up Minecraft Server

2.1 Download the Server File

Go to the official Minecraft Server Download page.

Download the latest minecraft_server.1.21.4.jar file.

Move it to a dedicated folder (e.g., minecraft-server).

2.2 Initial Server Setup

Open a terminal and navigate to the server folder:

cd path/to/minecraft-server

Run the server for the first time:

java -Xmx12G -Xms12G -jar minecraft_server.1.21.4.jar nogui

The server will generate some files and then stop. Open eula.txt, change eula=false to eula=true, and save the file.

Start the server again:

java -Xmx12G -Xms12G -jar minecraft_server.1.21.4.jar nogui

3. Set Up Ngrok for Port Forwarding

3.1 Install Ngrok

If you haven't installed Ngrok yet, use Homebrew:

brew install ngrok/ngrok/ngrok

3.2 Authenticate Ngrok

Sign up for a free account at Ngrok.

Get your authentication token from the Ngrok Dashboard.

Run the following command to authenticate Ngrok:

ngrok config add-authtoken YOUR_AUTH_TOKEN

3.3 Enable Billing (for TCP tunnels)

Ngrok requires a payment method to enable TCP tunnels. Add a card in the billing section:🔗 Ngrok Billing Dashboard

3.4 Start the Server Using Python

After setting up your Ngrok account, run the Python script included in this repository to start the server. Make sure you have Java 21 or above installed before proceeding.

Run the script:

python3 start_server.py

4. Join the Minecraft Server

Run the Python script to get the public server address.

Copy the Ngrok TCP URL from the output (e.g., tcp://xyz.ngrok.io:xxxxx).

Open Minecraft, go to Multiplayer, and click Direct Connect.

Paste the Ngrok TCP URL and join the server!

5. Notes

Ensure your firewall allows connections to Minecraft.

The server runs in offline mode by default.

You can modify server.properties for additional configurations.

Enjoy your multiplayer Minecraft server! 🎮