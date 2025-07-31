from openai import OpenAI
import base64
import os
import glob
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your extraction prompt
EXTRACTION_PROMPT = """Please extract all data from this handwritten spreadsheet image and convert it to CSV format. The spreadsheet contains the following columns in order:

1. Date
2. User name  
3. Materials (abbreviations of metals and oxides)
4. Threshold power (percent)
5. Power deposition (percent) 
6. Rate (percent)
7. Thickness (percent)
8. Crystal monitor (percent)

Please follow these extraction and validation rules:
- Extract each row of data carefully
- Maintain the exact column order listed above
- Use standard date formats (MM/DD/YYYY or similar)
- Include a header row with column names
- If any cell is unclear or illegible, use "UNCLEAR" as the value
- Blank cells should be left empty (just use commas with no value between them)

IMPORTANT FORMATTING RULES:
- For Thickness column: Extract only the numeric value, remove "nm" or any other units
- For percentage columns (Threshold Power, Power Deposition, Rate, Crystal Monitor): 
  * Extract only the numeric value, remove "%" symbols
  * Valid values must be between 0 and 100
  * If a percentage value is outside 0-100 range, use "INVALID_RANGE" instead
- Remove all unit symbols (%, nm, etc.) from the final output

Quality control:
- Double-check that percentage values are reasonable (0-100)
- Flag any suspicious or out-of-range values
- Output only the CSV data, no additional text

CSV Header: Date,User Name,Materials,Threshold Power,Power Deposition,Rate,Thickness,Crystal Monitor"""


def encode_image(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_image_to_csv(image_path, page_number, output_dir):
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
                        {"type": "text", "text": EXTRACTION_PROMPT},
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
    # Configure your paths here
    image_folder = "data/images"  # Change this to your actual folder path
    output_dir = "data/output_csvs"  # Output directory for all CSV files

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
        csv_data, success = process_image_to_csv(image_path, i, output_dir)

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
