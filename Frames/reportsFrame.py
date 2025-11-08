import ttkbootstrap as ttk
from ttkbootstrap.validation import validator, add_validation
import os
import re
from datetime import datetime
import webbrowser

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.colors import green, orange, red, black
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.platypus as platypus

from Frames.pageFrame import pageFrame
from Database import DatabaseConnection
from utils import previewText


class ReportFrame(pageFrame):
    def __init__(self, master: ttk.window.Window, role: str, employee_id: int):
        # Inherits Page Frame
        super().__init__(master=master,
                         title="Reports",
                         role=role,
                         button_config={
                             "Worker": ["Product Movement", "Stock Level"],
                             "Supervisor": ["Product Movement", "Stock Level", "Performance Report",
                                            "Traceability Report"],
                             "Administrator": ["Product Movement", "Stock Level", "Performance Report",
                                               "Traceability Report", "User Activities"]
                         },
                         employeeID=employee_id)

        self.db_connection = DatabaseConnection()

        self.product_movement_report()

    def product_movement_report(self):
        column_names = ("Date", "Product", "Batch No.", "From", "To", "Quantity", "Status")
        self._insert_table_headings(column_names)
        self._load_table_rows(self.db_connection.query_product_movement_report())

    def stock_level_report(self):
        column_names = ("Product", "Unit Cost", "Total Value", "On Hand", "Free to Use", "Incoming", "Outgoing")
        self._insert_table_headings(column_names)
        self._load_table_rows(self.db_connection.query_stock_level_report())

    def performance_report(self):
        employee = self._dialog_employee()
        # employee = "1"

        if employee is None:
            return

        employee = employee.split(' - ')[0]

        parameters = [value for value in self.db_connection.query_employee_report(employee)]
        image = f"{self.config.getGraphicsPath()}/User_Avatars/{self.config.getPreferences(employee)[0]}.png"

        self._generate_report(parameters + [image])

    def traceability_report(self):
        batch_number = self._dialog_product_batch_no()

        if batch_number is None:
            return

        batch_number = (batch_number.split(' - ')[0], batch_number.split(' - ')[1])

        column_names = ("PIC", "Product Name", "Date", "Batch No.", "From", "To", "Quantity")
        self._insert_table_headings(column_names)
        self._load_table_rows(self.db_connection.query_traceability_report(batch_number[0], batch_number[1]))

    def user_activities_report(self):
        column_names = ("Date", "Time", "User", "Activity", "Remark")
        self._insert_table_headings(column_names)
        self._load_table_rows(self.db_connection.query_user_activities_report())

    def _insert_table_headings(self, column_names: tuple) -> None:
        self.tableview.purge_table_data()
        # print(column_names)

        for column in column_names:
            self._insert_table_columns(column)

    def getButtonCommand(self, button_text):
        if button_text == "Product Movement":
            self.product_movement_report()

        elif button_text == "Stock Level":
            self.stock_level_report()

        elif button_text == "Performance Report":
            self.performance_report()

        elif button_text == "Traceability Report":
            self.traceability_report()

        elif button_text == "User Activities":
            self.user_activities_report()

    def _dialog_employee(self) -> str | None:
        def on_submit_button():
            text = entry.get()
            if text in entry.cget("values"):
                toplevel.destroy()
                toplevel.selected_employee = text

            else:
                ttk.Label(frame, text="Submission failed to process", bootstyle="danger", anchor=ttk.CENTER,
                          font=self.font.get_font("error")).grid(row=2, column=1, columnspan=2, sticky="we")

        toplevel = ttk.Toplevel(master=self.master, width=400, height=150, resizable=(False, False),
                                title="Performance Report", transient=self.master, minsize=(400, 150))
        errVar = ttk.StringVar()
        toplevel.selected_employee = None

        ttk.Frame(toplevel, height=20).grid(row=0, column=0)
        ttk.Label(toplevel, text="Enter Employee Name", font=self.font.get_font("thin2"), anchor=ttk.W).grid(
            row=1, column=0, sticky="nwes", padx=20)
        entry = ttk.Combobox(toplevel, values=self.db_connection.query_worker())
        entry.grid(row=2, column=0, sticky="nwes", padx=20)
        ttk.Label(toplevel, textvariable=errVar, anchor=ttk.NW, font=self.font.get_font("error"),
                  foreground=self.styleObj.colors.get("danger")).grid(row=3, column=0, sticky="nwes", padx=20)
        ttk.Separator(toplevel).grid(row=4, column=0, columnspan=3, sticky="wes")
        frame = ttk.Frame(toplevel, padding=10)
        frame.grid(row=5, column=0, sticky="nwes")

        toplevel.rowconfigure(0, weight=0)
        toplevel.rowconfigure(1, weight=0)
        toplevel.rowconfigure(2, weight=1)
        toplevel.rowconfigure(3, weight=1)
        toplevel.rowconfigure(4, weight=1)
        toplevel.rowconfigure(5, weight=0)
        toplevel.columnconfigure(0, weight=1)

        errVar2 = ttk.StringVar()
        ttk.Button(frame, text="Cancel", bootstyle="danger", command=lambda: toplevel.destroy()).grid(row=1, column=1)
        ttk.Button(frame, text="Submit", bootstyle="success", command=lambda: on_submit_button()
                   ).grid(row=1, column=2)

        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=8)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        # Preview Text
        previewText(entry, key="employeeIDNameEntry")

        # Validation
        def validate_entry(event):
            if event.postchangetext in event.widget.cget("values") or event.postchangetext == "":
                errVar.set("")
                return True
            else:
                errVar.set("Invalid Employee Name")
                return False

        add_validation(entry, validator(validate_entry), when="focus")
        toplevel.wait_window()
        return toplevel.selected_employee

    def _dialog_product_batch_no(self) -> str | None:
        def on_submit_button():
            text = entry.get()
            if text in entry.cget("values"):
                toplevel.destroy()
                toplevel.selected_batch_no = text
            else:
                ttk.Label(frame, text="Submission failed to process", bootstyle="danger", anchor=ttk.CENTER,
                          font=self.font.get_font("error")).grid(row=2, column=1, columnspan=2, sticky="we")

        toplevel = ttk.Toplevel(master=self.master, width=400, height=150, resizable=(False, False),
                                title="Traceability Report", transient=self.master, minsize=(400, 150))
        errVar = ttk.StringVar()
        toplevel.selected_batch_no = None

        ttk.Frame(toplevel, height=20).grid(row=0, column=0)
        ttk.Label(toplevel, text="Enter Batch No.", font=self.font.get_font("thin2"), anchor=ttk.W).grid(
            row=1, column=0, sticky="nwes", padx=20)
        entry = ttk.Combobox(toplevel, values=self.db_connection.query_productBatchNo())
        entry.grid(row=2, column=0, sticky="nwes", padx=20)
        ttk.Label(toplevel, textvariable=errVar, anchor=ttk.NW, font=self.font.get_font("error"),
                  foreground=self.styleObj.colors.get("danger")).grid(row=3, column=0, sticky="nwes", padx=20)
        ttk.Separator(toplevel).grid(row=4, column=0, columnspan=3, sticky="wes")
        frame = ttk.Frame(toplevel, padding=10)
        frame.grid(row=5, column=0, sticky="nwes")

        toplevel.rowconfigure(0, weight=0)
        toplevel.rowconfigure(1, weight=0)
        toplevel.rowconfigure(2, weight=1)
        toplevel.rowconfigure(3, weight=1)
        toplevel.rowconfigure(4, weight=1)
        toplevel.rowconfigure(5, weight=0)
        toplevel.columnconfigure(0, weight=1)

        errVar2 = ttk.StringVar()
        ttk.Button(frame, text="Cancel", bootstyle="danger", command=lambda: toplevel.destroy()).grid(row=1, column=1)
        ttk.Button(frame, text="Submit", bootstyle="success", command=lambda: on_submit_button()
                   ).grid(row=1, column=2)

        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=8)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        # Preview Text
        previewText(entry, key="batchNoEntry")

        # Validation
        def validate_entry(event):
            if event.postchangetext in event.widget.cget("values") or event.postchangetext == "":
                errVar.set("")
                return True
            else:
                errVar.set("Invalid Batch No.")
                return False

        add_validation(entry, validator(validate_entry), when="focus")
        toplevel.wait_window()
        return toplevel.selected_batch_no


    def _generate_report(self, parameters: list[str]):
        """Parameters: [Employee ID - Employee Name, Employee Role, Email, Contact Number, Tasks Assigned,
        Tasks Completed, Tasks Overdue, PFP Image Object]"""
        # Read the latest file from Reports directory, and increment the file name by 1 (Format: Report_1.pdf)
        report_files = [f for f in os.listdir(self.config.getReportsFile()) if re.match(r"Report_\d+.pdf", f)]

        # If the file does not exist, create a new file with the name Report_1.pdf
        if report_files:
            report_files.sort(key=lambda f: int(re.search(r'\d+', f).group()))
            last_file = report_files[-1]
            file_number = int(re.search(r"\d+", last_file).group())
            file_name = f"{self.config.getReportsFile()}/Report_{file_number + 1}.pdf"

        else:
            file_name = f"{self.config.getReportsFile()}/Report_1.pdf"

        self.__create_pdf__(file_name, parameters)

        # Open the PDF file
        webbrowser.open_new(f'file://{file_name}')

    def __create_pdf__(self, output_filename: str, parameters: list[str]):
        """Parameters: [Employee ID - Employee Name, Employee Role, Email, Contact Number, Tasks Assigned,
                Tasks Completed, Tasks Overdue, PFP Image Object]"""

        # Create a new A5-sized canvas
        c = canvas.Canvas(output_filename, pagesize=A5)

        # Draw the title
        title = "Worker Performance Report"
        pdfmetrics.registerFont(TTFont('Lexend', f'{self.config.repo_file_path}/Fonts/Lexend-Regular.ttf'))
        c.setFont('Lexend', 16)
        c.setFillColor(black)  # Set the fill color to black
        title_width = pdfmetrics.stringWidth(title, 'Lexend', 16)  # Get the width of the title
        title_x = (420 - title_width) / 2  # Adjust the x-coordinate to center the title
        title_y = 520  # Adjust the y-coordinate to place the title at the top
        c.drawString(title_x, title_y, title)  # Draw the title at the adjusted position

        # Draw the subtitle
        subtitle = f"Report generated on {datetime.now().strftime('%d %B %Y, %A')}"
        c.setFont('Lexend', 10)
        subtitle_width = pdfmetrics.stringWidth(subtitle, 'Lexend', 10)  # Get the width of the subtitle
        subtitle_x = (420 - subtitle_width) / 2  # Adjust the x-coordinate to center the subtitle
        subtitle_y = 500  # Adjust the y-coordinate to place the subtitle below the title
        c.drawString(subtitle_x, subtitle_y, subtitle)  # Draw the subtitle at the adjusted position

        # Draw the second part of the subtitle
        subtitle_part2 = f"For employee {parameters[0].split(' - ')[1]}"
        subtitle_width2 = pdfmetrics.stringWidth(subtitle_part2, 'Lexend', 10)  # Get the width of the subtitle
        subtitle_x2 = (420 - subtitle_width2) / 2  # Calculate the x-coordinate to center the subtitle
        subtitle_y2 = 485  # Adjust the y-coordinate to place the subtitle below the first part
        c.drawString(subtitle_x2, subtitle_y2, subtitle_part2)  # Draw the subtitle at the adjusted position

        # Draw the PFP
        image = platypus.Image(parameters[7], width=100, height=100)
        image.drawOn(c, 50, 300)

        # Draw the employee ID and name, role, email, and contact number
        text_objects = parameters[:4]
        style = getSampleStyleSheet()['Normal']
        for i, text in enumerate(text_objects):
            text_width = pdfmetrics.stringWidth(text, 'Lexend', 12)
            x = 100 - text_width / 2
            c.setFont('Lexend', 12)
            c.drawString(x, 250 - i * 30, text)

        # Draw the text above the meter
        tasks_completed_text = f"Tasks completed: {parameters[5]}/{parameters[4]}"
        c.setFont('Lexend', 12)
        tasks_completed_text_width = pdfmetrics.stringWidth(tasks_completed_text, 'Lexend', 12)
        tasks_completed_text_x = (550 - tasks_completed_text_width) / 2
        tasks_completed_text_y = 350
        c.drawString(tasks_completed_text_x, tasks_completed_text_y, tasks_completed_text)

        # Draw a meter for the task completion rate
        tasks_assigned = parameters[4]
        tasks_completed = parameters[5]
        completion_rate = int(tasks_completed) / int(tasks_assigned) if tasks_assigned else 0
        color = green if completion_rate > 0.8 else orange if completion_rate > 0.5 else red

        # Draw the full circle (background of the meter)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)  # Set the color to light gray
        c.setFillColorRGB(0.7, 0.7, 0.7)  # Set the fill color to light gray
        c.circle(275, 265, 50, fill=1)  # Draw a circle at (275, 265) with radius 50

        # Draw the partial circle (progress of the meter)
        c.setStrokeColor(color)  # Set the color to the completion color
        c.setFillColor(color)  # Set the fill color to the completion color
        c.wedge(225, 215, 325, 315, 90, completion_rate * 360 if completion_rate else 1, fill=1)  # Draw an arc
        # representing the completion

        # Draw the smaller circle in the center
        c.setStrokeColorRGB(1, 1, 1)  # Set the color to white
        c.setFillColorRGB(1, 1, 1)  # Set the fill color to white
        c.circle(275, 265, 30, fill=1)  # Draw a smaller circle at (275, 265) with radius 30

        # Draw the task completion rate text
        text_part2 = f"{completion_rate * 100:.1f}%"
        text_width2 = pdfmetrics.stringWidth(text_part2, 'Lexend', 12)
        x2 = 277 - text_width2 / 2
        y2 = 261
        c.setFillColor('black')
        c.drawString(x2, y2, text_part2)

        # Draw the task completion rate as a percentage
        c.setFont('Lexend', 12)
        c.drawString(200, 170, f"Task Completion Rate: {completion_rate * 100:.1f}%")  # Adjust the position as needed

        # Draw the existing footer
        c.setFont('Lexend', 8)  # Set the font to Lexend and size to 10
        footer_text = f"Page 1 | Generated on {datetime.now().strftime('%d %B %Y, %A')}"
        footer_width = pdfmetrics.stringWidth(footer_text, 'Lexend', 8)  # Get the width of the footer
        footer_x = (420 - footer_width) / 2  # Calculate the x-coordinate to center the footer
        footer_y = 20  # Set the y-coordinate to place the footer at the bottom
        c.drawString(footer_x, footer_y, footer_text)  # Draw the footer at the adjusted position

        # Draw the new row below the footer
        new_row_text = "Reports are saved to (repository_path)/Reports by default"
        new_row_width = pdfmetrics.stringWidth(new_row_text, 'Lexend', 8)  # Get the width of the new row
        new_row_x = (420 - new_row_width) / 2  # Calculate the x-coordinate to center the new row
        new_row_y = 10  # Set the y-coordinate to place the new row below the footer
        c.drawString(new_row_x, new_row_y, new_row_text)  # Draw the new row at the adjusted position

        # Save the canvas to a PDF file
        c.save()


if __name__ == '__main__':
    from navigationFrame import navigationFrame

    # Create Main Window, and center it
    window = ttk.Window(title="Keai IWMS", themename="litera", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    # Creates Frames
    lFrame = navigationFrame(window, 1, ttk.Frame(window))
    lFrame.getButtonCommand("Report")
    lFrame.rFrame.user_activities_report()
    # window.withdraw()

    # Starts Event Main Loop
    window.mainloop()
