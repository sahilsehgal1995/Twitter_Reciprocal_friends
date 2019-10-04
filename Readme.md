About:
Program for finding reciprocal friends of 100 users who are connected internally.
Following are the steps taken to reach the final social media graph.
1. Enter root user twitter ID from where you want to initiate the search
2. Twitter ID entered in first step is passed to search user function which fetch corresponding user ID.
3. The root user ID is pushed to a queue.
4. Find reciprocal friend (users who are in both the lists friends and followers) IDs.
5. Reciprocal friend IDs found in previous step are sent to user lookup API call which returns the profile of every user.
6. Sort the profiles in descending order based on followers count.
7. Take first 5 followers and push them to queue.
8. For every single element in queue, fetch their reciprocal friends till total user count doesn't reach 100.
9. Use networkx package to generate connectivity graph and save it in image using matplotlib.pyplot package.
10. Find the average distance and diameter of graph.


Requirements:
1. Python 3

Modules:
1. sys - pip install sys | For printing system standard errors
2. time - pip install time | For adding a timeout so that program execution can be halted
3. urllib.request - pip install urllib | For handling http network error
4. http.client - pip install http | For handling http network error
5. twitter - pip install twitter | Official Twitter api python package
6. networkx - pip install networkx | For creating a graph and finding average distance and diameter
7. matplotlib.pyplot - pip install matplotlib | | For generating an image file from the graph

How to Run:
python3 assignment1.py

@Copyright Sahil Sehgal | SU ID: 343-933-724