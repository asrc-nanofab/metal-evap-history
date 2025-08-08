from openai import OpenAI
import base64
import os
import glob
import time
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_unique_user_names(file_path="data/2025_07_31_badger_metal_evap_data.txt"):
    """
    Read the users file and return a unique list of 'first name last name' combinations.

    Args:
        file_path (str): Path to the tab-delimited users file

    Returns:
        list: Unique list of user names in 'first name last name' format
    """
    try:
        # Read the tab-delimited file
        df = pd.read_csv(file_path, delimiter="\t")

        # Extract first name and last name columns (assuming columns 5 and 4 based on file structure)
        # Columns: equipment, date, role, active, last name, first name, member
        first_names = df["first name"].astype(str)
        last_names = df["last name"].astype(str)

        # Combine first and last names
        full_names = first_names + " " + last_names

        # Remove duplicates and sort
        unique_names = sorted(list(set(full_names)))

        # Remove any empty or invalid entries
        unique_names = [
            name for name in unique_names if name.strip() and name != "nan nan"
        ]

        print(f"✓ Loaded {len(unique_names)} unique user names from {file_path}")
        return unique_names

    except Exception as e:
        print(f"✗ Error reading user names file: {str(e)}")
        print("Continuing without user name validation...")
        return []


# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_extraction_prompt(user_names_list):
    """Create the extraction prompt with the list of valid user names."""

    # Format the user names list for the prompt
    if user_names_list:
        names_text = "\n".join([f"- {name}" for name in user_names_list])
        user_validation_text = f"""
VALID USER NAMES:
The following is a complete list of valid user names. When extracting the User Name from the handwritten spreadsheet, match the handwritten name as closely as possible to one of these names:

{names_text}

USER NAME MATCHING RULES:
- Match handwritten user names to the closest name from the valid list above
- Account for handwriting variations, abbreviations, or partial names
- If you find a close match, use the exact name from the valid list
- If no reasonable match can be found, use "UNKNOWN_USER" instead of guessing
- Common variations to consider: initials, nicknames, last name only, first name only
"""
    else:
        user_validation_text = """
USER NAME EXTRACTION:
- Extract user names exactly as written in the handwritten spreadsheet
- Account for handwriting variations, abbreviations, or partial names
- If any user name is unclear or illegible, use "UNCLEAR" as the value
"""

    prompt = f"""Please extract all data from this handwritten spreadsheet image and convert it to CSV format. The spreadsheet contains the following columns in order:

1. Date
2. User name  
3. Materials (abbreviations of metals and oxides)
4. Threshold power (percent)
5. Power deposition (percent) 
6. Rate (percent)
7. Thickness (percent)
8. Crystal monitor (percent)
{user_validation_text}
Please follow these extraction and validation rules:
- Extract each row of data carefully
- Maintain the exact column order listed above
- Include a header row with column names
- If any cell is unclear or illegible, use "UNCLEAR" as the value
- Blank cells should be left empty (just use commas with no value between them)

DATE FORMATTING RULES:
- Always return dates in MM/DD/YYYY format (month/day/4-digit-year)
- If the handwritten date includes a 4-digit year, use it as written
- If the handwritten date only shows month/day (like "3/15" or "03/15"), extrapolate the year:
  * Look at other dates in the same spreadsheet for context
  * All entries in a single spreadsheet typically occur within the same week/year
  * Use the most logical year based on the context of other complete dates in the sheet
  * If no other dates have years visible, use reasonable assumptions based on the data context
- Examples: "3/15" might become "03/15/2024" if other dates suggest 2024
- If date format is unclear, use "UNCLEAR" for that entry

IMPORTANT FORMATTING RULES:
- For Thickness column: Extract only the numeric value, remove "nm" or any other units
- For Rate column: Extract only the numeric value, remove any units
  * If rate includes "A/S" or "Å/S" (angstroms per second), extract only the number
- For percentage columns (Threshold Power, Power Deposition, Rate, Crystal Monitor): 
  * Extract only the numeric value, remove "%" symbols
  * Valid values must be between 0 and 100
  * If a percentage value is outside 0-100 range, use "INVALID_RANGE" instead
- Remove all unit symbols (%, nm, A/S, Å/S, etc.) from the final output

Quality control:
- Double-check that percentage values are reasonable (0-100)
- Double-check that the Threshold Power value is less than the Power Deposition value for each row
- Ensure all dates follow MM/DD/YYYY format with consistent year extrapolation
- Flag any suspicious or out-of-range values
- Output only the CSV data, no additional text

CSV Header: Date,User Name,Materials,Threshold Power,Power Deposition,Rate,Thickness,Crystal Monitor"""

    return prompt


def encode_image(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_image_to_csv(image_path, page_number, output_dir, extraction_prompt):
    """Process a single image and return CSV data"""
    print(f"Processing page {page_number}: {os.path.basename(image_path)}...")

    try:
        # Encode the image
        base64_image = encode_image(image_path)

        # Make API call
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": extraction_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=8192,
            temperature=0,
        )

        # Extract the CSV content
        csv_content = response.choices[0].message.content.strip()

        # Save individual page CSV
        output_filename = os.path.join(output_dir, f"page_{page_number}_output.csv")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(csv_content)

        print(f"✓ Saved: {output_filename}")
        return csv_content, True

    except Exception as e:
        print(f"✗ Error processing {image_path}: {str(e)}")
        return None, False


def main():
    # Load user names first
    print("Loading user names for validation...")
    user_names = get_unique_user_names()

    # Create extraction prompt with user names
    extraction_prompt = create_extraction_prompt(user_names)

    folder_name = "2025_06_Metal_Evap_Data"
    # Configure your paths here
    image_folder = (
        f"data/images/{folder_name}"  # Change this to your actual folder path
    )
    output_dir = f"data/output_csvs/{folder_name}"  # Output directory for all CSV files

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Supported image formats
    image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]

    # Find all images
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(image_folder, ext)))

    # Sort files to ensure consistent processing order
    image_files.sort()

    if not image_files:
        print(f"No images found in folder: {image_folder}")
        print(
            "Make sure your images are in the correct folder and have supported extensions (.jpg, .png, .jpeg)"
        )
        return

    print(f"Found {len(image_files)} images to process:")
    for i, file in enumerate(image_files, 1):
        print(f"  {i}. {os.path.basename(file)}")

    print("\nStarting processing...\n")

    # Process each image
    all_csv_data = []
    successful_pages = []

    for i, image_path in enumerate(image_files, 1):
        csv_data, success = process_image_to_csv(
            image_path, i, output_dir, extraction_prompt
        )

        if success and csv_data:
            all_csv_data.append(csv_data)
            successful_pages.append(i)

        # Small delay to be respectful to API rate limits
        if i < len(image_files):
            time.sleep(1)

    # Combine all successful extractions into one master CSV
    if all_csv_data:
        print(f"\n✓ Successfully processed {len(successful_pages)} pages")

        # Combine CSVs (skip headers after the first one)
        combined_csv = all_csv_data[0]  # First page with header

        for csv_data in all_csv_data[1:]:
            # Skip the header line for subsequent pages
            lines = csv_data.split("\n")
            if len(lines) > 1:
                combined_csv += "\n" + "\n".join(lines[1:])

        # Save combined result to the same output directory
        combined_filename = os.path.join(output_dir, "combined_all_pages.csv")
        with open(combined_filename, "w", encoding="utf-8") as f:
            f.write(combined_csv)

        print(f"✓ Saved combined file: {combined_filename}")
        print(
            f"✓ Individual page files: {os.path.join(output_dir, 'page_1_output.csv')} through {os.path.join(output_dir, f'page_{len(successful_pages)}_output.csv')}"
        )
    else:
        print("✗ No pages were successfully processed")


if __name__ == "__main__":
    main()
