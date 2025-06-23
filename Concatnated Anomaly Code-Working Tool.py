import pandas as pd
from sklearn.ensemble import IsolationForest
import warnings
import streamlit as st
import os
from datetime import datetime
import io

# Suppress warnings
warnings.filterwarnings('ignore')

def run_anomaly_detection():
    """Run the entire anomaly detection process"""
    
    # Load data
    file_path = r'C:\Users\145989\OneDrive - Arrow Electronics, Inc\Desktop\sql OUTPUT\1st project ML Parametric\API\Shot june2025-Parametric DB.xlsx'
    
    try:
        data = pd.read_excel(file_path)
        st.success(f"✅ Data loaded successfully! Found {len(data)} records.")
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

    # Clean and preprocess data
    data_cleaned = data.dropna().copy()
    st.info(f"📊 After cleaning: {len(data_cleaned)} records remaining")
    
    pl_name_col = 'PL_NAME'
    fet_name_col = 'FET_NAME'
    VALUE_ID_col = 'VALUE_ID'
    value_col = 'VALUE'
    unit_col = 'UNIT'

    # Convert VALUE to numeric and flag non-numeric values for Isolation Forest only
    data_cleaned['VALUE_NUMERIC'] = pd.to_numeric(data_cleaned[value_col], errors='coerce')
    data_cleaned['is_numeric'] = data_cleaned['VALUE_NUMERIC'].notna()

    # Define custom logic for |, /, or 'to' in the majority/minority calculation
    def custom_majority_check(value):
        if pd.notna(value) and any(sub in str(value) for sub in ['|', '/', 'to', '!', ' '] ):
            return True  # Treat as numeric for majority/minority calculation
        return pd.notna(pd.to_numeric(value, errors='coerce'))

    data_cleaned['is_numeric_majority'] = data_cleaned[value_col].apply(custom_majority_check)

    # Combine PL_NAME and FET_NAME to create a unique group identifier
    data_cleaned['GROUP'] = data_cleaned[pl_name_col].astype(str) + '_' + data_cleaned[fet_name_col].astype(str)

    # Define valid units for different types of measurements
    valid_units = {
        'Current': ['A'],
        'Voltage': ['V'],
        'Weight': ['g','lb', 'oz'],
        'Frequency': ['Hz'],
        'Resistance': ['Ohm'],
        'Power': ['W','dB','VA','HP'],
        'Capacitance': ['F'],
        'Impedance': ['Ohm'],
        'Gain': ['dB'],
        'Thermal': ['c', 'k', '°'] ,
        'Temperature': ['c', 'k', '°'] ,
        'Tolerance': ['%','ppm','ppb'] ,
        'Ratio': ['%'] ,
        'Efficiency': ['%'] ,
        'Aging': ['Year','ppm'] ,
        'Noise': ['db','ppm'] ,
        'Stability': ['ppm'] ,
        'Sensitivity': ['db'] ,
        'Gain Bandwidth': ['Hz'] ,
        'Breaking Capacity': ['A'] ,
        'Gain Attenuation': ['dB'] ,
        'Loss': ['dB'],
        'Mean Spherical Candle Power': ['MSCP'],
        'Minimum Isolation Voltage' : ['db'] , 
          'Current': ['A'], 'Voltage': ['V'], 'Weight': ['g','lb', 'oz'], 'Frequency': ['Hz'],
        'Resistance': ['Ohm'], 'Power': ['W','dB','VA','HP'], 'Capacitance': ['F'], 'Impedance': ['Ohm'],
        'Gain': ['dB'], 'Thermal': ['c', 'k', '°'], 'Temperature': ['c', 'k', '°'],
        'Tolerance': ['%','ppm','ppb'], 'Ratio': ['%'], 'Efficiency': ['%'], 'Aging': ['Year','ppm'],
        'Noise': ['db','ppm'], 'Stability': ['ppm'], 'Sensitivity': ['db'], 'Gain Bandwidth': ['Hz'],
        'Breaking Capacity': ['A'], 'Gain Attenuation': ['dB'], 'Loss': ['dB'], 'Mean Spherical Candle Power': ['MSCP'],
        'Minimum Isolation Voltage' : ['db'] ,
        'time' : ['s','min','h','ns','d','month','year',''],
        'color': [''],
        'depth': ['m','cm','mm','in','ft','mile'],
        'height' : ['m','cm','mm','in','ft','mile'],
        'length' : ['m','cm','mm','in','ft','mile'],
        'size' : ['m','cm','mm','in','gallon','AWG','b','B','bit','byte','oz','word','pixel','cc','ounce'],
        'Rate' : [    'bps', 'sps', 'N/mm', 'Hz', 'V/us', 'SCFM|GPH', 'r/min', 'bE', 'lbs/in', 'N.mm/deg', 'WPS', 'L/min', 'Bd', 'fps', 'Gbps', 'lb/in', 'L/sec', 'm³/h', 'gpm', 'slm', 'slpm', 
        'sccm', 'g', 'SPS', 'm/s', 'ft/min', 'scfh', 'Grms', 'ft²/min', 
        'Gs', 's', '', 'Tps', 'baud', 'CFM', 'rpm'] ,
        'Material': ['','  '],
        'Diameter' : ['m','cm','mm','in','ft','mile'],
        'speed' : ['m/s','km/h','mph','hz','kph','rpm','pbs','rps','cm/s','ft/s','G','Sec','bps'],
        'width' : ['m','cm','mm','in','ft','mile','°','pbs','hz'],
        'dimension' : ['m'],
        'thickness' : ['m','in'],
        'mounting' : ['m','in',''],
        'Coefficient' : ['%'],
        'noise': ['dB','db','ppm','%'],
        'gender': [''],
        'Supported Device' :['','  '],
        'area' : ['m2','cm2','mm2','inch2','ft2','acre'],
        'volume' : ['m3','cm3','mm3','inch3','ft3','liter'],
        'pressure' : ['Pa','kPa','MPa','bar','psi'],
        'energy' : ['J','kJ','cal','Wh','kWh'],
        'power' : ['W','kW','MW'],
        'torque' : ['Nm','lb-ft','kg-m'],
        'force' : ['N','kN','lb','kg'],
        'acceleration' : ['m/s2','g'],
        'density' : ['kg/m3','g/cm3','lb/in3'] ,
        'type': ['','°','bit',' '],
        'Bandwidth' : ['Hz','bps'],
        'number' : ['','Turns','key','byte','b',' ']
    }

    # Updated function to validate units based on FET_NAME with partial match support
    def is_valid_unit(unit, fet_name):
        if pd.isna(unit):  # Handle missing units
            return False
        unit_parts = str(unit).lower().split('|')  # Split compound units
        unit_valid = False
        for part in unit_parts:
            part = part.strip()  # Clean whitespace
            for key, units in valid_units.items():
                if key.lower() in str(fet_name).lower():  # Match FET_NAME to valid unit types
                    if any(valid_unit.lower() in part for valid_unit in units):
                        unit_valid = True
                        break  # Stop checking once a match is found
        return unit_valid

    # Initialize anomaly detection columns
    data_cleaned['ANOMALY'] = False
    data_cleaned['ANOMALY_REASON'] = ''

    # Detect invalid units
    invalid_unit_mask = ~data_cleaned.apply(lambda row: is_valid_unit(row[unit_col], row[fet_name_col]), axis=1)
    data_cleaned.loc[invalid_unit_mask, 'ANOMALY'] = True
    data_cleaned.loc[invalid_unit_mask, 'ANOMALY_REASON'] += 'Invalid unit for measurement; '

    # Apply Isolation Forest for numeric anomalies
    def apply_isolation_forest(group):
        numeric_rows = group[group['is_numeric']].copy()
        numeric_rows = numeric_rows.dropna(subset=['VALUE_NUMERIC'])  # Drop NaNs before applying Isolation Forest
        if len(numeric_rows) > 1:
            features = numeric_rows[['VALUE_NUMERIC']].astype(float)
            iso_forest = IsolationForest(contamination=0.0001, random_state=42)
            iso_forest.fit(features)
            predictions = iso_forest.predict(features)
            anomaly_mask = predictions == -1
            group.loc[numeric_rows.index[anomaly_mask], 'ANOMALY'] = True
            group.loc[numeric_rows.index[anomaly_mask], 'ANOMALY_REASON'] += 'Isolation Forest anomaly detected; '
        return group

    data_cleaned = data_cleaned.groupby('GROUP', group_keys=False).apply(apply_isolation_forest)

    # Detect PL group anomalies based on majority type
    def detect_pl_group_anomaly(df):
        pl_group = df.groupby(pl_name_col)
        majority_types = pl_group['is_numeric_majority'].agg(['sum', 'count'])
        majority_types['non_numeric'] = majority_types['count'] - majority_types['sum']
        majority_types['PL_MAJORITY_TYPE'] = majority_types.apply(
            lambda row: 'numeric' if row['sum'] > row['non_numeric'] else 'non_numeric', axis=1
        )
        df = df.merge(
            majority_types['PL_MAJORITY_TYPE'],
            left_on=pl_name_col,
            right_index=True,
            how='left'
        )
        mask_numeric_majority = df['PL_MAJORITY_TYPE'] == 'numeric'
        mask_non_numeric_majority = df['PL_MAJORITY_TYPE'] == 'non_numeric'
        mask_anomaly_numeric = mask_numeric_majority & (~df['is_numeric_majority'])
        mask_anomaly_non_numeric = mask_non_numeric_majority & (df['is_numeric_majority'])
        df.loc[mask_anomaly_numeric, 'ANOMALY'] = True
        df.loc[mask_anomaly_numeric, 'ANOMALY_REASON'] += 'PL majority is numeric but value is non-numeric; '
        df.loc[mask_anomaly_non_numeric, 'ANOMALY'] = True
        df.loc[mask_anomaly_non_numeric, 'ANOMALY_REASON'] += 'PL majority is non-numeric but value is numeric; '
        return df

    data_cleaned = detect_pl_group_anomaly(data_cleaned)

    # Detect non-numeric anomalies
    def detect_non_numeric_anomaly(df):
        def is_non_numeric_anomaly(value):
            if pd.notna(value):
                if any(char in str(value) for char in ['|', '/', 'to', '!', ' ','!!'] ):
                    return False
                try:
                    float(value)
                    return False
                except ValueError:
                    return True
            return True

        anomaly_mask = df[value_col].apply(is_non_numeric_anomaly)
        df.loc[anomaly_mask, 'ANOMALY'] = True
        df.loc[anomaly_mask, 'ANOMALY_REASON'] += 'Non-numeric value without allowed characters; '
        return df

    data_cleaned = detect_non_numeric_anomaly(data_cleaned)

    # Clean up anomaly reason column
    data_cleaned['ANOMALY_REASON'] = data_cleaned['ANOMALY_REASON'].str.rstrip('; ').replace('', 'No anomaly')

    # Calculate the average and median value per GROUP for anomalies detected by Isolation Forest
    def calculate_average_and_median(group):
        if 'Isolation Forest anomaly detected' in group['ANOMALY_REASON'].values:
            group['Average'] = group['VALUE_NUMERIC'].mean()
            group['Median'] = group['VALUE_NUMERIC'].median()  # Adding median calculation
        else:
            group['Average'] = None
            group['Median'] = None  # If no anomaly, set median to None
        return group

    # Apply the updated function to calculate both average and median
    data_cleaned = data_cleaned.groupby('GROUP', group_keys=False).apply(calculate_average_and_median)

    # Extract anomalies for output
    anomalies = data_cleaned[data_cleaned['ANOMALY']]

    # Define the Controlled Anomaly condition
    def apply_controlled_anomaly_condition(group):
        avg = group['Average'].mean()  # Calculate the average for the group
        group['Controlled_Anomaly'] = group.apply(
            lambda row: -50 <= (avg - row['VALUE_NUMERIC']) <= 50, axis=1
        )  # Check if the difference between average and VALUE_NUMERIC is in the controlled range
        return group

    # Apply the Controlled Anomaly condition to each group
    data_cleaned = data_cleaned.groupby('GROUP', group_keys=False).apply(apply_controlled_anomaly_condition)

    # Filter out anomalies that are within the controlled range (if Controlled_Anomaly is True)
    anomalies = data_cleaned[(data_cleaned['ANOMALY']) & (~data_cleaned['Controlled_Anomaly'])]

    # Define output columns, including the Controlled_Anomaly column
    output_columns = [
        pl_name_col,
        fet_name_col,
        VALUE_ID_col,
        value_col,
        'VALUE_NUMERIC',
        unit_col,
        'Average',
        'Median',
        'GROUP',
        'ANOMALY',
        'ANOMALY_REASON'
    ]

    st.success(f"🎯 Anomaly detection completed! Found {len(anomalies)} anomalies.")
    
    return anomalies[output_columns]

def validate_uploaded_values(uploaded_file):
    """Validate uploaded values against the database"""
    
    # Load the main database
    db_file_path = r'C:\Users\145989\OneDrive - Arrow Electronics, Inc\Desktop\sql OUTPUT\1st project ML Parametric\API\Shot june2025-Parametric DB.xlsx'
    
    try:
        db_data = pd.read_excel(db_file_path)
        st.success(f"✅ Database loaded successfully! Found {len(db_data)} records.")
    except Exception as e:
        st.error(f"❌ Error loading database: {str(e)}")
        return None
    
    # Load uploaded file
    try:
        uploaded_data = pd.read_excel(uploaded_file)
        st.success(f"✅ Uploaded file loaded successfully! Found {len(uploaded_data)} records.")
    except Exception as e:
        st.error(f"❌ Error loading uploaded file: {str(e)}")
        return None
    
    # Check required columns
    required_columns = ['PL_NAME', 'FET_NAME','VALUE', 'UNIT']
    missing_columns = [col for col in required_columns if col not in uploaded_data.columns]
    
    if missing_columns:
        st.error(f"❌ Missing required columns: {missing_columns}")
        st.info("Required columns: PL_NAME, FET_NAME, VALUE, UNIT")
        return None
    
    # Clean and preprocess uploaded data
    uploaded_cleaned = uploaded_data.dropna().copy()
    st.info(f"📊 After cleaning uploaded data: {len(uploaded_cleaned)} records remaining")
    
    # Combine PL_NAME and FET_NAME to create a unique group identifier
    uploaded_cleaned['GROUP'] = uploaded_cleaned['PL_NAME'].astype(str) + '_' + uploaded_cleaned['FET_NAME'].astype(str)
    
    # Convert VALUE to numeric
    uploaded_cleaned['VALUE_NUMERIC'] = pd.to_numeric(uploaded_cleaned['VALUE'], errors='coerce')
    uploaded_cleaned['is_numeric'] = uploaded_cleaned['VALUE_NUMERIC'].notna()
    
    # Define custom logic for majority check
    def custom_majority_check(value):
        if pd.notna(value) and any(sub in str(value) for sub in ['|', '/', 'to', '!', ' '] ):
            return True
        return pd.notna(pd.to_numeric(value, errors='coerce'))
    
    uploaded_cleaned['is_numeric_majority'] = uploaded_cleaned['VALUE'].apply(custom_majority_check)
    
    # Define valid units (same as in main function)
    valid_units = {
        'Current': ['A'],
        'Voltage': ['V'],
        'Weight': ['g','lb', 'oz'],
        'Frequency': ['Hz'],
        'Resistance': ['Ohm'],
        'Power': ['W','dB','VA','HP'],
        'Capacitance': ['F'],
        'Impedance': ['Ohm'],
        'Gain': ['dB'],
        'Thermal': ['c', 'k', '°'] ,
        'Temperature': ['c', 'k', '°'] ,
        'Tolerance': ['%','ppm','ppb'] ,
        'Ratio': ['%'] ,
        'Efficiency': ['%'] ,
        'Aging': ['Year','ppm'] ,
        'Noise': ['db','ppm'] ,
        'Stability': ['ppm'] ,
        'Sensitivity': ['db'] ,
        'Gain Bandwidth': ['Hz'] ,
        'Breaking Capacity': ['A'] ,
        'Gain Attenuation': ['dB'] ,
        'Loss': ['dB'],
        'Mean Spherical Candle Power': ['MSCP'],
        'Minimum Isolation Voltage' : ['db'] , 
          'Current': ['A'], 'Voltage': ['V'], 'Weight': ['g','lb', 'oz'], 'Frequency': ['Hz'],
        'Resistance': ['Ohm'], 'Power': ['W','dB','VA','HP'], 'Capacitance': ['F'], 'Impedance': ['Ohm'],
        'Gain': ['dB'], 'Thermal': ['c', 'k', '°'], 'Temperature': ['c', 'k', '°'],
        'Tolerance': ['%','ppm','ppb'], 'Ratio': ['%'], 'Efficiency': ['%'], 'Aging': ['Year','ppm'],
        'Noise': ['db','ppm'], 'Stability': ['ppm'], 'Sensitivity': ['db'], 'Gain Bandwidth': ['Hz'],
        'Breaking Capacity': ['A'], 'Gain Attenuation': ['dB'], 'Loss': ['dB'], 'Mean Spherical Candle Power': ['MSCP'],
        'Minimum Isolation Voltage' : ['db'] ,
        'time' : ['s','min','h','ns','d','month','year',''],
        'color': [''],
        'depth': ['m','cm','mm','in','ft','mile'],
        'height' : ['m','cm','mm','in','ft','mile'],
        'length' : ['m','cm','mm','in','ft','mile'],
        'size' : ['m','cm','mm','in','gallon','AWG','b','B','bit','byte','oz','word','pixel','cc','ounce'],
        'Rate' : [    'bps', 'sps', 'N/mm', 'Hz', 'V/us', 'SCFM|GPH', 'r/min', 'bE', 'lbs/in', 'N.mm/deg', 'WPS', 'L/min', 'Bd', 'fps', 'Gbps', 'lb/in', 'L/sec', 'm³/h', 'gpm', 'slm', 'slpm', 
        'sccm', 'g', 'SPS', 'm/s', 'ft/min', 'scfh', 'Grms', 'ft²/min', 
        'Gs', 's', '', 'Tps', 'baud', 'CFM', 'rpm'] ,
        'Material': ['','  '],
        'Diameter' : ['m','cm','mm','in','ft','mile'],
        'speed' : ['m/s','km/h','mph','hz','kph','rpm','pbs','rps','cm/s','ft/s','G','Sec','bps'],
        'width' : ['m','cm','mm','in','ft','mile','°','pbs','hz'],
        'dimension' : ['m'],
        'thickness' : ['m','in'],
        'mounting' : ['m','in',''],
        'Coefficient' : ['%'],
        'noise': ['dB','db','ppm','%'],
        'gender': [''],
        'Supported Device' :['','  '],
        'area' : ['m2','cm2','mm2','inch2','ft2','acre'],
        'volume' : ['m3','cm3','mm3','inch3','ft3','liter'],
        'pressure' : ['Pa','kPa','MPa','bar','psi'],
        'energy' : ['J','kJ','cal','Wh','kWh'],
        'power' : ['W','kW','MW'],
        'torque' : ['Nm','lb-ft','kg-m'],
        'force' : ['N','kN','lb','kg'],
        'acceleration' : ['m/s2','g'],
        'density' : ['kg/m3','g/cm3','lb/in3'] ,
        'type': ['','°','bit',' '],
        'Bandwidth' : ['Hz','bps'],
        'number' : ['','Turns','key','byte','b',' ']
    }
    
    # Function to validate units
    def is_valid_unit(unit, fet_name):
        if pd.isna(unit):
            return False
        unit_parts = str(unit).lower().split('|')
        unit_valid = False
        for part in unit_parts:
            part = part.strip()
            for key, units in valid_units.items():
                if key.lower() in str(fet_name).lower():
                    if any(valid_unit.lower() in part for valid_unit in units):
                        unit_valid = True
                        break
        return unit_valid
    
    # Initialize validation columns
    uploaded_cleaned['ANOMALY'] = False
    uploaded_cleaned['ANOMALY_REASON'] = ''
    uploaded_cleaned['VALIDATION_STATUS'] = 'Valid'
    
    # Validate units
    invalid_unit_mask = ~uploaded_cleaned.apply(lambda row: is_valid_unit(row['UNIT'], row['FET_NAME']), axis=1)
    uploaded_cleaned.loc[invalid_unit_mask, 'ANOMALY'] = True
    uploaded_cleaned.loc[invalid_unit_mask, 'ANOMALY_REASON'] += 'Invalid unit for measurement; '
    uploaded_cleaned.loc[invalid_unit_mask, 'VALIDATION_STATUS'] = 'Invalid'
    
    # Validate against database groups
    db_cleaned = db_data.dropna().copy()
    db_cleaned['GROUP'] = db_cleaned['PL_NAME'].astype(str) + '_' + db_cleaned['FET_NAME'].astype(str)
    db_cleaned['VALUE_NUMERIC'] = pd.to_numeric(db_cleaned['VALUE'], errors='coerce')
    
    # For each uploaded record, check if it's an outlier compared to database
    for idx, row in uploaded_cleaned.iterrows():
        group = row['GROUP']
        db_group_data = db_cleaned[db_cleaned['GROUP'] == group]
        
        if len(db_group_data) > 0:
            db_values = db_group_data['VALUE_NUMERIC'].dropna()
            
            if len(db_values) > 0 and pd.notna(row['VALUE_NUMERIC']):
                # Calculate statistics from database
                db_mean = db_values.mean()
                db_std = db_values.std()
                
                # Check if uploaded value is an outlier (beyond 3 standard deviations)
                if abs(row['VALUE_NUMERIC'] - db_mean) > 3 * db_std:
                    uploaded_cleaned.loc[idx, 'ANOMALY'] = True
                    uploaded_cleaned.loc[idx, 'ANOMALY_REASON'] += 'Outlier compared to database; '
                    uploaded_cleaned.loc[idx, 'VALIDATION_STATUS'] = 'Outlier'
                
                # Add database statistics
                uploaded_cleaned.loc[idx, 'DB_MEAN'] = db_mean
                uploaded_cleaned.loc[idx, 'DB_STD'] = db_std
                uploaded_cleaned.loc[idx, 'DB_COUNT'] = len(db_values)
            else:
                uploaded_cleaned.loc[idx, 'DB_MEAN'] = None
                uploaded_cleaned.loc[idx, 'DB_STD'] = None
                uploaded_cleaned.loc[idx, 'DB_COUNT'] = 0
        else:
            uploaded_cleaned.loc[idx, 'ANOMALY'] = True
            uploaded_cleaned.loc[idx, 'ANOMALY_REASON'] += 'Group not found in database; '
            uploaded_cleaned.loc[idx, 'VALIDATION_STATUS'] = 'Not Found'
            uploaded_cleaned.loc[idx, 'DB_MEAN'] = None
            uploaded_cleaned.loc[idx, 'DB_STD'] = None
            uploaded_cleaned.loc[idx, 'DB_COUNT'] = 0
    
    # Clean up anomaly reason column
    uploaded_cleaned['ANOMALY_REASON'] = uploaded_cleaned['ANOMALY_REASON'].str.rstrip('; ').replace('', 'No issues found')
    
    st.success(f"🎯 Validation completed! Found {uploaded_cleaned['ANOMALY'].sum()} issues in uploaded data.")
    
    return uploaded_cleaned

# Streamlit App
def main():
    st.set_page_config(
        page_title="Parametric Anomaly QA Tool",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for blue theme
    st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .stButton > button {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0052a3;
    }
    .stDownloadButton > button {
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stDownloadButton > button:hover {
        background-color: #218838;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🔍 Parametric Anomaly QA Tool")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("📋 Tool Information")
    st.sidebar.markdown("""
    This tool performs comprehensive anomaly detection on parametric data using:
    
    - **Isolation Forest** for numeric outliers
    - **Unit validation** based on measurement types
    - **PL group analysis** for consistency checks
    - **Controlled anomaly filtering** (±50 range)
    - **Database comparison** for uploaded values
    
    Choose your analysis method below.
    """)
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🚀 Analysis Options")
  
        
        # --- New Section: Validate New Values ---
        st.markdown("#### 🆕 Validate New Values")
        st.markdown(
            "Upload an Excel file to validate new values against the database. "
            "**Required columns:** `PL_NAME`, `FET_NAME`, `VALUE`, `UNIT`"
        )

        new_values_file = st.file_uploader(
            "Choose an Excel file for new values",
            type=['xlsx', 'xls'],
            key="new_values_file",
            help="Upload Excel file with columns: PL_NAME, FET_NAME, VALUE, UNIT"
        )

        if new_values_file is not None:
            if st.button("🆕 Validate New Values", type="primary", key="validate_new_values", use_container_width=True):
                with st.spinner("🔄 Validating new values against database..."):
                    validation_results = validate_uploaded_values(new_values_file)
                    
                    if validation_results is not None and len(validation_results) > 0:
                        st.markdown("### 📊 Validation Results for New Values")
                        st.dataframe(validation_results.head(10), use_container_width=True)
                        
                        # Download button for results
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"New_Values_Validation_{timestamp}.xlsx"
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            validation_results.to_excel(writer, index=False, sheet_name='Validation_Results')
                        excel_data = output.getvalue()
                        st.download_button(
                            label="📥 Download New Values Validation Report (Excel)",
                            data=excel_data,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ No results to display or validation failed.")
        
        st.markdown("---")
        
        # Run Entire Database Button
        st.markdown("#### 🗄️ Run Entire Database Analysis")
        st.markdown("Analyze the complete database for anomalies.")
        
        if st.button("🔧 Run Entire Database", type="primary", use_container_width=True):
            with st.spinner("🔄 Running anomaly detection... This may take a few minutes."):
                # Run the anomaly detection
                anomalies_df = run_anomaly_detection()
                
                if anomalies_df is not None and len(anomalies_df) > 0:
                    # Display summary statistics
                    st.markdown("### 📊 Analysis Results")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Total Anomalies", len(anomalies_df))
                    with col_b:
                        st.metric("Unique PL Names", anomalies_df['PL_NAME'].nunique())
                    with col_c:
                        st.metric("Unique FET Names", anomalies_df['FET_NAME'].nunique())
                    
                    # Show sample of anomalies
                    st.markdown("### 📋 Sample Anomalies")
                    st.dataframe(anomalies_df.head(10), use_container_width=True)
                    
                    # Create download button
                    st.markdown("### 💾 Download Results")
                    
                    # Generate timestamp for filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"Anomalies_Parametrics_{timestamp}.xlsx"
                    
                    # Convert DataFrame to Excel bytes
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        anomalies_df.to_excel(writer, index=False, sheet_name='Anomalies')
                    
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="📥 Download Anomalies Report (Excel)",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    # Also save to original path for backup
                    try:
                        output_path = r'C:\Users\145989\OneDrive - Arrow Electronics, Inc\Desktop\sql OUTPUT\1st project ML Parametric\patch2\Anomalies_Of_parametrics22_6.xlsx'
                        anomalies_df.to_excel(output_path, index=False, columns=anomalies_df.columns)
                        st.success(f"✅ Results also saved to: {output_path}")
                    except Exception as e:
                        st.warning(f"⚠️ Could not save to original path: {str(e)}")
                
                elif anomalies_df is not None:
                    st.info("ℹ️ No anomalies detected in the dataset.")
                else:
                    st.error("❌ Analysis failed. Please check the data source and try again.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by Streamlit and Scikit-learn*")

if __name__ == "__main__":
    main()
