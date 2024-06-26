# Proxy Checker Map

This project is a Python-based GUI application that checks multiple IP addresses using a specified proxy, gathers information from `ip-api`, and displays the results on an interactive map. The tool also saves the results in a CSV file.

## Features

- GUI for easy input of proxy configuration and number of IPs to check
- Supports SOCKS5 proxies
- Concurrent IP checking for faster results
- Progress bar to show the progress
- Real-time log updates
- Stop and save functionality
- Interactive map with IP locations
- CSV output of IP details

## Prerequisites

- Python 3.x
- aiohttp
- aiohttp_socks
- folium
- tkinter

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/mangoproxy-code/proxy-checker-map.git
    cd proxy-checker-map
    ```

2. Install the required Python packages:
    ```sh
    pip install aiohttp aiohttp_socks folium
    ```

## Usage

1. Run the `main.py` script:
    ```sh
    python main.py
    ```

2. Use the GUI to:
    - Input your proxy configuration in the format `user:password@host:port`.
    - Enter the number of IPs to check.
    - Click "Start" to begin the IP checking process.
    - Click "Stop and Save" to stop the process and save the results.
    - Click "Open Map" to view the interactive map.
    - Click "Open CSV" to view the CSV file with the results.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Alex Whynot
