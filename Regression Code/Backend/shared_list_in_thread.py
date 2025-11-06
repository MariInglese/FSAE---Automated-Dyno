import threading
import time

class SharedListProcessor:
    def __init__(self):
        self.shared_list = []  # Shared list used by multiple threads
        self.lock = threading.Lock()  # Lock for thread safety
        self.running = True  # Control variable for the threads

    def add_to_list_continuously(self):
        """Thread function to continuously add items to the list."""
        item_id = 1
        while self.running:
            with self.lock:  # Acquire the lock before modifying the list
                self.shared_list.append(f"Item{item_id}")
                print(f"Added Item{item_id}")
            item_id += 1
            time.sleep(1)  # Add items at intervals

    def process_list_continuously(self):
        """Thread function to continuously process (remove) items from the list."""
        while self.running:
            with self.lock:  # Acquire the lock before accessing/modifying the list
                if self.shared_list:
                    # item = self.shared_list.pop(0)  # Process (pop) the first item
                    # print(f"Processed {item}")
                    for item in self.shared_list:
                        print(item)
            time.sleep(0.5)  # Process items at a different interval

    def stop(self):
        """Stop the threads by setting the running flag to False."""
        self.running = False

# Example usage
if __name__ == "__main__":
    processor = SharedListProcessor()

    # Start the threads for adding and processing items
    add_thread = threading.Thread(target=processor.add_to_list_continuously)
    process_thread = threading.Thread(target=processor.process_list_continuously)
    add_thread.start()
    process_thread.start()

    # Let the threads run for a while
    time.sleep(5)

    # Stop the threads
    processor.stop()
    add_thread.join()
    process_thread.join()
    print("Stopped all threads.")
