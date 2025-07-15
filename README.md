# Parametric Anomaly QA Tool: Technical Documentation

**Version:** 1.0

**Date:** 2025-07-09

**Author:** Almohtadey Metwaly

## 1. Introduction

This document provides a comprehensive technical overview of the Parametric Anomaly QA Tool, a Python-based application designed to identify anomalies in parametric data. The tool is built using Streamlit, a powerful open-source framework for creating and sharing data applications. The core of the anomaly detection logic relies on the scikit-learn library, specifically the Isolation Forest algorithm, in conjunction with a set of custom-defined business rules for data validation.

The primary purpose of this tool is to automate the quality assurance (QA) process for parametric data by systematically identifying and flagging potential errors, inconsistencies, and outliers. By doing so, it aims to improve data integrity, reduce manual effort, and ensure that the data used for downstream applications is of the highest quality. The tool provides a user-friendly web interface that allows users to run analyses on a complete database, validate new data sets, and manage a list of approved anomalies.

This documentation is intended for a technical audience, including data scientists, engineers, and developers who are responsible for maintaining, extending, or deploying the tool. It covers the system architecture, setup and installation procedures, a detailed explanation of the anomaly detection methodologies, and guidelines for deployment and usage.

## 2. System Overview

The Parametric Anomaly QA Tool is a monolithic application that combines a user interface, data processing logic, and anomaly detection models into a single Python script. The application is designed to be run as a web service, accessible through a web browser.

### 2.1. Architecture

The application\'s architecture can be broken down into three main components:

*   **User Interface (UI):** The UI is built with Streamlit and provides an interactive web-based front-end for the tool. It allows users to upload files, trigger analyses, view results, and download reports. The UI is organized into distinct sections for different functionalities, such as running a full database analysis, validating new values, and managing approved anomalies.

*   **Data Processing and Anomaly Detection Engine:** This is the core of the application, where all the data loading, cleaning, preprocessing, and anomaly detection logic resides. It is implemented using the pandas library for data manipulation and scikit-learn for the machine learning-based anomaly detection. The engine incorporates a series of business rules to identify various types of anomalies, including invalid units, inconsistencies in data types, and statistical outliers.

*   **Data Storage:** The tool interacts with two primary data sources, both of which are expected to be in Excel format:
    *   **Main Parametric Database:** A comprehensive dataset containing the historical parametric data. The default filename for this is `Shot june2025-Parametric DB.xlsx`.
    *   **Approved Anomaly Values:** A master list of known and accepted anomalies. This file is used to prevent the tool from repeatedly flagging the same known deviations. The default filename is `Approved Anomaly Values.xlsx`.

### 2.2. Technology Stack

The tool is built upon a foundation of open-source Python libraries. The key technologies used are:

*   **Python:** The core programming language for the application. The recommended version is Python 3.11 or higher.
*   **Streamlit:** A web application framework for building interactive data science applications.
*   **pandas:** A powerful data analysis and manipulation library, used for handling all data-related operations.
*   **scikit-learn:** A machine learning library that provides the Isolation Forest algorithm for outlier detection.
*   **openpyxl:** A library for reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files.




## 3. Setup and Installation

This section outlines the steps required to set up and install the Parametric Anomaly QA Tool on a Linux server. It covers the necessary prerequisites, environment setup, and dependency installation.

### 3.1. Prerequisites

Before proceeding with the installation, ensure that your Linux server meets the following requirements:

*   **Operating System:** A Linux distribution (e.g., Ubuntu, CentOS, Debian).
*   **Python:** Python 3.11 or higher must be installed. The tool was developed and tested with **Python 3.11.0rc1**.
*   **Internet Connectivity:** Required for downloading Python packages and dependencies.

### 3.2. Environment Setup

It is highly recommended to use a virtual environment to manage the project\'s dependencies. This ensures that the project\'s libraries do not conflict with other Python projects on your system.

1.  **Update System Packages (Optional but Recommended):**
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2.  **Install `venv` Module (if not already installed):**
    ```bash
    sudo apt install python3.11-venv -y
    ```

3.  **Navigate to your desired project directory:**
    ```bash
    cd /path/to/your/project
    ```

4.  **Create a virtual environment:**
    ```bash
    python3.11 -m venv venv
    ```

5.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```
    (Your terminal prompt should change to indicate the active virtual environment, e.g., `(venv) user@hostname:~/project$`)

### 3.3. Dependency Installation

Once the virtual environment is activated, you can install the required Python libraries. The following libraries and their versions were used during development:

*   **pandas**: **2.3.0**
*   **scikit-learn**: **1.7.0**
*   **streamlit**: **1.46.1**
*   **openpyxl**: (Installed as a dependency of pandas, typically latest compatible version)

To install these dependencies, create a `requirements.txt` file in your project directory with the following content:

```
pandas==2.3.0
scikit-learn==1.7.0
streamlit==1.46.1
openpyxl
```

Then, install them using pip:

```bash
pip install -r requirements.txt
```

### 3.4. Data File Placement

The application expects the following Excel files to be present in a `data` directory relative to the main script:

*   `Shot june2025-Parametric DB.xlsx`
*   `Approved Anomaly Values.xlsx`

Create a `data` directory within your project and place these files inside it. For example, if your main script is `app.py`:

```
/path/to/your/project/
├── app.py
├── requirements.txt
└── data/
    ├── Shot june2025-Parametric DB.xlsx
    └── Approved Anomaly Values.xlsx
```

**Important Note on Hardcoded Paths:** The provided code contains hardcoded Windows file paths (e.g., `C:\Users\145989\OneDrive - Arrow Electronics, Inc\Desktop\sql OUTPUT\1st project ML Parametric\API\Shot june2025-Parametric DB.xlsx`). For deployment on a Linux server, these paths **must be updated** to reflect the correct Linux file system structure. It is recommended to use relative paths or environment variables for better portability. For example, the `file_path` and `approved_file_path` variables in `run_anomaly_detection` already use `os.path.join(os.path.dirname(os.path.abspath(__file__)), \'..\', \'data\', \'...')`, which is a good practice. However, the `db_file_path` and `output_path` in `validate_uploaded_values` and `main` functions still use absolute Windows paths and need to be changed.

Example of path modification in `validate_uploaded_values`:

```python
# Original (Windows path)
# db_file_path = r\'C:\Users\145989\OneDrive - Arrow Electronics, Inc\Desktop\sql OUTPUT\1st project ML Parametric\API\Shot june2025-Parametric DB.xlsx\'

# Modified for Linux (assuming \'data\' directory is sibling to script)
db_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \'..\', \'data\', \'Shot june2025-Parametric DB.xlsx\')
```

And in the `main` function for `output_path`:

```python
# Original (Windows path)
# output_path = r\'C:\Users\145989\OneDrive - Arrow Electronics, Inc\Desktop\sql OUTPUT\1st project ML Parametric\patch2\Anomalies_Of_parametrics22_6.xlsx\'

# Modified for Linux (example, adjust as needed)
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \'output\', \'Anomalies_Of_parametrics22_6.xlsx\')
# Ensure the \'output\' directory exists or create it programmatically
# os.makedirs(os.path.dirname(output_path), exist_ok=True)
```

These changes are crucial for the application to function correctly in the Linux environment.


## 4. Detailed Functionality and Business Rules

This section delves into the specifics of each core function within the Parametric Anomaly QA Tool, explaining their purpose, internal logic, and the business rules they implement for anomaly detection and data validation.

### 4.1. `run_anomaly_detection()`

This function is the primary entry point for performing anomaly detection on the main parametric dataset. It orchestrates a series of steps, from data loading and preprocessing to the application of various anomaly detection techniques.

#### 4.1.1. Data Loading and Initial Preprocessing

The function begins by loading the main parametric database, `Shot june2025-Parametric DB.xlsx`, and the `Approved Anomaly Values.xlsx` file. The latter is crucial for excluding known anomalies from the detection process, ensuring that the tool focuses on new or unapproved deviations. Data is then cleaned by dropping rows with any missing values, which is a common first step in preparing data for analysis.

#### 4.1.2. Value Type Conversion and Categorization

A critical step involves converting the `VALUE` column to a numeric format (`VALUE_NUMERIC`) where possible. Non-numeric values are flagged, and a special `is_numeric_majority` flag is introduced. This flag uses custom logic to determine if a value, even if not strictly numeric, should be considered numeric for the purpose of majority calculations within groups. This accounts for specific data entry conventions where numeric ranges or multiple values might be represented in a single string (e.g., \'10|20\', \'5/10\', \'1 to 15\').

To facilitate group-based analysis, a `GROUP` identifier is created by concatenating `PL_NAME` and `FET_NAME`. This ensures that anomaly detection and validation rules are applied within relevant subsets of the data.

#### 4.1.3. Unit Validation

One of the fundamental business rules implemented is the validation of units. The tool maintains a comprehensive dictionary, `valid_units`, which maps various `FET_NAME` categories (e.g., \'Current\', \'Voltage\', \'Temperature\', \'Frequency\') to a list of their respective valid units (e.g., \'A\', \'V\', \'c\', \'k\', \'Hz\').

The `is_valid_unit` helper function checks if the `UNIT` associated with a `FET_NAME` is appropriate. This validation supports partial matches and handles compound units (e.g., \'A|V\'), ensuring flexibility while maintaining data integrity. Any record with an invalid unit for its measurement type is immediately flagged as an anomaly with the reason \'Invalid unit for measurement; \'.

#### 4.1.4. Isolation Forest for Numeric Outliers

For numerical data, the Isolation Forest algorithm from `scikit-learn` is employed to detect statistical outliers. This unsupervised learning algorithm is particularly effective for high-dimensional datasets and does not require prior knowledge of data distribution. It works by randomly selecting a feature and then randomly selecting a split value between the maximum and minimum values of the selected feature. This partitioning is repeated recursively until each instance is isolated. Anomalies are points that require fewer splits to be isolated.

The algorithm is applied independently to the `VALUE_NUMERIC` column within each `GROUP`. The `contamination` parameter is set to `0.0001`, which represents the expected proportion of outliers in the dataset. This parameter is a critical configuration point and can be adjusted based on the domain\'s understanding of anomaly prevalence. Records identified as outliers by Isolation Forest are flagged with the reason \'Isolation Forest anomaly detected; \'.

#### 4.1.5. PL Group Majority Type Anomaly Detection

This rule addresses inconsistencies in data types within `PL_NAME` groups. The logic determines the predominant data type (numeric or non-numeric) for each `PL_NAME` group. If a value within that group deviates from this majority type (e.g., a non-numeric value appears in a group that is overwhelmingly numeric, or vice-versa), it is flagged as an anomaly. This helps catch data entry errors or unexpected variations in data representation within a product line.

#### 4.1.6. Non-numeric Value Format Check

Beyond unit validation, this rule specifically targets non-numeric values that do not conform to expected formats. It flags non-numeric entries in the `VALUE` column that do not contain any of the predefined allowed special characters (\'|\', \'/\', \'to\', \'!', \' \', \'!!\'). This helps identify free-text entries that might be erroneous or uninterpretable, ensuring that non-numeric data adheres to a structured or semi-structured format.

#### 4.1.7. Controlled Anomaly Condition (Post-processing)

After initial anomaly detection, a post-processing step applies a \'Controlled Anomaly\' condition. For anomalies initially flagged by Isolation Forest, the function calculates the average `VALUE_NUMERIC` for their respective `GROUP`. If the difference between the anomalous `VALUE_NUMERIC` and the group\'s average falls within a specified tolerance band (currently `+/- 50`), the anomaly is reclassified as \'controlled\' and is *not* included in the final anomaly report. This rule acts as a filter, allowing for minor, acceptable deviations around a group\'s mean to be ignored, preventing false positives for small fluctuations.

#### 4.1.8. Output

The function returns a pandas DataFrame containing all detected anomalies, along with detailed information such as `PL_NAME`, `FET_NAME`, `VALUE_ID`, the original `VALUE`, its numeric conversion (`VALUE_NUMERIC`), `UNIT`, the calculated `Average` and `Median` for the group (if an Isolation Forest anomaly was detected), the `GROUP` identifier, a boolean `ANOMALY` flag, and a concatenated `ANOMALY_REASON` string explaining why each record was flagged.

### 4.2. `validate_uploaded_values(uploaded_file)`

This function is designed to validate new or external datasets against the existing historical database. It ensures that newly introduced data conforms to established patterns and rules.

#### 4.2.1. Data Loading and Preprocessing

Similar to `run_anomaly_detection`, this function loads the main database (`Shot june2025-Parametric DB.xlsx`) and the `uploaded_file`. Approved anomalies are also excluded from the uploaded data to avoid flagging already known deviations. A crucial initial check verifies that the uploaded file contains all required columns: `PL_NAME`, `FET_NAME`, `VALUE`, and `UNIT`. Missing columns will result in an error and halt the validation process.

Preprocessing steps, including cleaning, group creation, and numeric conversion, are applied to the uploaded data, mirroring the steps in `run_anomaly_detection` to ensure consistency in data preparation.

#### 4.2.2. Unit Validation

The same `is_valid_unit` logic and `valid_units` dictionary used in `run_anomaly_detection` are applied here. This ensures that new data adheres to the same unit standards as the historical data. Invalid units are flagged, and the `VALIDATION_STATUS` is set to \'Invalid\'.

#### 4.2.3. Database Outlier Check

This is a key validation rule. For each record in the uploaded data, the function compares its `VALUE_NUMERIC` against the statistical distribution of the corresponding `GROUP` in the historical database. Specifically, it calculates the mean and standard deviation of `VALUE_NUMERIC` for that group from the `db_data`.

An uploaded value is flagged as an outlier if it deviates by more than 3 standard deviations from the mean of its group in the historical database. This rule helps identify values that are statistically improbable given past observations for that specific `PL_NAME` and `FET_NAME` combination. The `VALIDATION_STATUS` for such records is set to \'Outlier\', and `DB_MEAN`, `DB_STD`, and `DB_COUNT` are provided for context.

#### 4.2.4. Group Not Found Check

If an uploaded record\'s `GROUP` (combination of `PL_NAME` and `FET_NAME`) does not exist in the historical database, it is flagged as an anomaly. This rule is important for identifying entirely new parametric combinations that have no historical context, which might warrant further investigation or manual approval.

#### 4.2.5. Output

The function returns a DataFrame with the uploaded data, augmented with `ANOMALY` flags, `ANOMALY_REASON` strings, and a `VALIDATION_STATUS` column (\'Valid\', \'Invalid\', \'Outlier\', \'Not Found\'). It also includes `DB_MEAN`, `DB_STD`, and `DB_COUNT` for records that were compared against the database.

### 4.3. `load_approved_anomalies(approved_file_path)`

This utility function is responsible for loading the master list of approved anomalies from the specified Excel file (`Approved Anomaly Values.xlsx`). It includes basic error handling, returning an empty pandas DataFrame if the file does not exist or cannot be read. This ensures that the main anomaly detection and validation processes can proceed without interruption, even if the approved anomalies file is missing or corrupted.

### 4.4. `append_approved_anomalies(uploaded_file, approved_file_path)`

This function allows users to update the master `Approved Anomaly Values.xlsx` file by appending new approved anomalies from an uploaded Excel file. It performs a check to ensure the uploaded file contains the required columns (`PL_NAME`, `FET_NAME`, `VALUE`). The function then loads the existing approved anomalies, concatenates them with the newly uploaded ones, removes any duplicate entries to maintain a clean list, and saves the combined, deduplicated list back to the `approved_file_path`. This mechanism provides a way to continuously refine the anomaly detection process by incorporating feedback and acknowledging legitimate data points that might otherwise be flagged as anomalies.

### 4.5. `main()` (Streamlit Application Entry Point)

The `main()` function serves as the entry point for the Streamlit web application. It configures the Streamlit page, applies custom CSS for styling, and sets up the interactive user interface elements.

#### 4.5.1. Page Configuration and Styling

It sets the page title, icon, layout, and initial sidebar state. Custom CSS is embedded to apply a blue theme, enhancing the visual appeal and branding of the application. This includes styling for buttons and the main background.

#### 4.5.2. User Interface Sections

The UI is logically divided into several sections:

*   **Tool Information Sidebar:** Provides a brief overview of the tool\'s capabilities and the anomaly detection methods employed.

*   **"Validate New Values" Section:** Features a file uploader for users to submit new Excel files for validation. Upon submission, it calls `validate_uploaded_values`, displays a preview of the results, and provides a download button for a detailed validation report in Excel format.

*   **"Run Entire Database Analysis" Section:** Contains a button to trigger the `run_anomaly_detection` function on the pre-configured main database. After the analysis, it presents summary metrics (total anomalies, unique PL/FET names), a sample of the detected anomalies, and a download button for the full anomaly report. It also attempts to save the report to a specified local path.

*   **"Upload Approved Anomaly" Section:** Provides a file uploader for users to submit Excel files containing new approved anomalies. This section utilizes the `append_approved_anomalies` function to update the master list, effectively teaching the system to ignore specific data points in future analyses.

#### 4.5.3. Hardcoded Paths in UI Logic

It is important to reiterate that some hardcoded Windows paths appear within the `main()` function, particularly for the `output_path` when saving the anomaly report. These paths must be reviewed and adjusted for the Linux deployment environment to ensure proper file saving and access. For example, the line `output_path = r\'C:\Users\145989\OneDrive - Arrow Electronics, Inc\Desktop\sql OUTPUT\1st project ML Parametric\patch2\Anomalies_Of_parametrics22_6.xlsx\'` needs to be changed to a suitable Linux path, such as `/home/ubuntu/output/Anomalies_Of_parametrics22_6.xlsx` or a path relative to the application\'s root directory.

## 5. Configuration Parameters

The tool\'s behavior can be influenced by several key configuration parameters embedded within the code. Understanding and potentially adjusting these parameters is crucial for fine-tuning the anomaly detection process to specific business needs and data characteristics.

*   **Isolation Forest Contamination (`contamination=0.0001`)**: Located in the `apply_isolation_forest` sub-function within `run_anomaly_detection()`. This parameter estimates the proportion of outliers in the dataset. A higher value will result in more anomalies being detected. The current setting of `0.0001` suggests an expectation of very few outliers. This value should be adjusted based on the actual prevalence of anomalies in your data.

*   **Controlled Anomaly Threshold (`-50 <= (avg - row[\'VALUE_NUMERIC\']) <= 50`)**: Found in the `apply_controlled_anomaly_condition` sub-function within `run_anomaly_detection()`. This defines a tolerance band around the group\'s average. Anomalies detected by Isolation Forest that fall within this `+/- 50` range are considered \'controlled\' and are not reported. This parameter allows for ignoring minor, acceptable deviations that might otherwise be flagged as anomalies. Adjusting this range can help reduce false positives for small fluctuations.

*   **Database Outlier Threshold (`> 3 * db_std`)**: Used in the `validate_uploaded_values()` function. This rule flags an uploaded value as an outlier if it is more than 3 standard deviations away from the mean of its corresponding group in the historical database. The `3` standard deviations represent a common statistical threshold for outliers. This value can be modified to make the validation more or less stringent (e.g., `2` for more sensitivity, `4` for less).

*   **Allowed Non-numeric Characters (`\'|\', \'/\', \'to\', \'!', \' \', \'!!\'`)**: Defined in the `is_non_numeric_anomaly` sub-function within `detect_non_numeric_anomaly` in `run_anomaly_detection()`. These characters are considered acceptable within non-numeric `VALUE` entries. If your data contains other specific non-numeric patterns that should be allowed, they need to be added to this list.

*   **Valid Units Dictionary (`valid_units`)**: This dictionary, present in both `run_anomaly_detection()` and `validate_uploaded_values()`, is a critical configuration for unit validation. It maps `FET_NAME` categories to lists of valid units. Any updates to measurement types or their associated units must be reflected in this dictionary to ensure accurate unit validation.

*   **Hardcoded File Paths**: As previously mentioned, several file paths are hardcoded within the script. These include the paths to the main database, the approved anomalies file, and the output path for generated reports. These paths (`file_path`, `approved_file_path`, `db_file_path`, `output_path`) must be updated to reflect the actual locations on the deployment server. It is highly recommended to use relative paths or environment variables for these configurations to enhance portability and ease of deployment across different environments.

## 6. Deployment on Linux Server

Deploying the Parametric Anomaly QA Tool on a Linux server involves ensuring the environment is correctly set up, the application files are in place, and the Streamlit application is launched. This section provides a step-by-step guide for deployment.

### 6.1. Prepare the Server Environment

Follow the steps outlined in Section 3.2 (Environment Setup) to create and activate a Python virtual environment on your Linux server. Ensure all necessary system packages are installed.

### 6.2. Transfer Application Files

Copy the entire project directory (including `app.py`, `requirements.txt`, and the `data` directory with your Excel files) to your Linux server. A common location might be `/home/ubuntu/parametric_anomaly_tool/`.

```bash
# Example using scp from your local machine
scp -r /path/to/local/project_directory ubuntu@your_server_ip:/home/ubuntu/parametric_anomaly_tool/
```

### 6.3. Update Hardcoded Paths

**This is a critical step.** As noted in Section 3.4 and Section 5, several file paths are hardcoded in the `app.py` script using Windows-style paths. You **must** edit `app.py` on the Linux server to update these paths to their correct Linux equivalents. For example:

*   Change `db_file_path = r\'C:\Users\...\'` to `db_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \'data\', \'Shot june2025-Parametric DB.xlsx\')`
*   Change `output_path = r\'C:\Users\...\'` to a suitable Linux path, e.g., `output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), \'output\', \'Anomalies_Of_parametrics22_6.xlsx\')`. Remember to create the `output` directory if it doesn\'t exist: `mkdir -p /home/ubuntu/parametric_anomaly_tool/output`.

### 6.4. Install Dependencies

Navigate to your project directory on the Linux server, activate the virtual environment, and install the Python dependencies using the `requirements.txt` file:

```bash
cd /home/ubuntu/parametric_anomaly_tool/
source venv/bin/activate
pip install -r requirements.txt
```

### 6.5. Run the Streamlit Application

Once all dependencies are installed and paths are updated, you can launch the Streamlit application:

```bash
streamlit run app.py --server.port 8503 --server.address 0.0.0.0
```

*   `app.py`: Replace with the actual name of your main Python script.
*   `--server.port 8503`: Specifies the port on which the Streamlit application will run. The user provided `http://10.199.104.150:8503/` as the tool link, so port `8503` is used.
*   `--server.address 0.0.0.0`: Makes the application accessible from any IP address, which is necessary for external access on a server.

### 6.6. Access the Application

After running the command, Streamlit will typically provide a network URL. You can access the application from your web browser using the IP address of your Linux server and the specified port. Based on the provided information, the tool should be accessible at:

`http://10.199.104.150:8503/`

### 6.7. Running as a Background Process (Optional)

For continuous operation, you might want to run the Streamlit application as a background process. Tools like `nohup` or `screen` can be used for this purpose.

**Using `nohup`:**

```bash
nohup streamlit run app.py --server.port 8503 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

This command will run the Streamlit app in the background and redirect its output to `streamlit.log`. You can then close your terminal session without stopping the application.

**Using `screen`:**

1.  Install `screen` if not already present: `sudo apt install screen -y`
2.  Start a new screen session: `screen -S anomaly_app`
3.  Inside the screen session, navigate to your project directory and run the Streamlit app: `cd /home/ubuntu/parametric_anomaly_tool/ && source venv/bin/activate && streamlit run app.py --server.port 8503 --server.address 0.0.0.0`
4.  Detach from the screen session (the app will continue running): Press `Ctrl+A` then `D`.
5.  To reattach to the session: `screen -r anomaly_app`

### 6.8. Confluence Page Reference

The user also provided a Confluence page link related to the Anomaly Detection Project on Parametric Data:

`https://arrowecommerce.atlassian.net/wiki/spaces/~880510370/pages/3988226051/Anomaly+Detection+Project+on+Parametric+Data`

This page likely contains additional business context, project details, or historical information relevant to the tool. It should be consulted for a complete understanding of the project\'s scope and requirements.

## 7. Conclusion

The Parametric Anomaly QA Tool provides a robust and flexible solution for maintaining the quality and integrity of parametric data. By combining statistical methods like Isolation Forest with custom business rules for unit validation and data consistency, it offers a comprehensive approach to anomaly detection. The Streamlit interface ensures ease of use, while the detailed documentation provided herein aims to facilitate its deployment, maintenance, and future development.

Continued monitoring of the tool\'s performance, regular updates to the `Approved Anomaly Values.xlsx` file, and periodic review of the configuration parameters (e.g., Isolation Forest contamination, controlled anomaly threshold) are recommended to ensure its ongoing effectiveness and accuracy.

## 8. References

[1] pandas documentation: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)

[2] scikit-learn documentation: [https://scikit-learn.org/stable/documentation.html](https://scikit-learn.org/stable/documentation.html)

[3] Streamlit documentation: [https://docs.streamlit.io/](https://docs.streamlit.io/)

[4] openpyxl documentation: [https://openpyxl.readthedocs.io/en/stable/](https://openpyxl.readthedocs.io/en/stable/)

[5] Confluence Page: [https://arrowecommerce.atlassian.net/wiki/spaces/~880510370/pages/3988226051/Anomaly+Detection+Project+on+Parametric+Data](https://arrowecommerce.atlassian.net/wiki/spaces/~880510370/pages/3988226051/Anomaly+Detection+Project+on+Parametric+Data)


