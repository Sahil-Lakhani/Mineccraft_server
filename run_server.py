import subprocess
import time
import signal
import sys
import re
import threading

# Server configuration
server_jar = "minecraft_server.1.21.4.jar"
memory = "12G"
minecraft_port = "25565"

# Function to start Minecraft server with error capture
def start_minecraft_server():
    print("Starting Minecraft server...")
    process = subprocess.Popen(
        ["java", f"-Xmx{memory}", f"-Xms{memory}", "-jar", server_jar, "nogui"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("Minecraft server process started!")
    
    # Start threads to monitor both stdout and stderr
    def monitor_output(stream, prefix):
        for line in stream:
            print(f"[{prefix}] {line.strip()}")
    
    stdout_thread = threading.Thread(target=monitor_output, args=(process.stdout, "SERVER"))
    stderr_thread = threading.Thread(target=monitor_output, args=(process.stderr, "SERVER ERROR"))
    
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait a bit to see if server crashes immediately
    time.sleep(3)
    if process.poll() is not None:
        print(f"WARNING: Server exited immediately with code {process.returncode}")
        # Try to capture any stderr that was generated
        error_output = process.stderr.read()
        if error_output:
            print(f"Server error output: {error_output}")
    else:
        print("Server initialization appears successful")
    
    return process

# Function to start ngrok
def start_ngrok():
    print("Starting ngrok tunnel...")
    process = subprocess.Popen(
        ["ngrok", "tcp", minecraft_port],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("ngrok started!")
    return process

# Function to get ngrok URL using the web API
def get_ngrok_url():
    # Wait a bit for ngrok to initialize
    time.sleep(3)
    
    max_attempts = 10
    attempts = 0
    
    while attempts < max_attempts:
        try:
            # Use curl to query the ngrok API
            result = subprocess.run(
                ["curl", "http://127.0.0.1:4040/api/tunnels"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the JSON output
            import json
            data = json.loads(result.stdout)
            
            # Look for TCP tunnels
            for tunnel in data.get('tunnels', []):
                public_url = tunnel.get('public_url', '')
                if 'tcp://' in public_url:
                    # Extract host and port from tcp://host:port
                    match = re.search(r'tcp://([^:]+):(\d+)', public_url)
                    if match:
                        host, port = match.groups()
                        return host, port
            
            # No tunnel found yet, wait and retry
            attempts += 1
            time.sleep(2)
            
        except Exception as e:
            print(f"Attempt {attempts}: Failed to get ngrok URL: {e}")
            attempts += 1
            time.sleep(2)
    
    print("\nERROR: Could not get ngrok URL after multiple attempts.")
    print("Please check if ngrok is running properly by visiting http://127.0.0.1:4040 in your browser")
    return None, None

# Function to stop everything gracefully
def stop_services(server_process, ngrok_process):
    print("\nStopping Minecraft server...")
    
    # Send 'stop' command to Minecraft server if it's still running
    if server_process.poll() is None:
        try:
            server_process.stdin.write("stop\n")
            server_process.stdin.flush()
        except:
            print("Failed to send 'stop' command, forcing termination")
            server_process.terminate()
    
    # Wait for server to stop gracefully (if it was running)
    if server_process.poll() is None:
        timeout = 30
        for i in range(timeout):
            if server_process.poll() is not None:
                break
            time.sleep(1)
        
        # Force kill if it didn't stop
        if server_process.poll() is None:
            print("Forcing server shutdown...")
            server_process.terminate()
    
    # Stop ngrok
    print("Stopping ngrok...")
    ngrok_process.terminate()
    
    print("All services stopped successfully.")

# Signal handler for graceful shutdown
def signal_handler(sig, frame, server_process, ngrok_process):
    stop_services(server_process, ngrok_process)
    sys.exit(0)

# Main function
def main():
    # Start Minecraft server
    server_process = start_minecraft_server()
    
    # Start ngrok only if the server is still running
    if server_process.poll() is None:
        ngrok_process = start_ngrok()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, server_process, ngrok_process))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, server_process, ngrok_process))
        
        # Get and display the ngrok URL
        host, port = get_ngrok_url()
        
        if host and port:
            print("\n===== MINECRAFT SERVER READY =====")
            print(f"Server Address: {host}")
            print(f"Port: {port}")
            print(f"Java Edition Direct Connect: {host}:{port}")
            print("Share this address with your friends to connect!")
            print("=====================================\n")
        
        # Keep the script running and monitor processes
        try:
            while True:
                # Check if processes are still running
                if server_process.poll() is not None:
                    print(f"Minecraft server has stopped unexpectedly! (Exit code: {server_process.returncode})")
                    # Try to get any remaining error output
                    error_output = server_process.stderr.read()
                    if error_output:
                        print(f"Final server error output: {error_output}")
                    ngrok_process.terminate()
                    sys.exit(1)
                    
                if ngrok_process.poll() is not None:
                    print("ngrok has stopped unexpectedly!")
                    stop_services(server_process, ngrok_process)
                    sys.exit(1)
                    
                time.sleep(1)
        except KeyboardInterrupt:
            stop_services(server_process, ngrok_process)
    else:
        print("Cannot start ngrok because the Minecraft server failed to start properly.")
        print("Please check the server error messages above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()