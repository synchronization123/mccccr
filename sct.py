import pandas as pd
import requests
from datetime import datetime

# Set the API URL and token
api_url = 'https://demo.defectdojo.org/api/v2/engagements/'
api_token = 'Token 548afd6fab3bea9794a41b31da0e9404f733e222'
headers = {'Content-Type': 'application/json', 'Authorization': api_token}

# Fetch product ID and lead ID from their respective API endpoints
def fetch_product_and_lead_ids():
    try:
        product_url = 'https://demo.defectdojo.org/api/v2/products/'
        lead_url = 'https://demo.defectdojo.org/api/v2/users/'

        product_response = requests.get(product_url, headers=headers)
        lead_response = requests.get(lead_url, headers=headers)

        # Check if requests are successful
        if product_response.status_code == 200 and lead_response.status_code == 200:
            product_data = product_response.json()
            lead_data = lead_response.json()

            return product_data, lead_data
        else:
            print("Failed to fetch product or lead data")
            return None, None
    except Exception as e:
        print(f"Error fetching product and lead data: {e}")
        return None, None

# Function to create engagements from the Excel file
def create_engagements_from_excel(excel_file):
    try:
        # Load the Excel file
        df = pd.read_excel(excel_file)

        # Ensure the column names are correct
        print("Columns in the Excel file:", df.columns.tolist())

        # Fetch product and lead data from the API
        product_data, lead_data = fetch_product_and_lead_ids()
        if product_data is None or lead_data is None:
            return

        # Prepare a list to store updated rows with engagement URLs
        engagements = []

        # Loop through the rows and prepare data
        for index, row in df.iterrows():
            title = row.get('title')
            lead_id = row.get('lead')
            product_id = row.get('product')
            tags = row.get('tags').split(',')  # Split tags into a list
            target_start = row.get('target_start')
            target_end = row.get('target_end')

            # Convert dates to the proper format (YYYY-MM-DD)
            try:
                # Check if the value is a Timestamp or string
                if isinstance(target_start, pd.Timestamp):
                    target_start = target_start.strftime('%Y-%m-%d')
                else:
                    target_start = datetime.strptime(str(target_start), '%Y-%m-%d').strftime('%Y-%m-%d')

                if isinstance(target_end, pd.Timestamp):
                    target_end = target_end.strftime('%Y-%m-%d')
                else:
                    target_end = datetime.strptime(str(target_end), '%Y-%m-%d').strftime('%Y-%m-%d')
            except Exception as e:
                print(f"Error parsing dates: {e}")
                target_start = target_end = None

            # Prepare the JSON data to be sent
            payload = {
                "name": title,
                "lead": lead_id,  # Assuming lead ID is available
                "product": product_id,  # Assuming product ID is available
                "tags": tags,  # Tags should be a list
                "target_start": target_start,
                "target_end": target_end
            }

            # Send the POST request to the API to create the engagement
            response = requests.post(api_url, headers=headers, json=payload)

            # Check if the request was successful
            if response.status_code == 201:
                engagement_id = response.json().get('id')  # Get the engagement ID
                engagement_url = f"https://demo.defectdojo.org/engagement/{engagement_id}"  # Construct the URL
                print(f"Successfully created engagement: {title}, Engagement URL: {engagement_url}")
                # Append the engagement URL to the data
                row['engagement_id_url'] = engagement_url
            else:
                print(f"Failed to create engagement {title}. Status code: {response.status_code}")
                print(response.text)
                row['engagement_id_url'] = 'Failed to create'

            # Append the row with the engagement URL to the list
            engagements.append(row)

        # Create a DataFrame from the updated engagements list
        engagements_df = pd.DataFrame(engagements)

        # Save the engagements data to a new Excel file (engagementlogs.xlsx)
        engagements_df.to_excel('engagementlogs.xlsx', index=False)
        print("Engagements have been logged in engagementlogs.xlsx")

        # Clear the DataFrame for better performance
        del engagements_df  # Explicitly delete the DataFrame to free up memory
        print("DataFrame cleared.")

    except Exception as e:
        print(f"Error reading the Excel file or sending data: {e}")

# Provide the Excel file path
excel_file = 'datatask.xlsx'  # Adjust this as needed

# Create engagements from the Excel file
create_engagements_from_excel(excel_file)
