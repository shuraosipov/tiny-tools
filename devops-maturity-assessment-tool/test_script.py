import os
import requests

# List of PDF URLs to download
pdf_urls = [
    'https://docs.tibco.com/pub/spotfire_server/14.4.1/SPOT_sfire_server_14.4.1_installation.pdf?id=0',
    'https://docs.tibco.com/pub/spotfire_server/14.4.1/SPOT_sfire_server_14.4.1_relnotes.pdf?id=0',
    # Add more URLs as needed
]

# Directory to save downloaded PDFs
download_dir = 'spotfire_server_14_4_1_pdfs'
os.makedirs(download_dir, exist_ok=True)

def download_pdf(url, directory):
    """Download a PDF file from the given URL to the specified directory."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    # Extract the filename from the URL
    filename = os.path.join(directory, url.split('/')[-1].split('?')[0])
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f'Downloaded: {filename}')

if __name__ == '__main__':
    for pdf_url in pdf_urls:
        download_pdf(pdf_url, download_dir)
