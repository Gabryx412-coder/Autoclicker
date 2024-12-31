import threading
import keyboard
from pynput.keyboard import Controller
import time

class KeyPressThread(threading.Thread):
    """Thread separato per gestire la pressione di un singolo tasto."""
    def __init__(self, key, controller):
        super().__init__()
        self.key = key
        self.controller = controller
        self._stop_event = threading.Event()

    def run(self):
        """Esegui la pressione continua del tasto fino a quando non viene fermato."""
        while not self._stop_event.is_set():
            self.controller.press(self.key)
            time.sleep(0.1)  # Intervallo per ridurre il carico della CPU

    def stop(self):
        """Ferma il thread e rilascia il tasto."""
        self._stop_event.set()
        self.controller.release(self.key)

class AutoClicker:
    def __init__(self):
        self.controller = Controller()
        self.threads = {}
        self.keys_to_press = []
        self.is_running = False

    def choose_keys(self):
        """Funzione per scegliere i tasti da premere."""
        while True:
            try:
                num_keys = int(input("Quanti tasti vuoi tenere premuti? "))
                if num_keys < 1:
                    print("Devi selezionare almeno 1 tasto.")
                    continue
                break
            except ValueError:
                print("Per favore, inserisci un numero valido.")

        keys = []
        for i in range(num_keys):
            while True:
                key = input(f"Scegli il tasto numero {i + 1} (puoi usare lettere o numeri): ").strip().lower()
                if self.is_valid_key(key):
                    keys.append(key)
                    break
                else:
                    print("Tasto non valido, inserisci una lettera o un numero.")

        self.keys_to_press = keys
        print(f"Tasti selezionati: {', '.join(self.keys_to_press)}")

    def is_valid_key(self, key):
        """Controlla se un tasto è valido (alfanumerico o tasti speciali)."""
        return len(key) == 1 and (key.isalnum() or key in ('shift', 'ctrl', 'alt'))

    def start_pressing_keys(self):
        """Inizia a premere i tasti selezionati."""
        for key in self.keys_to_press:
            thread = KeyPressThread(key, self.controller)
            self.threads[key] = thread
            thread.start()
        print(f"I tasti {', '.join(self.keys_to_press)} sono ora tenuti premuti!")

    def stop_pressing_keys(self):
        """Ferma la pressione dei tasti e rilascia tutte le chiavi."""
        for key, thread in self.threads.items():
            thread.stop()
        self.threads.clear()
        print("Tutti i tasti sono stati rilasciati.")

    def monitor_f5(self):
        """Monitora il tasto F5 per avviare o fermare la pressione dei tasti."""
        while True:
            if keyboard.is_pressed('f5') and not self.is_running:
                self.is_running = True
                self.start_pressing_keys()
                self.wait_for_f5_release()  # Attendi fino a che F5 non viene rilasciato
            elif keyboard.is_pressed('f5') and self.is_running:
                self.is_running = False
                self.stop_pressing_keys()
                self.wait_for_f5_release()  # Attendi fino a che F5 non viene rilasciato

    def wait_for_f5_release(self):
        """Evita che il tasto F5 venga rilevato ripetutamente."""
        while keyboard.is_pressed('f5'):
            time.sleep(0.1)

    def start(self):
        """Avvia il programma, chiedi i tasti e monitorizza F5."""
        print("Benvenuto nell'autoclicker!")
        self.choose_keys()

        print("Premi F5 per iniziare a tenere premuti i tasti.")
        # Avvia il monitoraggio del tasto F5 in un thread separato
        threading.Thread(target=self.monitor_f5, daemon=True).start()

        try:
            while True:
                time.sleep(0.1)  # Mantieni il programma in esecuzione senza consumare troppe risorse
        except KeyboardInterrupt:
            print("\nProgramma interrotto.")

if __name__ == "__main__":
    AutoClicker().start()
