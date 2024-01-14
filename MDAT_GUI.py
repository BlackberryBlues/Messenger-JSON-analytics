import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
from tkcalendar import DateEntry
from tkinter import ttk
import os
import algs
import glob

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Messenger Data Analysis Tool GUI")

        # initialize global variables
        self.messages_data = pd.DataFrame()
        self.participants = pd.DataFrame()
        self.local_start_date = ''
        self.local_end_date = ''
        self.output_directory = ''
        self.conversation_title = ''
        self.input_folder_path = ''
        self.grid_on = True
        self.color_palette = 'bright'

        # Left Column
        self.left_frame = tk.Frame(root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Title and Buttons
        title_label = tk.Label(self.left_frame, text="MDAT", font=("Helvetica", 14))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        file_button = tk.Button(self.left_frame, text="Input Files Folder", command=self.select_input_file)
        file_button.grid(row=1, column=0, padx=(0, 10))

        folder_button = tk.Button(self.left_frame, text="Output Folder", command=self.select_output_folder)
        folder_button.grid(row=1, column=1)

        # Date Selection
        date_label = tk.Label(self.left_frame, text="Time Frame", font=("Helvetica", 14))
        date_label.grid(row=2, column=0, columnspan=2, pady=(20, 10))

        start_date_label = tk.Label(self.left_frame, text="Start Date:")
        start_date_label.grid(row=3, column=0, padx=(0, 10), sticky="e")

        self.global_start_date = DateEntry(self.left_frame, width=12, background='grey',
                                          foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.global_start_date.grid(row=3, column=1)

        end_date_label = tk.Label(self.left_frame, text="End Date:")
        end_date_label.grid(row=4, column=0, padx=(0, 10), sticky="e")

        self.global_end_date = DateEntry(self.left_frame, width=12, background='grey',
                                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.global_end_date.grid(row=4, column=1)

        self.total_time_label = tk.Label(self.left_frame, text="Total time:")
        self.total_time_label.grid(row=5, column=0, columnspan=4, padx=(0, 10))

        # Time Frame
        time_frame_label = tk.Label(self.left_frame, text="Time Resolution", font=("Helvetica", 14))
        time_frame_label.grid(row=6, column=0, columnspan=2, pady=(20, 10))

        self.time_frame_var = tk.StringVar()
        self.time_frame_var.set("Daily")

        daily_radio = tk.Radiobutton(self.left_frame, text="Daily", variable=self.time_frame_var, value="Daily")
        daily_radio.grid(row=7, column=0, padx=(0, 10), pady=(0, 10))

        monthly_radio = tk.Radiobutton(self.left_frame, text="Monthly", variable=self.time_frame_var, value="Monthly")
        monthly_radio.grid(row=7, column=1, padx=(0, 10), pady=(0, 10))

        # Separator Line
        separator = ttk.Separator(root, orient="vertical")
        separator.grid(row=0, column=1, sticky="ns", pady=10)

        # Right Column
        self.right_frame = tk.Frame(root)
        self.right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Checkboxes
        checkbox_label = tk.Label(self.right_frame, text="Analysis output selection", font=("Helvetica", 14))
        checkbox_label.grid(row=0, column=0, pady=(0, 10))

        self.checkbox1a_val = tk.IntVar()
        self.checkbox1b_val = tk.IntVar()
        self.checkbox2_val = tk.IntVar()
        self.checkbox3_val = tk.IntVar()
        self.checkbox4_val = tk.IntVar()
        self.checkbox5_val = tk.IntVar()
        self.checkbox6_val = tk.IntVar()

        checkbox1a = tk.Checkbutton(self.right_frame, text="Hourly Activity Histogram", variable=self.checkbox1a_val)
        checkbox1a.grid(row=1, column=0, sticky="w")

        checkbox1b = tk.Checkbutton(self.right_frame, text="Activity Histogram", variable=self.checkbox1b_val)
        checkbox1b.grid(row=2, column=0, sticky="w")

        checkbox2 = tk.Checkbutton(self.right_frame, text="Participants Comparison", variable=self.checkbox2_val)
        checkbox2.grid(row=4, column=0, sticky="w")

        checkbox3 = tk.Checkbutton(self.right_frame, text="Activity in Time", variable=self.checkbox3_val)
        checkbox3.grid(row=5, column=0, sticky="w")

        checkbox4 = tk.Checkbutton(self.right_frame, text="Call Duration Analysis", variable=self.checkbox4_val)
        checkbox4.grid(row=6, column=0, sticky="w")

        checkbox5 = tk.Checkbutton(self.right_frame, text="Show longest text (all time)", variable=self.checkbox5_val)
        checkbox5.grid(row=7, column=0, sticky="w")

        checkbox6 = tk.Checkbutton(self.right_frame, text="Absolute Total Comparison (Long)", variable=self.checkbox6_val)
        checkbox6.grid(row=8, column=0, sticky="w")

        run_button = tk.Button(self.right_frame, text="Run Analysis", command=self.run_analysis)
        run_button.grid(row=10, column=0, padx=(10, 0), pady=(10, 10), sticky="s")

        separator = ttk.Separator(root, orient="vertical")
        separator.grid(row=0, column=3, sticky="ns", pady=10)

        # Right Column
        self.right_right_frame = tk.Frame(root)
        self.right_right_frame.grid(row=0, column=4, padx=10, pady=10, sticky="nsew")

        another_label = tk.Label(self.right_right_frame, text="Standalone Combined Analysis", font=("Helvetica", 14))
        another_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        comp_1_file_button = tk.Button(self.right_right_frame, text="Component 1", command=self.add_component)
        comp_1_file_button.grid(row=1, column=0, padx=(0, 10), pady=(10, 5))
        self.comp_1 = tk.Label(self.right_right_frame, text='Component 1')
        self.comp_1.grid(row=1, column=1, padx=(10, 0), pady=(10, 10), sticky="w")

        comp_2_file_button = tk.Button(self.right_right_frame, text="Component 2", command=self.add_component)
        comp_2_file_button.grid(row=2, column=0, padx=(0, 10), pady=(10, 5))
        self.comp_2 = tk.Label(self.right_right_frame, text='Component 2')
        self.comp_2.grid(row=2, column=1, padx=(10, 0), pady=(10, 10), sticky="w")

        comp_3_file_button = tk.Button(self.right_right_frame, text="Component 3", command=self.add_component)
        comp_3_file_button.grid(row=3, column=0, padx=(0, 10), pady=(10, 5))
        self.comp_3 = tk.Label(self.right_right_frame, text='Component 3')
        self.comp_3.grid(row=3, column=1, padx=(10, 0), pady=(10, 10), sticky="w")

        comp_4_file_button = tk.Button(self.right_right_frame, text="Component 4", command=self.add_component)
        comp_4_file_button.grid(row=4, column=0, padx=(0, 10), pady=(10, 5))
        self.comp_4 = tk.Label(self.right_right_frame, text='Component 4')
        self.comp_4.grid(row=4, column=1, padx=(10, 0), pady=(10, 10), sticky="w")

        run_comparison = tk.Button(self.right_right_frame, text="Compare Multiple Users", command=self.run_comparison)
        run_comparison.grid(row=10, column=0, columnspan=2, padx=(10, 0), pady=(10, 10), sticky="s")

        self.comp_messages = []
        self.comp_titles = []
        self.comp_starts = []
        self.comp_ends = []
        self.comp_counter = 0

        # Status Bar
        input_file_status_bar = tk.Frame(root, bd=1, relief=tk.SUNKEN)
        input_file_status_bar.grid(row=1, column=0, columnspan=4, sticky="ew")

        output_file_status_bar = tk.Frame(root, bd=1, relief=tk.SUNKEN)
        output_file_status_bar.grid(row=2, column=0, columnspan=4, sticky="ew")

        status_bar = tk.Frame(root, bd=1, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=4, sticky="ew")

        # Label for displaying input file path and output folder
        self.display_label_input = tk.Label(input_file_status_bar, text="Input File: Not Selected", anchor="w")
        self.display_label_input.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.display_label_output = tk.Label(output_file_status_bar, text="Output Folder: Not Selected", anchor="w")
        self.display_label_output.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.status_bar = tk.Label(status_bar, text="", anchor="w")
        self.status_bar.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    def select_input_file(self):
        self.input_folder_path = filedialog.askdirectory()
        folder_name = os.path.basename(self.input_folder_path)
        self.display_label_input.config(text=f"Input Files Directory: {folder_name}")

        #part to select it as an output directory as well
        self.output_directory = self.input_folder_path
        self.display_label_output.config(text=f"Output Folder: {folder_name}")

        try:
            print(self.input_folder_path)
            (self.local_start_date, self.local_end_date, self.conversation_title,
            self.participants, self.messages_data, (years, months, days)) = algs.read_json_files(self.input_folder_path)

            self.global_start_date.set_date(self.local_start_date)  # set the starting value to the first message dat
            # self.start_date_entry.config(mindate=self.start_date, maxdate=self.end_date)
            self.global_end_date.set_date(self.local_end_date)  # set the end date to the date of the last noted text
            # self.end_date_entry.config(mindate=self.start_date, maxdate=self.end_date)
            self.total_time_label.config(text=f"Total time: {years} Years, {months} Months, {days} Days")
        except:
            pass




    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        print(folder_path)
        self.output_directory = folder_path
        folder_name = os.path.basename(folder_path)
        self.display_label_output.config(text=f"Output Folder: {folder_name}")

    def check_param_validity(self):
        start_date = self.global_start_date.get_date()
        end_date = self.global_end_date.get_date()

        if start_date > end_date:
            tk.messagebox.showerror('Error', "Start date can't be later than the end date")

        if self.output_directory == '':
            self.output_directory = "D:\1_STRAINS\1 semester\Lille Python\data science\Messenger_visuals"

    def run_analysis(self):
        # Implement the functionality of the 'Run' button here
        self.status_bar.config(text="Checking parameters validity...")
        self.check_param_validity()

        self.status_bar.config(text="Running...")
        #outsource.analyze_messages(self.file_data, self.output_directory)

        self.status_bar.config(text="Messages analyzed, plotting graphs...")
        #outsource.compare_participants(self.file_data, self.output_directory)

        if self.checkbox1a_val.get():
            # if box 1 is checked (Hourly Activity Histogram)
            self.status_bar.config(text="Graphing Hourly Activity Histogram...")
            algs.hourly_activity_histogram(self.messages_data, self.output_directory, self.conversation_title,
                                           (self.global_start_date.get_date(), self.local_start_date),
                                           (self.global_end_date.get_date(), self.local_start_date),
                                           self.grid_on, self.color_palette)
        if self.checkbox1b_val.get():
            # if box 1 is checked (Daily/Monthly Activity Histogram)
            if self.time_frame_var.get() == 'Daily':
                self.status_bar.config(text="Graphing Daily Activity Histogram...")
                algs.daily_activity_histogram(self.messages_data, self.output_directory, self.conversation_title,
                                              (self.global_start_date.get_date(), self.local_start_date),
                                              (self.global_end_date.get_date(), self.local_start_date),
                                              self.grid_on, self.color_palette)
            elif self.time_frame_var.get() == 'Monthly':
                self.status_bar.config(text="Graphing Montlhy Activity Histogram...")
                algs.monthly_activity_histogram(self.messages_data, self.output_directory, self.conversation_title,
                                                (self.global_start_date.get_date(), self.local_start_date),
                                                (self.global_end_date.get_date(), self.local_start_date),
                                                self.grid_on, self.color_palette)

        if self.checkbox2_val.get():
            # if box 2 is checked (Participants Comparison)
            self.status_bar.config(text="Analyzing Messaging History...")
            algs.submit_analysis(self.messages_data, self.output_directory, self.conversation_title,
                                 (self.global_start_date.get_date(), self.local_start_date),
                                 (self.global_end_date.get_date(), self.local_end_date))
            # self.status_bar.config(text="Plotting Participants Activity...")
            # algs.compare_participants(self.output_directory, self.conversation_title,
            #                           self.grid_on, self.color_palette)

        if self.checkbox3_val.get():
            # if box 3 is checked (Activity in Time)
            if self.time_frame_var.get() == 'Daily':
                self.status_bar.config(text="Graphing Daily Activity...")
                algs.plot_activity_days(self.messages_data, self.output_directory, self.conversation_title,
                                        (self.global_start_date.get_date(), self.local_start_date),
                                        (self.global_end_date.get_date(), self.local_end_date),
                                        self.grid_on, self.color_palette)
            elif self.time_frame_var.get() == 'Monthly':
                self.status_bar.config(text="Graphing Monthly Activity...")
                algs.plot_activity_months(self.messages_data, self.output_directory, self.conversation_title,
                                          (self.global_start_date.get_date(), self.local_start_date),
                                          (self.global_end_date.get_date(), self.local_start_date),
                                          self.grid_on, self.color_palette)

        if self.checkbox4_val.get():
            # if box 4 is checked
            self.status_bar.config(text="Calculating Total Call Time...")
            algs.call_time_analysis(self.messages_data)


        if self.checkbox5_val.get():
            # if box 5 is checked
            longest_string_sender, longest_string_content, longest_string_timestamp = algs.find_longest_text(self.messages_data,
                                                                                                             (self.global_start_date.get_date(), self.local_start_date),
                                                                                                             (self.global_end_date.get_date(), self.local_start_date))

            new_window = tk.Toplevel(self.root)
            new_window.title("Longest text viewer")

            l = tk.Label(new_window, text=f'Longest text had {len(longest_string_content)} characters.\n'
                                          f'Sent by: {longest_string_sender} on {longest_string_timestamp.strftime("%d.%m.%Y")} \n'
                                          f'It read: \n'
                                          f'{longest_string_content}', wraplength=600)
            l.pack()

        if self.checkbox6_val.get():
            # if box 6 is checked
            # find all folders and all files within them
            # get title and total messages
            # save to file
            self.status_bar.config(text="Doing a Very Long Analysis...")

            parent_folders = self.input_folder_path
            print(parent_folders)
            child_folders = glob.glob(f'{parent_folders}\*')

            for i, folder in enumerate(child_folders):
                try:
                    print(f'Manipulating folder {i + 1}/{len(child_folders)}')

                    # Set the local output directory to the input directory
                    self.output_directory = folder

                    # First need to load all the data from selected child folder
                    (self.local_start_date, self.local_end_date, self.conversation_title,
                     self.participants, self.messages_data, (years, months, days)) = algs.read_json_files(
                        folder)

                    # Assign global start/end times because it's working like this and we're not touching what's working fine
                    self.global_start_date.set_date(
                        self.local_start_date)  # set the starting value to the first message dat
                    self.global_end_date.set_date(
                        self.local_end_date)  # set the end date to the date of the last noted text

                    # Hourly activity histogram
                    algs.hourly_activity_histogram(self.messages_data, self.output_directory, self.conversation_title,
                                                   (self.global_start_date.get_date(), self.local_start_date),
                                                   (self.global_end_date.get_date(), self.local_start_date),
                                                   self.grid_on, self.color_palette)

                    # Daily activity histogram
                    algs.daily_activity_histogram(self.messages_data, self.output_directory, self.conversation_title,
                                                  (self.global_start_date.get_date(), self.local_start_date),
                                                  (self.global_end_date.get_date(), self.local_start_date),
                                                  self.grid_on, self.color_palette)

                    # Monthly activity histogram
                    algs.monthly_activity_histogram(self.messages_data, self.output_directory, self.conversation_title,
                                                    (self.global_start_date.get_date(), self.local_start_date),
                                                    (self.global_end_date.get_date(), self.local_start_date),
                                                    self.grid_on, self.color_palette)

                    # Compare participants
                    algs.submit_analysis(self.messages_data, self.output_directory, self.conversation_title,
                                         (self.global_start_date.get_date(), self.local_start_date),
                                         (self.global_end_date.get_date(), self.local_end_date))

                    # Graph daily activity
                    algs.plot_activity_days(self.messages_data, self.output_directory, self.conversation_title,
                                            (self.global_start_date.get_date(), self.local_start_date),
                                            (self.global_end_date.get_date(), self.local_end_date),
                                            self.grid_on, self.color_palette)

                    # Graph monthly activity
                    algs.plot_activity_months(self.messages_data, self.output_directory, self.conversation_title,
                                              (self.global_start_date.get_date(), self.local_start_date),
                                              (self.global_end_date.get_date(), self.local_start_date),
                                              self.grid_on, self.color_palette)
                except:
                    print(f'Skipped folder {folder}')
                    continue



            #algs.just_get_total_messages(self.input_folder_path)

        os.startfile(self.output_directory)
        self.status_bar.config(text="Analysis finished successfully!")

    def add_component(self):
        # messages, output folder, titles, starts, ends
        input_folder_path = filedialog.askdirectory()
        folder_name = os.path.basename(input_folder_path)
        if self.comp_counter == 0:
            self.comp_1.config(text=f"Component 1: {folder_name}")
            self.comp_counter += 1
        elif self.comp_counter == 1:
            self.comp_2.config(text=f"Component 2: {folder_name}")
            self.comp_counter += 1
        elif self.comp_counter == 2:
            self.comp_3.config(text=f"Component 3: {folder_name}")
            self.comp_counter += 1
        elif self.comp_counter == 3:
            self.comp_4.config(text=f"Component 4: {folder_name}")
            self.comp_counter += 1

        s, e, t, _, m = algs.read_json_files(input_folder_path)

        self.comp_messages.append(m)
        self.comp_titles.append(t)
        self.comp_ends.append(e)
        self.comp_starts.append(s)

    def run_comparison(self):
        if self.time_frame_var.get() == 'Daily':
            algs.plot_multiple_chats_day(self.comp_messages, self.output_directory, self.comp_titles, self.comp_starts,
                                         self.comp_ends, self.grid_on, self.color_palette)
        elif self.time_frame_var.get() == 'Monthly':
            algs.plot_multiple_chats_month(self.comp_messages, self.output_directory, self.comp_titles, self.comp_starts,
                                           self.comp_ends, self.grid_on, self.color_palette)
        self.comp_1.config(text=f"Component 1:")
        self.comp_2.config(text=f"Component 2:")
        self.comp_3.config(text=f"Component 3:")
        self.comp_4.config(text=f"Component 4:")
        self.comp_messages = []
        self.comp_titles = []
        self.comp_starts = []
        self.comp_ends = []
        self.comp_counter = 0

if __name__ == "__main__":
    root = tk.Tk()
    my_gui = App(root)
    root.mainloop()
