# scmachinery-troubleshooting
# Inspiration

A few weeks prior to HackNotts, one of my friends back in Japan asked me to build a troubleshooting portal website for his workplace, as the workers there struggle daily to fix machine troubles without any references.

# What it does

The website is basically a CRUD application with a Firestore database. After creating an account on the website, you can post information on a machine trouble and its troubleshooting method, and view and search for similar troubles in the past.

# How I built it

I used Flask and HTML for front- and back-end. For a cloud server and a database, I hosted on GCP and Firebase, respectively. It needed to be able to be accessed from different sorts of devices like a PC or a smartphone so I decided to make a portal website instead of a mobile app. I really wanted to collaborate with other like-minded people but I decided not to, since it was a project for my friend and was needed to be built in Japanese.
