import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
import glob
import pytz
from datetime import datetime

file_path = "../your_activity_across_facebook/messages/inbox/katarinavatrtova_6327591163970896/message_1.json"
dynamo = 'your_activity_across_facebook\messages\inbox\dynamopodhradova_1247663678672962'
chiara = "D:/6_Data Analysis/5of8-facebook-100010947246070-05_12_2023-RIBP7sSP/your_activity_across_facebook/messages/inbox/chiaranemethova_4063628567025807"
kata = "D:/6_Data Analysis/5of8-facebook-100010947246070-05_12_2023-RIBP7sSP/your_activity_across_facebook/messages/inbox/katarinavatrtova_6327591163970896"



def custom_decode(s):
    ''' Decodes special characters for terminal output '''
    try:
        return s.encode('raw_unicode_escape').decode('utf8')
    except:
        return s

def total_time(start, end):
    start = pd.Timestamp(start).to_pydatetime().date()
    end = pd.Timestamp(end).to_pydatetime().date()

    delta = end - start

    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = delta.days % 30

    return years, months, days

def read_json_files(folderpath):
    ''' Reads all json files and returns start_date, end_date, conversation title, df.participants, df.messages '''
    json_files = glob.glob(f'{folderpath}\*.json', recursive=True)
    #print(f'Available json files: {json_files}')
    all_messages = pd.DataFrame()  # initiates empty messages dataframe

    for i, json_file in enumerate(json_files):
        #print(f'Reading file no. {i + 1}')
        with open(json_file, 'r', encoding='raw_unicode_escape') as file:
            raw_data = json.load(file)  # read raw data file
            if i == 0:
                conversation_title = custom_decode(raw_data['title'])  # fetch conversation title
                participants = pd.DataFrame.from_dict(raw_data['participants'])  # fetch participant names
            new_messages = pd.DataFrame.from_dict(raw_data['messages'])  # fetch messages in this file
            all_messages = pd.concat([all_messages, new_messages], axis=0)  # concatenate new and old file messages
            all_messages = all_messages.reset_index(drop=True)  # reset index of the dataframe

    all_messages['timestamp_ms'] = pd.to_datetime(all_messages['timestamp_ms'], unit='ms', utc=True)
    all_messages['timestamp_local'] = all_messages['timestamp_ms'].dt.tz_convert(pytz.timezone('Europe/Bratislava'))
    start_date = all_messages['timestamp_local'].min()
    end_date = all_messages['timestamp_local'].max()
    all_messages['sender_name'] = all_messages['sender_name'].apply(custom_decode)
    all_messages['content'] = all_messages['content'].apply(custom_decode)

    total_time_bundle = total_time(start_date, end_date)
    #print(all_messages)
    #print('Done reading files!')
    return start_date, end_date, conversation_title, participants, all_messages, total_time_bundle


def just_get_total_messages(folderpath):
    r = {'title': [], 'total_messages': []}
    child_folders = glob.glob(f'{folderpath}\*')

    for i, child in enumerate(child_folders):
        #print(f'Doing folder {i + 1}')
        try:
            json_files = glob.glob(f'{child}\*.json', recursive=True)
            # print(f'Available json files: {json_files}')
            all_messages = pd.DataFrame()  # initiates empty messages dataframe

            for i, json_file in enumerate(json_files):
                # print(f'Reading file no. {i + 1}')
                with open(json_file, 'r', encoding='raw_unicode_escape') as file:
                    raw_data = json.load(file)  # read raw data file
                    if i == 0:
                        conversation_title = custom_decode(raw_data['title'])  # fetch conversation title
                    new_messages = pd.DataFrame.from_dict(raw_data['messages'])  # fetch messages in this file
                    all_messages = pd.concat([all_messages, new_messages], axis=0)  # concatenate new and old file messages
                    all_messages = all_messages.reset_index(drop=True)  # reset index of the dataframe

            r['total_messages'].append(len(all_messages['timestamp_ms']))
            r['title'].append(conversation_title)
            #print('success')
        except:
            #print('failed')
            continue

    #print(len(r['title']))
    #print(len(r['total_messages']))
    results_df = pd.DataFrame().from_dict(r)
    results_df = results_df.sort_values(by='total_messages')[::-1]
    results_df.to_csv(f'{folderpath}/absolute_total_comparison.csv')
    #print(results_df)


def hourly_activity_histogram(messages_df, output_directory, graph_title, start, end, grid_on, c_palette):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date() # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date() # global and local end

    filtered_df = messages_df[(messages_df['timestamp_local'].dt.date >= g_start) & (messages_df['timestamp_local'].dt.date <= g_end)]  # filter only the dates that are within the range
    messages_df['hour'] = filtered_df['timestamp_local'].dt.hour
    hourly_counts = messages_df['hour'].value_counts().sort_index()

    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    # sns.set_palette(c_palette)

    fig = plt.figure(figsize=(10, 6))
    hist, bins, _ = plt.hist(messages_df['hour'], bins=range(25), edgecolor='black',
                             label=f'Total Messages: {len(filtered_df)}', zorder=2)

    max_hour = hourly_counts.idxmax()
    max_count = hourly_counts.max()

    max_hour_index = list(bins).index(max_hour)
    plt.bar(max_hour_index + 0.5, hist[max_hour_index], color='red', edgecolor='black',
            label=f'Most Active Hour ({int(max_hour)} h): {max_count} Messages', width=1, zorder=3)

    plt.title(f'{graph_title} Chat Activity per Hour ({g_start.strftime('%d/%m/%Y')} - {g_end.strftime('%d/%m/%Y')})')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Messages')
    plt.legend()
    plt.grid(zorder=1)
    plt.xticks([i + 0.5 for i in range(24)], range(24))
    plt.xlim(0, 24)
    #plt.show()
    plt.savefig(f'{output_directory}/hourly_activity_histogram {graph_title} ({g_start.strftime('%d.%m.%Y')} - {g_end.strftime('%d.%m.%Y')}).png', dpi=300)


def daily_activity_histogram(messages_df, output_directory, graph_title, start, end, grid_on, c_palette):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date() # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date() # global and local end

    filtered_df = messages_df[(messages_df['timestamp_local'].dt.date >= g_start) & (messages_df['timestamp_local'].dt.date <= g_end)]  # filter only the dates that are within the range
    messages_df['day'] = filtered_df['timestamp_local'].dt.day
    daily_counts = messages_df['day'].value_counts().sort_index()

    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    # sns.set_palette(c_palette)

    fig = plt.figure(figsize=(10, 6))

    hist, bins, _ = plt.hist(messages_df['day'], bins=range(1, 33), edgecolor='black',
                             label=f'Total Messages: {len(filtered_df)}', zorder=2)

    max_day = daily_counts.idxmax()
    max_count = daily_counts.max()

    max_day_index = list(bins).index(max_day)
    plt.bar(max_day_index + 1.5, hist[max_day_index], color='red', edgecolor='black',
            label=f'Most Active Day ({max_day}.): {max_count} Messages', width=1, zorder=3)

    plt.title(f'{graph_title} Chat Activity per Day ({g_start.strftime('%d/%m/%Y')} - {g_end.strftime('%d/%m/%Y')})')
    plt.xlabel('Day of Month')
    plt.ylabel('Number of Messages')
    plt.legend()
    plt.grid(zorder=1)
    plt.xticks([i + 0.5 for i in range(1, 32)], range(1, 32))
    plt.xlim(1, 32)
    #plt.show()
    plt.savefig(f'{output_directory}/daily_activity_histogram {graph_title} ({g_start.strftime('%d.%m.%Y')} - {g_end.strftime('%d.%m.%Y')}).png', dpi=300)


def monthly_activity_histogram(messages_df, output_directory, graph_title, start, end, grid_on, c_palette):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date() # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date() # global and local end

    filtered_df = messages_df[(messages_df['timestamp_local'].dt.date >= g_start) & (messages_df['timestamp_local'].dt.date <= g_end)]  # filter only the dates that are within the range
    messages_df['month'] = filtered_df['timestamp_local'].dt.month
    monthly_counts = messages_df['month'].value_counts().sort_index()

    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    # sns.set_palette(c_palette)

    fig = plt.figure(figsize=(10, 6))

    hist, bins, _ = plt.hist(messages_df['month'], bins=range(1, 14), edgecolor='black',
                             label=f'Total Messages: {len(filtered_df)}', zorder=2)

    max_month = monthly_counts.idxmax()
    max_count = monthly_counts.max()

    max_hour_index = list(bins).index(max_month)
    plt.bar(max_hour_index + 1.5, hist[max_hour_index], color='red', edgecolor='black',
            label=f'Most Active Month ({max_month}): {max_count} Messages', width=1, zorder=3)

    plt.title(f'{graph_title} Chat Activity per Month ({g_start.strftime('%d/%m/%Y')} - {g_end.strftime('%d/%m/%Y')})')
    plt.xlabel('Month')
    plt.ylabel('Number of Messages')
    plt.legend()
    plt.grid(zorder=1)
    plt.xticks([i + 0.5 for i in range(1, 13)], range(1, 13))
    plt.xlim(1, 13)
    #plt.show()
    plt.savefig(f'{output_directory}/monthly_activity_histogram {graph_title} ({g_start.strftime('%d.%m.%Y')} - {g_end.strftime('%d.%m.%Y')}).png', dpi=300)


def find_longest_text(messages_df, start, end):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date() # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date() # global and local end

    filtered_df = messages_df[
        (messages_df['timestamp_local'].dt.date >= g_start) & (messages_df['timestamp_local'].dt.date <= g_end)]

    longest_string = filtered_df['content'].astype(str).apply(len).idxmax()
    longest_string_sender = filtered_df.loc[longest_string, 'sender_name']
    longest_string_content = filtered_df.loc[longest_string, 'content']
    longest_string_timestamp = filtered_df.loc[longest_string, 'timestamp_local']

    return longest_string_sender, longest_string_content, longest_string_timestamp

def submit_analysis(messages_df, output_directory, graph_title, start, end):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date() # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date() # global and local end

    cols_to_drop = []
    for item in ['sender_name', 'timestamp_ms', 'is_geoblocked_for_viewer', 'share', 'is_unsent']:
        if item in messages_df.columns:
            cols_to_drop.append(item)

    columns_to_analyze = messages_df.columns.drop(cols_to_drop)

    filtered_df = messages_df[
        (messages_df['timestamp_local'].dt.date >= g_start) & (messages_df['timestamp_local'].dt.date <= g_end)]

    overview = pd.DataFrame(index=filtered_df['sender_name'].unique())

    for column in columns_to_analyze:
        text_mes = filtered_df[['sender_name',
                             column]].dropna().reset_index()  # create new df with only text messages, drop NaN and reindex
        grouped_text = text_mes.groupby(
            by='sender_name').count()  # count total number of occurences of non NaN values in each column
        overview.loc[grouped_text.index, column] = grouped_text[
            column]  # insert into dataframe at specified index and column

    overview = overview.sort_values(by='timestamp_local')[::-1]

    total_messages = overview['timestamp_local'].sum()

    show_these = []

    for item in ['content', 'photos', 'videos', 'audio_files', 'gifs', 'files']:
        if item in overview.columns:
            show_these.append(item)

    fig, ax = plt.subplots(figsize=(10, 6))  # Set the figure size to 10x10 inches

    overview[show_these].plot.barh(ax=ax, rot=0, stacked=True)
    plt.gca().invert_yaxis()

    # Calculate the sum of each stacked column
    column_sums = overview[show_these].sum(axis=1)

    # Add numerical values on top of the combined bars
    for i, value in enumerate(column_sums):
        ax.text(value, i, f'{value:.0f}', ha='left', va='center', fontsize=10, color='black', rotation=45)

    plt.title(f'{graph_title} User comparison ({g_start.strftime('%d/%m/%Y')} - {g_end.strftime('%d/%m/%Y')})')
    plt.legend(loc=7)
    xlim = ax.get_xlim()[1]  # get x limit of the plot to plot text at 80% of total width
    plt.text(xlim * 0.8, int(len(overview.index)) - 1, f'Total messages: {total_messages}', ha='center', va='center',
             color='black')
    plt.tight_layout()
    #plt.show()
    plt.savefig(f'{output_directory}/participant_comparison {graph_title} ({g_start.strftime('%d.%m.%Y')} - {g_end.strftime('%d.%m.%Y')}).png', dpi=300, bbox_inches='tight')

def submit_analysis_old(messages_df, output_directory, graph_title, start, end):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date() # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date() # global and local end

    messages_df['sender_name'] = messages_df['sender_name'].apply(
        custom_decode)  # decode the names to normal characters xD
    participants = messages_df['sender_name'].unique()  # take unique names of participants
    messages_df['content'] = messages_df['content'].apply(
        custom_decode)  # decode text messages to normal characters xD (optional)
    try:
        messages_df = messages_df.drop('is_geoblocked_for_viewer', axis=1)  # drop this unnecessary column
        #messages_df = messages_df.drop('share', axis=1)  # drop this unnecessary column
    except:
        pass

    filtered_df = messages_df[(messages_df['timestamp_local'].dt.date >= g_start) & (messages_df['timestamp_local'].dt.date <= g_end)]

    filtered_df = filtered_df.groupby('sender_name').count()

    # messages_df = messages_df.groupby('sender_name').count()  # count all columns and group by participant

    #print(filtered_df)

    result = {'participants': [], 'total': []}

    for column in filtered_df.columns:
        result[column] = []

    excluded_keys = ['participants', 'total', 'sender_name']

    for i, participant in enumerate(participants):
        result['participants'].append(participant)
        result['total'].append(filtered_df['timestamp_ms'][i])
        for k in result.keys():
            if k not in excluded_keys:
                result[k].append(filtered_df[k][i])

    results_df = pd.DataFrame(result)
    #return  results_df
    results_df.to_csv(f'{output_directory}/analysis_results {graph_title}.csv')


#start2, end2, title2, _, messages2 = read_json_files(dynamo)

#submit_analysis(messages2)

#hourly_activity_histogram(messages2, '', title2, (start2, start2), (end2, end2))

#data = submit_analysis(messages2, '', '')

#print(data)

def compare_participants(output_directory, graph_title, grid_on, c_palette):

    data = pd.read_csv(f'{output_directory}/analysis_results {graph_title}.csv')
    #data = submit_analysis(messages, '')

    #data = output_directory.sort_values(by=['total'])[::-1]
    data = data.sort_values(by=['total'])[::-1]  # sort by total activity
    #print(data)

    plot_df = pd.DataFrame({
        'Text': list(data['content']),
        'Photos': list(data['photos']),
        'Videos': list(data['videos'])
        #'Gifs': list(data['gifs']),
        #'Voice': list(data['audio_files']),
        #'Calls': list(data['call_duration'])
                                        }, index=list(data['participants']))

    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    # sns.set_palette(c_palette)

    ax = plot_df.plot.bar(rot=0, stacked=True, figsize=(10, 6))
    ax.set_title('Messaging decomposition')
    ax.legend()
    plt.xticks(rotation=45)
    ax.set_axisbelow(True)
    #ax.set_xticklabels(list(data['participants']), ha='right')
    plt.minorticks_on()
    plt.show()
    plt.savefig(f'{output_directory}/participant_comparison {graph_title}.png', dpi=300, bbox_inches='tight')


#compare_participants(data, '', True, 'viridis')

def plot_activity_days(messages, output_directory, title, start, end, grid_on, c_palette):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date() # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date() # global and local end

    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    sns.set_palette(c_palette)

    fig = plt.figure(figsize=(8, 6))

    df_day = messages.groupby(pd.Grouper(key='timestamp_local', freq='D')).size()  # get y values to a list
    df_day.index = pd.to_datetime(
        df_day.index).date  # change index from timestamp datatype do datetime object for future reindexing

    if g_start == l_start and g_end == l_end:
        #print('If clause 1')
        #l_start -= pd.DateOffset(days=1)
        date_range = pd.date_range(l_start, l_end)  # create date range of all days
        date_series = date_range.to_series()

    else:
        #print('If clause 2')
        #l_start -= pd.DateOffset(days=1)
        #g_start -= pd.DateOffset(days=1)
        global_range = pd.date_range(g_start, g_end)  # global range of x values
        date_series = global_range.to_series()
        df_day = df_day.reindex(global_range)  # reindex our data on global range, getting NaN where no value

    plt.plot(date_series, df_day)

    df_day = df_day.dropna()
    avg_count = sum(df_day) / len(df_day)

    plt.scatter(df_day.idxmax(), max(df_day), color='red', label=f'The Most Active Day: {max(df_day)} Messsages ({df_day.idxmax()})')
    plt.axhline(y=avg_count, color='grey', linestyle='--', label=f'Average Daily Messages: {avg_count:.2f}')

    # Check if there are more than 12 months
    if (g_end - g_start).days > 365:
        date_format = mdates.DateFormatter('%Y')
        plt.gca().xaxis.set_major_formatter(date_format)
    elif (g_end - g_start).days > 35:
        date_format = mdates.DateFormatter('%b %Y')
        plt.gca().xaxis.set_major_formatter(date_format)
    else:
        date_format = mdates.DateFormatter('%d %b %Y')
        plt.gca().xaxis.set_major_formatter(date_format)

    # Formatting x-axis ticks
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6))

    # Rotate the tick labels for better readability
    plt.gcf().autofmt_xdate()

    plt.title(f'{title} Daily Chat Activity ({g_start.strftime('%d/%m/%Y')} - {g_end.strftime('%d/%m/%Y')})')
    plt.ylabel('Number of Messages')
    plt.minorticks_on()
    plt.xticks(rotation=45)
    plt.legend()
    #plt.show()
    plt.savefig(f'{output_directory}/daily_activity {title} ({g_start.strftime('%d.%m.%Y')} - {g_end.strftime('%d.%m.%Y')}).png', dpi=300)


def plot_activity_months(messages, output_directory, title, start, end, grid_on, c_palette):
    g_start, l_start = start[0], pd.Timestamp(start[1]).to_pydatetime().date()  # global and local start
    g_end, l_end = end[0], pd.Timestamp(end[1]).to_pydatetime().date()  # global and local end

    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    sns.set_palette(c_palette)

    fig = plt.figure(figsize=(8, 6))

    df_month = messages.groupby(pd.Grouper(key='timestamp_local', freq='M')).size()  # get y values to a list
    df_month.index = pd.to_datetime(df_month.index) + pd.offsets.MonthBegin(1)
    df_month.index = df_month.index.date

    if g_start == l_start and g_end == l_end:
        date_range = pd.date_range(l_start, l_end, freq='MS')  # create date range of all days
        date_series = date_range.to_series()

    else:
        global_range = pd.date_range(g_start, g_end, freq='MS')  # global range of x values
        date_series = global_range.to_series()
        #print(df_month)
        df_month = df_month.reindex(global_range)  # reindex our data on global range, getting NaN where no value

        #print(date_series)
        #print(df_month)

    plt.plot(date_series, df_month)

    df_month = df_month.dropna()
    avg_count = sum(df_month) / len(df_month)

    max_month = df_month.idxmax()

    plt.scatter(max_month, max(df_month), color='red', label=f'The Most Active Month: {max(df_month)} Messsages ({max_month.strftime('%m/%Y')})')
    plt.axhline(y=avg_count, color='grey', linestyle='--', label=f'Average Monthly Messages: {avg_count:.2f}')

    # Check if there are more than 12 months
    if (g_end - g_start).days > 365:
        date_format = mdates.DateFormatter('%Y')
        plt.gca().xaxis.set_major_formatter(date_format)
    elif (g_end - g_start).days > 35:
        date_format = mdates.DateFormatter('%b %Y')
        plt.gca().xaxis.set_major_formatter(date_format)
    else:
        date_format = mdates.DateFormatter('%d %b %Y')
        plt.gca().xaxis.set_major_formatter(date_format)

    # Formatting x-axis ticks
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6))

    # Rotate the tick labels for better readability
    plt.gcf().autofmt_xdate()

    plt.title(f'{title} Monthly Chat Activity ({g_start.strftime('%m/%Y')} - {g_end.strftime('%m/%Y')})')
    plt.ylabel('Number of Messages')
    plt.minorticks_on()
    plt.xticks(rotation=45)
    plt.legend()
    #plt.show()
    plt.savefig(f'{output_directory}/monthly_activity {title} ({g_start.strftime('%m.%Y')} - {g_end.strftime('%m.%Y')}).png', dpi=300)

#start1, end1, title1, _, messages1 = read_json_files(kata)
#start2, end2, title2, _, messages2 = read_json_files(chiara)

#plot_activity_months(messages, '', title, start, end)

def call_time_analysis(messages):
    call_time = pd.DataFrame({'caller': list(messages['sender_name'][messages['call_duration'].dropna().index].apply(custom_decode)),
                          'duration_s': list(messages['call_duration'].dropna()),
                              'timestamp_local': list(messages['timestamp_local'][messages['call_duration'].dropna().index])})

    call_hist = pd.DataFrame({'t': 0}, index=np.arange(0, 24, 1))

    #print(call_time)

    call_time = call_time.drop(call_time[call_time['duration_s'] == 0].index, inplace=False).reset_index(drop=True)
    call_time['hour'] = call_time['timestamp_local'].dt.hour

    #print(call_hist.head())

    for i in range(len(call_time.index)):
        call_hist.at[int(call_time['hour'][i]), 't'] += call_time['duration_s'][i]  # sum of seconds for each ended call

    call_time = call_time.drop(['timestamp_local', 'hour'], axis=1)  # drop timestamp because it can't be summed
    call_time = call_time.groupby('caller').sum()  # sum durations of calls
    call_time['duration_dt'] = pd.to_timedelta(call_time['duration_s'], unit='s', errors='coerce')  # convert seconds to timedelta
    #print(call_time)  # for total call time


def plot_multiple_chats_day(messages, output_directory, titles, starts, ends, grid_on, c_palette):
    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    # sns.set_palette(c_palette)

    fig = plt.figure(figsize=(8, 6))

    g_start = pd.Timestamp(min(starts)).to_pydatetime().date()  # starts and ends need to be lists or tuples
    g_end = pd.Timestamp(max(ends)).to_pydatetime().date()

    global_range = pd.date_range(g_start, g_end)  # global range of x values
    date_series = global_range.to_series()

    for message, title in zip(messages, titles):
        df_day = message.groupby(pd.Grouper(key='timestamp_local', freq='D')).size()  # get y values to a list
        df_day.index = pd.to_datetime(df_day.index).date
        df_day = df_day.reindex(global_range)  # reindex our data on global range, getting NaN where no value
        plt.plot(date_series, df_day, label=title)

    plt.legend()
    plt.show()


def plot_multiple_chats_month(messages, output_directory, titles, starts, ends, grid_on, c_palette):
    # if grid_on:
    #     sns.set_style("whitegrid")
    # else:
    #     sns.set_style("white")
    # sns.set_palette(c_palette)

    fig = plt.figure(figsize=(8, 6))

    g_start = pd.Timestamp(min(starts)).to_pydatetime().date()  # starts and ends need to be lists or tuples
    g_end = pd.Timestamp(max(ends)).to_pydatetime().date()

    global_range = pd.date_range(g_start, g_end, freq='MS')  # global range of x values
    date_series = global_range.to_series()

    for message, title in zip(messages, titles):
        df_month = message.groupby(pd.Grouper(key='timestamp_local', freq='M')).size()  # get y values to a list
        df_month.index = pd.to_datetime(df_month.index) + pd.offsets.MonthBegin(1)
        df_month.index = df_month.index.date
        df_month = df_month.reindex(global_range)  # reindex our data on global range, getting NaN where no value
        plt.plot(date_series, df_month, label=title, alpha=0.7)

    plt.legend()
    plt.show()

#plot_multiple_chats_month((messages1, messages2), '', (title1, title2), (start1, start2), (end1, end2))


