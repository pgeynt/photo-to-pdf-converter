This project is a Python application that allows you to convert multiple photos into a single PDF file in a sequential order. The user-friendly interface is built using Tkinter for ease of use. The application automatically resizes images to fit the A4 page size and generates the PDF file.
Features

    Photo Uploading: Supports JPEG and PNG image formats.
    Automatic Sorting: Photos are automatically sorted based on numerical values in file names (e.g., image_10.jpg comes before image_2.jpg).
    Progress Tracking: A progress bar displays the current status during PDF creation.
    PDF Export: Save the generated PDF to a custom location.
    Error Handling: Provides informative error messages in case of issues.

How It Works

    Load Photos:
        Click "Load Photos" to select image files. The application sorts the images numerically based on their file names.

    Process Photos:
        After loading, click "Process" to begin converting the images into a PDF. The images are resized proportionally to fit the A4 page size.

    Save PDF:
        Once the process is complete, click "Save PDF" to choose a location and name for the output file.

Installation

    Clone the repository:

git clone https://github.com/your-username/photo-to-pdf-converter.git
cd photo-to-pdf-converter

Install the required dependencies:

pip install -r requirements.txt

Run the application:

python main.py
