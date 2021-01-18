import requests
from bs4 import BeautifulSoup
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math
from time import sleep

'''
Manually defining the genres for each media, as for metacritic certain genres
don't have fully fleshed out top 100's (not enough entries, greatly negative
scores near the bottom, I chose only 75+ scores based on whether its top 100
user/metascore
'''
movie_genres = ["action", "adventure", "animation", "biography", "comedy",
          "documentary", "crime", "drama", "family", "fantasy", "history",
          "horror", "musical", "mystery", "romance", "sci-fi", "sport",
          "thriller", "war"]

tv_genres = ["actionadventure", "comedy",
             "documentary", "drama", "fantasy", "sciencefiction", "suspense"]

game_genres = ["action", "adventure", "fighting", "first-person", "flight",
               "platformer", "puzzle", "racing", "real-time", "role-playing",
               "simulation", "sports", "strategy", "third-person",
               "turn-based",]


#A dictionary for easy access to genres, and other important data depending on
#user input
media_to_genres = {"movies": (movie_genres, 'movie', ""), "tv": (tv_genres, 'season', ""),
                   "games": (game_genres, 'game', "/all")}


'''
Creating a simple array to be used for the string versions of the numbers 1,2,3,4
, because the html of metacritic is setup such that each top 100 list is split
into 4 sections
'''
list_split = ["one", "two", "three", "four"]

#another simple array to iterate over to change the url to meta/user score
score_types = ["metascore", "userscore"]


print("\n---- Welcome to the Metacritic Score Analyzer ----\n")

#Ask for user input, only accept certain input
while True:
    media_type = input("What media type would you like to analyze? "
                       "Input: 'tv', 'movies', 'games': ")
    if media_type not in ['tv', 'movies', 'games']:
        print("Not valid")
    else:
        break


#The overarching for loop that does two iterations, one for top 100 by user
# and one for top 100 by critic score
for types in score_types:
    print("\n")

    #Track various data for matplot purposes and calculation for data analysis
    data = []
    avg_critic_scores= []
    avg_user_scores = []

    critic_standard_deviations = []
    user_standard_deviations = []

    critic_variances =[]
    user_variances = []

    correlations = []

    sample_sizes = []

    print("analyzing: top 100 " + types + " -----------------")

    #Then iterate over each genre for the chosen user input using the dictionary
    for genre in media_to_genres[media_type][0]:
        #Track all scores for the genre, for standard deviation calculation
        critic_scores = []
        user_scores = []

        #set up beautifulsoup, with a highly segmented url to change to different
        #media and genres
        url = 'https://www.metacritic.com/browse/' + media_type + '/genre/' + \
              types + '/' + genre + media_to_genres[media_type][2] +'?view=detailed'
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.content, 'html.parser')
        sleep(0.5)
        sample_size = 0
        critic_score_sum = 0
        user_score_sum = 0

        #each top 100 list in metacritic is split into 4 mini lists through
        #the html, this loop simply gathers data from all of them
        for number in list_split:

            media_list = soup.find(class_="browse_list_wrapper " + number + " browse-list-large")

            media = media_list.find_all(class_="browse-score-clamp")
            #Isolate all elements of data through filtering of class
            for element in media:
                media_critic_score = element.find(class_="metascore_w large " + media_to_genres[media_type][1] + " positive")
                media_user_score = element.find(class_="metascore_w user large " + media_to_genres[media_type][1] + " positive")
                #If both scores, meta and user, are present in the review of the
                #movie/show/game, only then include it
                if media_critic_score is not None and media_user_score is not None:
                    sample_size += 1

                    critic_score = float(media_critic_score.text)
                    user_score = float(media_user_score.text) * 10

                    critic_score_sum += critic_score
                    user_score_sum += user_score

                    critic_scores.append(critic_score)
                    user_scores.append(user_score)


        #calculate average, add to previous arrays to display using matplotlib
        critic_score_avg = round(critic_score_sum / sample_size, 2)
        user_score_avg = round(user_score_sum / sample_size, 2)

        sample_sizes.append(sample_size)

        avg_critic_scores.append(critic_score_avg)
        avg_user_scores.append(user_score_avg)

        data.append((genre, sample_size, critic_score_avg, user_score_avg))

        #calculate standard deviation,variance, and correlation for both critic and user scores
        temp_nums1 = []
        temp_nums2 = []
        covariance_sum = 0
        for i in range(len(critic_scores)):
            num1 = critic_scores[i] - critic_score_avg

            temp_nums1.append(num1 ** 2)

            num2 = user_scores[i] - user_score_avg

            temp_nums2.append(num2 ** 2)

            covariance_sum += num1 * num2

        deviation_sum1 = sum(temp_nums1)
        critic_variance = round(deviation_sum1 / len(temp_nums1),2)
        critic_standard_deviation = round(math.sqrt(critic_variance),2)

        critic_standard_deviations.append(critic_standard_deviation)
        critic_variances.append(critic_variance)

        deviation_sum2 = sum(temp_nums2)
        user_variance = round(deviation_sum2 / len(temp_nums2),2)
        user_standard_deviation = round(math.sqrt(user_variance),2)

        user_standard_deviations.append(user_standard_deviation)
        user_variances.append(user_variance)


        correlation = round(covariance_sum / math.sqrt(deviation_sum1 * deviation_sum2), 2)
        correlations.append(correlation)

    #calculating averages to display in the graph
    avg_all_critic_score = round(sum(avg_critic_scores) /len(avg_critic_scores),2)

    avg_all_user_score = round(sum(avg_user_scores) / len(avg_user_scores),2)

    avg_critic_std_dev = round(sum(critic_standard_deviations) /len(critic_standard_deviations),2)

    avg_user_std_dev = round(sum(user_standard_deviations) /len(user_standard_deviations),2)

    avg_critic_variance = round(sum(critic_variances) /len(critic_variances),2)

    avg_user_variance = round(sum(user_variances) /len(user_variances),2)

    avg_correlation = round(sum(correlations)/ len(correlations), 2)



    #set up graphs using matplot

    #number of bars to display, dependent on length of genres
    genre_length = len(media_to_genres[media_type][0])

    x = np.arange(genre_length)
    width = 0.25

    #set up figure and axis, then tune the size of the figure and set up bars
    figure, axis = plt.subplots()
    figure.set_size_inches(genre_length + 5, 6)

    bar1 = axis.bar(x-width/2, avg_critic_scores, width, label='Avg. Critic Scores')
    bar2 = axis.bar(x+width/2, avg_user_scores, width, label='Avg. User Scores')

    #setting up the legend
    handles, labels = axis.get_legend_handles_labels()
    entry1 = mpatches.Patch(color = 'm', label='Standard Deviation')
    entry2 = mpatches.Patch(color = 'lightgreen', label = 'Variance')
    entry3 = mpatches.Patch(color = 'gold', label = 'Correlation')
    handles.append(entry1)
    handles.append(entry2)
    handles.append(entry3)
    axis.legend(handles=handles, bbox_to_anchor=(1.04, 1))

    #handling x and y axis
    axis.set_ylabel('Scores')
    axis.set_title('Top 100 by ' + types + ' for ' + media_type)
    axis.set_xticks(x)
    x_axis = []
    for i in range(len(media_to_genres[media_type][0])):
        x_axis.append(media_to_genres[media_type][0][i] + '\n\nN = ' + str(sample_sizes[i]))
    axis.set_xticklabels(x_axis)

    #goes through each bar and labels the appropiate data
    for i in range(len(bar1)):
        height = bar1[i].get_height()
        axis.annotate(height, xy=(bar1[i].get_x() + bar1[i].get_width() /2, height),
                      xytext=(0, 4), textcoords="offset points",
                      ha='center', va='bottom')
        axis.annotate(critic_standard_deviations[i], xy=(bar1[i].get_x() + bar1[i].get_width() /2, height / 2 + 5),
                      xytext=(0, 4), textcoords="offset points",
                      ha='center', va='bottom', color = 'm', weight = 'bold')
        axis.annotate(critic_variances[i], xy=(bar1[i].get_x() + bar1[i].get_width() /2, height / 2 - 5),
                      xytext=(0, 4), textcoords="offset points",
                      ha='center', va='bottom', color = 'lightgreen', weight = 'bold')
        axis.annotate(correlations[i], xy=(bar1[i].get_x() + bar1[i].get_width(), height / 2 - 20),
                      xytext=(0, 4), textcoords="offset points",
                      ha='center', va='bottom', color = 'gold', weight = 'bold')
    for i in range(len(bar2)):
        height = bar2[i].get_height()
        delta = 0
        if abs(avg_critic_scores[i] - height) <= 3:
            delta = 0.19
        axis.annotate(height, xy=(bar2[i].get_x() + bar2[i].get_width() /2 + delta, height),
                      xytext=(0, 4), textcoords="offset points",
                      ha='center', va='bottom')
        axis.annotate(user_standard_deviations[i], xy=(bar2[i].get_x() + bar2[i].get_width() /2 + delta, height / 2 + 5),
                      xytext=(0, 4), textcoords="offset points",
                      ha='center', va='bottom', color = 'm', weight = 'bold')
        axis.annotate(user_variances[i], xy=(bar2[i].get_x() + bar1[i].get_width() /2 + delta, height / 2 - 5),
                      xytext=(0, 4), textcoords="offset points",
                      ha='center', va='bottom', color = 'lightgreen', weight = 'bold')

    #add data to the sidebar in boxes
    axis.text(genre_length, 65, 'Avg. of all critic scores: ' + str(avg_all_critic_score), style='italic',
            bbox={'facecolor': 'tab:blue', 'pad': 10})
    axis.text(genre_length, 55, 'Avg. of all user scores: ' + str(avg_all_user_score), style='italic',
              bbox={'facecolor': 'tab:orange', 'pad': 10})
    axis.text(genre_length, 45, 'Avg. Critic Std. dev.: ' + str(avg_critic_std_dev), style='italic',
              bbox={'facecolor': 'm', 'alpha': 0.5, 'pad': 10})
    axis.text(genre_length, 35, 'Avg. User Std. dev.: ' + str(avg_user_std_dev), style='italic',
              bbox={'facecolor': 'm', 'alpha': 0.5, 'pad': 10})
    axis.text(genre_length, 25, 'Avg. Critic Variance: ' + str(avg_critic_variance), style='italic',
              bbox={'facecolor': 'lightgreen', 'alpha': 0.5, 'pad': 10})
    axis.text(genre_length, 15, 'Avg. User Variance: ' + str(avg_user_variance), style='italic',
              bbox={'facecolor': 'lightgreen', 'alpha': 0.5, 'pad': 10})
    axis.text(genre_length, 5, 'Avg. Correlation: ' + str(avg_correlation), style='italic',
              bbox={'facecolor': 'gold', 'alpha': 0.5, 'pad': 10})
    figure.tight_layout()


plt.show()
