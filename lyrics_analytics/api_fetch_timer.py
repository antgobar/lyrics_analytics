# The lyricsovh API returns lyrics of a given artist + song title
# The same artist + song title cannot be fetched within 2 minutes
# If done an empty result is returned
# These set of functions read and write unix time stamps in order
# To be used in combination with another function to alert the user
# if they are calling the same artist + song title within 120 seconds

import time as t
import csv

def write_time(artists):
    current_time = int(t.time())
    with open('lyrics_analytics/api_timing_record.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([current_time])
        writer.writerow(artists)

def read_time():
    read_list = []
    with open('lyrics_analytics/api_timing_record.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            read_list.append(row)
    return read_list

def check_api_calls(artist_new):
    wait_time = 120
    read_list = read_time()
    time_elapsed = round(t.time()) - int(read_list[0][0])
    artist_old = read_list[1]
    time_until = wait_time - time_elapsed
    if time_elapsed < wait_time and any(artist in artist_new for artist in artist_old):
        print(f'''You are calling {artist_new}
Previously called {artist_old} within the last {wait_time} seconds
You may not get all their lyrics.
Please wait {time_until} seconds to call the same artist again :)''')
        return False
    
    else:
        return True
