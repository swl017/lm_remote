import socket
import threading
import argparse
import logging
import ssl
import select

def forward_data(source, destination):
    try:
        while True:
            ready_to_read, _, _ = select.select([source], [], [], 1)
            if ready_to_read:
                data = source.recv(1024)
                if not data:
                    break
                destination.sendall(data)
    except Exception as e:
        logging.error(f"Error forwarding data: {e}")
    finally:
        source.close()
        destination.close()

def handle_client(client_socket, dst_ip, dst_port, use_ssl=False):
    try:
        if use_ssl:
            context = ssl.create_default_context()
            dst_socket = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=dst_ip)
        else:
            dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        dst_socket.connect((dst_ip, dst_port))
        
        client_to_dst = threading.Thread(target=forward_data, args=(client_socket, dst_socket))
        dst_to_client = threading.Thread(target=forward_data, args=(dst_socket, client_socket))
        
        client_to_dst.start()
        dst_to_client.start()
        
        client_to_dst.join()
        dst_to_client.join()
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()
        if 'dst_socket' in locals():
            dst_socket.close()

def forward_connections(src_ip, src_port, dst_ip, dst_port, use_ssl=False):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((src_ip, src_port))
        server.listen(5)
        logging.info(f"Listening for connections on {src_ip}:{src_port}")
        
        while True:
            client_socket, addr = server.accept()
            logging.info(f"Accepted connection from {addr}")
            client_handler = threading.Thread(
                target=handle_client,
                args=(client_socket, dst_ip, dst_port, use_ssl)
            )
            client_handler.start()
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple TCP port forwarder")
    parser.add_argument("--src-ip", default="0.0.0.0", help="Source IP to listen on")
    parser.add_argument("--src-port", type=int, required=True, help="Source port to listen on")
    parser.add_argument("--dst-ip", required=True, help="Destination IP to forward to")
    parser.add_argument("--dst-port", type=int, required=True, help="Destination port to forward to")
    parser.add_argument("--use-ssl", action="store_true", help="Use SSL for outgoing connections")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    forward_connections(args.src_ip, args.src_port, args.dst_ip, args.dst_port, args.use_ssl)