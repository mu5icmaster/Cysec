<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/6295/6295417.png" width="100" alt="project-logo">
</p>
<p align="center">
    <h1 align="center">KEAI IWMS</h1>
</p>
<p align="center">
    <em>A comprehensive solution for Inventory and Warehouse Management.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/last-commit/twilight39/ALL2-IWMS?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/twilight39/ALL2-IWMS?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/twilight39/ALL2-IWMS?style=flat&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
		<em>Developed with the software and tools below.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat&logo=JSON&logoColor=white" alt="JSON">
</p>

<br><!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary><br>

- [📍 Overview](#-Overview)
- [🧩 Features](#-features)
- [🗂️ Repository Structure](#️-repository-structure)
- [📦 Modules](#-modules)
- [🚀 Getting Started](#-getting-started)
  - [⚙️ Installation](#️-installation)
  - [🤖 Usage](#-usage)
  - [🧪 Tests](#-tests)
</details>
<hr>

## 📍 Overview

**Objective**

An Inventory and Warehouse Management System (IWMS) aims to streamline the complex processes of acquiring, storing, controlling and distributing goods within a warehouse environment. This repository offers a comprehensive solution with user-friendly interfaces to streamline management and enhance productivity.

---

## 🧩 Features

### Inventory Management

KEAI is structured around various user interface frames that create seamless navigation through Login, Dashboard, Inventory, Notification, Accounts, and other screens. Each frame offers unique functionality to manage system operations.

<img width="1454" alt="Screenshot 2024-06-22 at 12 16 10 PM" src="https://github.com/twilight39/ALL2-IWMS/assets/169473752/30269f65-6a7d-4155-b5f0-c00265a36756">

- **Dashboard:** Provide an integrated overview for efficient workflow management 
- **Product:** Provide an interface to manage warehouse products 
- **Inventory:** Provide an interface to manage inventory stock 
- **Purchase Order:**  Provide an interface to manage inventory replenishments 
- **Sales Order:** Provide an interface to manage sales orders 
- **Vendor:** Provide an interface to manage suppliers 
- **Report:** Provide an interface to create comprehensive reports

---

### Warehouse Management

KEAI also offers a minimal system for managing employees, assigning/batch assigning tasks and monitoring task progress. Careful consideration is placed to ensure employees can customise interfaces to feel right at home. 

<img width="1441" alt="Screenshot 2024-06-22 at 12 40 45 PM" src="https://github.com/twilight39/ALL2-IWMS/assets/169473752/0a7a3500-5b39-41d3-add0-4eea13075daa">


## 🗂️ Repository Structure

```sh
└── ALL2-IWMS/
    ├── Database
    │   ├── Authentication.py
    │   ├── Database.py
    │   ├── Notification.py
    │   ├── Notifications.json
    │   └── __init__.py
    ├── Fonts
    │   ├── Lexend-Bold.ttf
    │   ├── Lexend-Regular.ttf
    │   ├── NotoSans-Bold.ttf
    │   ├── NotoSans-BoldItalic.ttf
    │   ├── NotoSans-Italic.ttf
    │   ├── NotoSans-Regular.ttf
    │   ├── ZillaSlab-Bold.ttf
    │   ├── ZillaSlab-BoldItalic.ttf
    │   ├── ZillaSlab-Italic.ttf
    │   └── ZillaSlab-Regular.ttf
    ├── Frames
    │   ├── Login.py
    │   ├── __init__.py
    │   ├── accountsPopup.py
    │   ├── dashboardFrame.py
    │   ├── inventoryFrame.py
    │   ├── navigationFrame.py
    │   ├── notificationFrame.py
    │   ├── pageFrame.py
    │   ├── popup.py
    │   ├── productFrame.py
    │   ├── purchaseOrderFrame.py
    │   ├── reportsFrame.py
    │   ├── salesOrderFrame.py
    │   ├── settingsPopup.py
    │   ├── taskFrame.py
    │   ├── ui_preview_text.json
    │   └── vendorFrame.py
    ├── Graphics
    │   ├── User_Avatars
    │   ├── loginBG.png
    │   ├── notificationIcon.png
    │   ├── passwordInvisible.png
    │   ├── passwordVisible.png
    │   ├── settingsIcon.png
    │   ├── themes_template.png
    │   └── xButton.png
    ├── Tests
    │   ├── __init__.py
    │   ├── test_configuration.py
    │   └── test_notification.py
    ├── configuration.py
    ├── main.py
    ├── SampleInfo.py
    ├── tmp
    │   └── temp_image.tiff
    └── utils.py
```

---

## 📦 Modules

<details closed><summary>Root</summary>

| File                                                                                     | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---                                                                                      | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| [configuration.py](https://github.com/twilight39/ALL2-IWMS/blob/master/configuration.py) | Provides functions for retrieving various file paths (e.g., Logs, Reports) and user preferences. Stores configuration options in a JSON-style config file.                                                                                       |
| [utils.py](https://github.com/twilight39/ALL2-IWMS/blob/master/utils.py)                 | Validates user input for various fields. Enhances user experience by providing immediate feedback on incorrect input. |
| [main.py](https://github.com/twilight39/ALL2-IWMS/blob/master/main.py)                   | Initializes and manages the graphical user interface (GUI) of the Keai Inventory Warehouse Management System (IWMS). The main.py file establishes the GUIs main window and sets up a loop to keep the application running.                                                                                                            |

</details>

<details closed><summary>Database</summary>

| File                                                                                                  | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ---                                                                                                   | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| [UnitTest.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Database/UnitTest.py)               | A test file used to populate the system with dummy data.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| [Notification.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Database/Notification.py)       | Manages user notifications within KEAI IWMS by communicating with the database and retrieving relevant notifications for employees. Handles notification storage in JSON format, and interacts with ToastNotification for real-time dekstop messaging to enhance user experience.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| [Database.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Database/Database.py)               | Establishes and handles the connection with the SQLite Database for KEAI IWMS. GUI Frames interact with this class to query, write and update data to the database. |
| [Authentication.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Database/Authentication.py)   | Verifies email and password inputs against database records encrypted with bcrypt hash functions. Responsible for account creation, update, and password reset operations.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

</details>

<details closed><summary>Tests</summary>

| File                                                                                                     | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---                                                                                                      | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| [test_configuration.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Tests/test_configuration.py) | This test module verifies that the Configuration Class functions correctly as a singleton, accesses files accordingly, and stores/retrieves data effectively.                                                                                                                                                                                          |
| [test_notification.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Tests/test_notification.py)   | This test module unit-tests essential functionalities of the Notification class. Key tests include verification of its role, proper initialization, notification reading, deletion and handling exclusions. The aim is to guarantee data integrity and user-specific functionality across the notification system. |

</details>

<details closed><summary>Frames</summary>

| File                                                                                                      | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ---                                                                                                       | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| [pageFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/pageFrame.py)                   | Abstract base class for Inventory Management GUI frames.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| [popup.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/popup.py)                           | Concrete base class for creating pop-ups. Used to handle user input before writing to database.                                                                                                                                                                                                                                                                                                                                                                                           |
| [Login.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/Login.py)                           | Creates a GUI to log in users. |
| [navigationFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/navigationFrame.py)       | Orchestrates  transitions between GUI frames, with each frame optimized for specific functions within IWMS, ensuring user-friendly interfaces and consistency across modules. |
| [dashboardFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/dashboardFrame.py)         | Creates a GUI for displaying an integrated warehouse and inventory overview.                                                                                                                                                                                                                                                                                                                                                           |
| [productFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/productFrame.py)             | Creates a GUI for updating product records.      |                                                                                                                                                                                                                                                                                                                                                                                        |
| [inventoryFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/inventoryFrame.py)         | Creates a GUI for updating inventory records.                                                                                                                                                                                                                                                                                            |
| [purchaseOrderFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/purchaseOrderFrame.py) | Creates a GUI for updating purchase order records.                                                                                                                                                 |
| [salesOrderFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/salesOrderFrame.py)       | Creates a GUI for updating sales order records.                                                                                                                                                              |
| [taskFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/taskFrame.py)                   | Creates a GUI for updating task records. Batch assignment of tasks is supported.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| [vendorFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/vendorFrame.py)               | Creates a GUI for updating vendor records.                                                                                                                                                                            |
| [reportsFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/reportsFrame.py)             | Creates a GUI for generating and viewing reports.                                                                                                                                                                                                                                                                                                                                     |
| [settingsPopup.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/settingsPopup.py)           | Creates a GUI for updating user settings, such as the profile picture, application theme or user password.                                                                                                                                                                                                                                                                                                                                                                                        |
| [notificationFrame.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/notificationFrame.py)   | Creates a GUI for viewing and managing notification records.                                                                                                                                               |
| [accountsPopup.py](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/accountsPopup.py)           | Creates a GUI for updating employee records. Only accessible to Administrators through the settings interface.                                                                                                                                              |
| [ui_preview_text.json](https://github.com/twilight39/ALL2-IWMS/blob/master/Frames/ui_preview_text.json)   | JSON text file containing UI text placeholders for interactive frames, streamlining user input prompts across various modules, enhancing user experience by providing standardized, clear, and consistent placeholders.                                                                                                                                                                                                                                                                                                                                                                                                                |


</details>

---

## 🚀 Getting Started

**System Requirements:**

* **Python**: `version 3.11.1`

### ⚙️ Installation

<h4>From <code>source</code></h4>

> 1. Clone the ALL2-IWMS repository:
>
> ```console
> $ git clone https://github.com/twilight39/ALL2-IWMS
> ```
>
> 2. Change to the project directory:
> ```console
> $ cd ALL2-IWMS
> ```
>
> 3. Install the dependencies:
> ```console
> $ pip install -r requirements.txt
> ```

### 🤖 Usage

<h4>From <code>source</code></h4>

> Run ALL2-IWMS using the command below:
> ```console
> $ python main.py
> ```
> The application will launch, and you will be directed to the login screen. Enter the default administrator 
> credentials to access the 
> dashboard.
> ```console
> Email: ahmad@gmail.com
> Password: admin1234
> ```
> You can also test the application with some dummy data. To do this, run the following command:
> ```console
> $ python SampleInfo.py
> ```
