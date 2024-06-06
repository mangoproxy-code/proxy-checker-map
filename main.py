import csv
import folium
from tkinter import Tk, Label, Entry, Button, StringVar, IntVar, Text, END, filedialog, ttk
from threading import Thread, Event
import webbrowser
from aiohttp_socks import ProxyConnector
import aiohttp
import asyncio
import os

class IPCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Checker Tool")
        self.root.resizable(False, False)

        self.stop_event = Event()

        self.proxy_label = Label(root, text="Proxy (user:password@host:port)")
        self.proxy_label.grid(row=0, column=0)
        self.proxy_entry = Entry(root, textvariable=StringVar())
        self.proxy_entry.grid(row=0, column=1)

        self.ips_label = Label(root, text="Number of IPs to Check")
        self.ips_label.grid(row=1, column=0)
        self.ips_entry = Entry(root, textvariable=IntVar())
        self.ips_entry.grid(row=1, column=1)

        self.mango_button = Button(root, text="Get Proxy from MangoProxy", command=self.open_mango_proxy)
        self.mango_button.grid(row=2, column=1)

        self.start_button = Button(root, text="Start", command=self.start)
        self.start_button.grid(row=3, column=1)

        self.stop_button = Button(root, text="Stop and Save", command=self.stop, state='disabled')
        self.stop_button.grid(row=4, column=1)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=5, column=1)

        self.log_label = Label(root, text="Log")
        self.log_label.grid(row=6, column=0)
        self.log_text = Text(root, height=10, width=50)
        self.log_text.grid(row=7, column=0, columnspan=3)

        self.open_map_button = Button(root, text="Open Map", command=self.open_map, state='disabled')
        self.open_map_button.grid(row=8, column=0)

        self.open_csv_button = Button(root, text="Open CSV", command=self.open_csv, state='disabled')
        self.open_csv_button.grid(row=8, column=1)

    def update_log(self, message):
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)

    def open_mango_proxy(self):
        webbrowser.open("https://dashboard.mangoproxy.com/signup?ref=soft")

    def start(self):
        self.stop_event.clear()
        self.stop_button.config(state='normal')
        self.start_button.config(state='disabled')
        self.open_map_button.config(state='disabled')
        self.open_csv_button.config(state='disabled')

        proxy_config = self.proxy_entry.get()
        num_ips = int(self.ips_entry.get())

        self.progress["maximum"] = num_ips
        self.progress["value"] = 0

        Thread(target=self.check_ips, args=(proxy_config, num_ips)).start()

    def stop(self):
        self.stop_event.set()
        self.update_log("Stopping IP checks...")

    def check_ips(self, proxy_config, num_ips):
        proxy_url = self.parse_proxy_config(proxy_config)
        if not proxy_url:
            self.update_log("Invalid proxy configuration format. Please use user:password@host:port")
            return

        results = asyncio.run(self.fetch_ip_info(proxy_url, num_ips))
        if results:
            self.save_to_csv(results)
            self.generate_map(results)
            self.open_map_button.config(state='normal')
            self.open_csv_button.config(state='normal')

        self.stop_button.config(state='disabled')
        self.start_button.config(state='normal')

    def parse_proxy_config(self, proxy_config):
        try:
            username_password, host_port = proxy_config.split('@')
            username, password = username_password.split(':')
            host, port = host_port.split(':')
            proxy_url = f"socks5://{username}:{password}@{host}:{port}"
            return proxy_url
        except ValueError:
            return None

    async def fetch_ip_info(self, proxy_url, num_ips):
        connector = ProxyConnector.from_url(proxy_url)
        semaphore = asyncio.Semaphore(10)  # Limit concurrent connections
        results = []

        async def fetch(session, i):
            if self.stop_event.is_set():
                return None

            url = "http://ip-api.com/json"
            try:
                async with semaphore:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.update_log(f"IP {data['query']} - {data['city']}, {data['country']}")
                            self.progress["value"] = i + 1
                            self.root.update_idletasks()
                            return data
                        else:
                            self.update_log(f"Failed to get IP info: HTTP {response.status}")
            except Exception as e:
                self.update_log(f"Failed to get IP info: {e}")
            return None

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [fetch(session, i) for i in range(num_ips)]
            results = await asyncio.gather(*tasks)

        return [result for result in results if result]

    def save_to_csv(self, results):
        keys = results[0].keys()
        with open('ip_results.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        self.update_log("CSV saved to ip_results.csv")

    def generate_map(self, results):
        map_center = [results[0]['lat'], results[0]['lon']]
        my_map = folium.Map(location=map_center, zoom_start=2)

        for result in results:
            folium.Marker(
                location=[result['lat'], result['lon']],
                popup=f"{result['city']}, {result['country']} - {result['query']}",
            ).add_to(my_map)

        my_map.save("map.html")
        self.update_log("Map saved to map.html")

    def open_map(self):
        webbrowser.open("map.html")

    def open_csv(self):
        os.startfile("ip_results.csv")

# Main function
if __name__ == '__main__':
    root = Tk()
    app = IPCheckerApp(root)
    root.mainloop()
