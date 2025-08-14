# LinkedIn_Scrapper

A Python-based LinkedIn job scraper that automates the process of collecting job postings from LinkedIn. This project is designed to help users gather job data efficiently for analysis or job search automation.

## Features
- Scrapes job postings from LinkedIn based on keywords and location
- Saves results to CSV or JSON
- Supports Google Drive integration for saving results
- Easy configuration with JSON credentials

## Getting Started

### Prerequisites
- Python 3.7+
- Google API credentials (for Drive integration)
- LinkedIn account (for scraping)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/AmitMandhana/LinkedIn_Scrapper.git
   cd LinkedIn_Scrapper
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Usage
1. Configure your credentials in `google_credentials.json` and `google_drive.json`.
2. Run the scraper:
   ```sh
   python job_scrapper.py
   ```

## License
This project is licensed under the MIT License.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact
For any questions, please open an issue on GitHub.
